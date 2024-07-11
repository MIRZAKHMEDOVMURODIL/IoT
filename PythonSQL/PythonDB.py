#!/usr/bin/env python
# coding: utf-8

# In[1]:


import time
import pandas as pd
import ibm_db
import logging
from sqlalchemy import create_engine
import os
import glob
import json
from datetime import datetime
import datetime as dt 
import numpy as np
from logging.handlers import RotatingFileHandler


# ハンドラを設定
handler = RotatingFileHandler(filename='logfile.log', maxBytes=1000000, backupCount=5)

# ログメッセージのフォーマットを指定
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# ロギングの基本設定を行い、ハンドラを追加
logging.basicConfig(level=logging.INFO, handlers=[handler])

#########################################################################################################################################################################


try:  
    # 'config.json' ファイルを開いて、設定データを読み込む
    with open('config.json') as config_file:
        config_data = json.load(config_file)

    # 設定データから必要な情報を取得
    database = config_data.get("database")
    hostname = config_data.get("hostname")
    port = config_data.get("port")
    protocol = config_data.get("protocol")
    uid = config_data.get("uid")
    pwd = config_data.get("pwd")
    global directory
    directory = config_data.get("directory")
    
    # 接続文字列を構築  
    conn_str = f"DATABASE={database};HOSTNAME={hostname};PORT={port};PROTOCOL={protocol};UID={uid};PWD={pwd};"

    # IBM Db2 データベースに接続
    conn = ibm_db.connect(conn_str, "", "")

    # 接続が成功したかどうかを確認
    if conn:
        print("Connected to the database\n")
        logging.info("Connected to the database\n")
    else:
        print("Failed to connect to the database\n")
        logging.error("Failed to connect to the database\n")
   
except Exception as e:
    logging.error(f"An unknown error occurred: {str(e)}")


##########################################################################################################################################################################

# 1) 各LOCATIONごとに最新のデータをINSERT/UPDATE  

def function_1():
    
    print("Function_1: Proccess started") 
    logging.info("Function_1: Proccess started")
          
    try:
        start_time = time.time()
        
        #1.最新フォルダ内のすべてのCSVファイルのパスを収集する。
        file_pattern = '20*'
        files = glob.glob(os.path.join(directory, file_pattern))
        files.sort()
        
        
        #2. 最新のCSVファイルを探す。
        if files:
            # 最新のフォルダのパスを取得し、その中のCSVファイルを抽出
            folder_path = files[-1]
            csv_files = glob.glob(os.path.join(folder_path, '*.csv'))
        
            if csv_files:
                 # 最新のCSVファイルを取得し、データフレームに読み込む
                latest_csv_file = max(csv_files, key=os.path.getmtime)
                df = pd.read_csv(latest_csv_file, encoding='cp932', dtype=object)
                
                
        #3. Locationカラムから最新の値を変数に入れる。
                
                # 日時型に変換
                df['Timestamp'] = pd.to_datetime(df['Timestamp'])
                
                # ユニークなロケーションを取得
                unique_locations = df['Location'].unique()
                
                # 最新のデータを格納するためのデータフレームを作成
                latest_data = pd.DataFrame()
                df_concat = []
                
                # ユニークなロケーションごとに最新のデータを選択し、データフレームに追加
                for location in unique_locations:
                    latest_location = df[df['Location'] == location].nlargest(1, 'Timestamp')
                    df_concat.append(latest_location)
                    
                # 各ロケーションの最新データを結合   
                latest_data = pd.concat(df_concat, ignore_index=True)

                # ログとコンソールに処理結果を出力
                print("Latest CSV file:", latest_csv_file)
                logging.info("Latest CSV file: %s", latest_csv_file)
                logging.info("Processed data for %d locations", len(unique_locations))
                
            else:
                print("No CSV files found in the latest folder.")
                logging.warning("No CSV files found in the latest folder.")
        else:
            print("No folders found.")
            logging.warning("No folders found.")
           
         
        # 4. データがあればUPDATE, データがなければINSERTする。
        merge_query = """
        MERGE INTO LIQUID_PARTICLE_LAST AS target
        USING (SELECT ? AS LOCATION, ? AS TS_DT, ? AS VALUE_1_0, ? AS VALUE_3_0, ? AS VALUE_5_0, ? AS VALUE_10_0, ? AS VALUE_15_0, ? AS VALUE_20_0, ? AS VALUE_25_0, ? AS VALUE_50_0 FROM SYSIBM.SYSDUMMY1) AS source
        ON target.LOCATION = source.LOCATION
        WHEN MATCHED THEN
            UPDATE SET target.TS_DT = source.TS_DT, 
                       target.VALUE_1_0 = source.VALUE_1_0, 
                       target.VALUE_3_0 = source.VALUE_3_0, 
                       target.VALUE_5_0 = source.VALUE_5_0, 
                       target.VALUE_10_0 = source.VALUE_10_0, 
                       target.VALUE_15_0 = source.VALUE_15_0, 
                       target.VALUE_20_0 = source.VALUE_20_0, 
                       target.VALUE_25_0 = source.VALUE_25_0, 
                       target.VALUE_50_0 = source.VALUE_50_0
        WHEN NOT MATCHED THEN
            INSERT (LOCATION, TS_DT, VALUE_1_0, VALUE_3_0, VALUE_5_0, VALUE_10_0, VALUE_15_0, VALUE_20_0, VALUE_25_0, VALUE_50_0)
            VALUES (source.LOCATION, source.TS_DT, source.VALUE_1_0, source.VALUE_3_0, source.VALUE_5_0, source.VALUE_10_0, source.VALUE_15_0, source.VALUE_20_0, source.VALUE_25_0, source.VALUE_50_0);
        """
        
        stmt = ibm_db.prepare(conn, merge_query)

        # 最新データをループしてマージ
        for index, row in latest_data.iterrows():
            # 行から必要なデータを抽出
            location = row['Location']
            timestamp = row['Timestamp']
            c1 = row['1.0μｍ']
            c3 = row['3.0μｍ']
            c5 = row['5.0μｍ']
            c10 = row['10.0μｍ']
            c15 = row['15.0μｍ']
            c20 = row['20.0μｍ']
            c25 = row['25.0μｍ']
            c50 = row['50.0μｍ']

            # データをマージする
            if ibm_db.execute(stmt, (location, timestamp, c1, c3, c5, c10, c15, c20, c25, c50)):
                print(f"Row {index + 1} merged successfully")
                logging.info(f"Row {index + 1} merged successfully")
            else:
                print(f"Error merging row {index + 1}: {ibm_db.stmt_errormsg()}")



        # 処理時間の計測と表示
        end_time = time.time()
        elapsed_time = end_time - start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        print(f"Time spent: {minutes} minutes and {seconds} seconds")
        logging.info(f"Time spent: {minutes} minutes and {seconds} seconds")
    except Exception as e:   
        logging.error(f"An unknown error occurred: {str(e)}")

    print("Function_1: Completed\n") 
    logging.info("Function_1: Completed\n") 
#####################################################################################################################################
        
# 2) JSON記録に記載された日より以降のデータをCSVファイルごとにINSERTする

        
    #1.　JSON 記録から最後INSERTされた行の時間を取得します。
    #2.　最新のフォルダから,全てのCSVファイルのパスを取得します。
    #3.　JSONに記載された最後の行以降のデータをまとめる。  


def function_2():
    print("Function_2: Proccess started") 
    logging.info("Function_2: Proccess started")
    try:
        start_time = time.time()
        json_file_path = 'insertion_time.json'
        
        # JSONファイルが存在する場合   
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as json_file:
                data = json.load(json_file)
                if 'insertion_time' in data and data['insertion_time'] and not pd.isna(data['insertion_time'])  :
                    
                    # 'insertion_time'が存在し、nanでない場合
                    insertion_time_raw = str(data['insertion_time'])
                    inserted_time = dt.datetime.strptime(insertion_time_raw, '%Y-%m-%d %H:%M:%S')
                    inserted_day = inserted_time.strftime('%Y%m%d')
                    time_to_compare = insertion_time_raw
                    print(f"Last Insertion time: {time_to_compare}")
                    
                    # CSVファイルの検索と選択
                    # directory = r"C:\Users\00220401626\Desktop\FMS\CsvData"
                    file_pattern = '20*'
                    files = glob.glob(os.path.join(directory, file_pattern))
                    files.sort()
                    folder_path = files[-1]
                    csv_files = glob.glob(os.path.join(folder_path, '*.csv'))
                    selected_csv_files = [file for file in csv_files if int(file[-12:-4]) >= int(inserted_day)]
                
                else:
                     # 'insertion_time'がnanまたは見つからない場合
                    print("Error: 'insertion_time' is 'nan' or not found in the JSON file.\nAll CSV files below are going to be inserted into the database.")
                    logging.error("Error: 'insertion_time' is 'nan' or not found in the JSON file. \nAll CSV files below are going to be inserted into the database.")
                    # directory = r"C:\Users\00220401626\Desktop\FMS\CsvData"
                    file_pattern = '20*'
                    files = glob.glob(os.path.join(directory, file_pattern))
                    files.sort()
                    folder_path = files[-1]
                    selected_csv_files = glob.glob(os.path.join(folder_path, '*.csv'))
                    time_to_compare = False
             
        else:
            # JSONファイルが存在しない場合
            print("JSON file does not exist. \nAll CSV files below are going to be inserted into the database.")
            logging.info("JSON file does not exist. All CSV files below are going to be inserted into the database.")
            # directory = r"C:\Users\00220401626\Desktop\FMS\CsvData"
            file_pattern = '20*'
            files = glob.glob(os.path.join(directory, file_pattern))
            files.sort()
            folder_path = files[-1]
            selected_csv_files = glob.glob(os.path.join(folder_path, '*.csv'))
            time_to_compare = False
            
        # 選択されたCSVファイルの表示とログ出力
        for i in selected_csv_files:
            print(i)
            logging.info(i)
            
        print("CSV files are inserting.......")
        logging.info("CSV files are inserting.......")
         

        
        
    # 4.JSONに記載された最後の行より以降のデータのcsvを１つずつINSERTする
        if selected_csv_files:
 
            # 選択されたCSVファイルごとに処理
            for i in selected_csv_files:
                 # CSVファイルをデータフレームとして読み込み  
         
               
                df = pd.read_csv(fr"{i}", encoding='cp932', dtype= object)
                
                # タイムスタンプの書式を整える
                df['Timestamp'] = df['Timestamp'].str.replace('/', '-', regex=False)

                # JSONファイルが存在し、挿入時刻が指定されている場合
                if os.path.exists(json_file_path) and time_to_compare:

                    # 指定時刻以降のデータを抽出
                    a = df[df['Timestamp'] >  time_to_compare]
                    data = tuple(tuple(row) for row in a.values )

                    # データを文字列に変換してINSERTクエリを構築
                    b = ""
                    for row in data:
                        b += str(row) +","
                    b = b[:-1]
                    
                    insert_query = f"INSERT INTO LIQUID_PARTICLE (Location, TS_DT, VALUE_1_0, VALUE_3_0, VALUE_5_0, VALUE_10_0, VALUE_15_0, VALUE_20_0, VALUE_25_0, VALUE_50_0) VALUES {b}"
                    stmt = ibm_db.prepare(conn, insert_query)
                    
                    try:
                        # データをデータベースに挿入
                        if ibm_db.execute(stmt, b):
                            print(f"{i} : Inserted successfully") 
                            logging.info(f"{i} : Inserted successfully")
                    except:
                        print(f"({i}) is already updated")
                        logging.info(f"{i} : is already updated")


                        
                    #5.時間を JSON ファイルに保存する   
                    insertion_time = a['Timestamp'].max()
                    if not pd.isna(insertion_time):
                        json_data = {'insertion_time': insertion_time}
                        with open('insertion_time.json', 'w') as json_file:
                            json.dump(json_data, json_file, indent=4)
                            
                else:
                    
                    data = tuple(tuple(row) for row in df.values )

                    # データを文字列に変換してINSERTクエリを構築
                    b = ""
                    for row in data:
                        b += str(row) +","
                    b = b[:-1]
                    
                    insert_query = f"INSERT INTO LIQUID_PARTICLE (Location, TS_DT, VALUE_1_0, VALUE_3_0, VALUE_5_0, VALUE_10_0, VALUE_15_0, VALUE_20_0, VALUE_25_0, VALUE_50_0) VALUES {b}"
                    stmt = ibm_db.prepare(conn, insert_query)

                    try:
                         # データをデータベースに挿入
                        if ibm_db.execute(stmt, b):
                            print(f"{i} : Inserted successfully") 
                            logging.info(f"{i} : Inserted successfully")
                    except:
                        print(f"({i}) is already updated")
                        logging.info(f"{i} : is already updated")
                        
                
                    #5.時間を JSON ファイルに保存する          
                
                    insertion_time = df['Timestamp'].max()
                    if not pd.isna(insertion_time):
                        json_data = {'insertion_time': insertion_time}
                        with open('insertion_time.json', 'w') as json_file:
                            json.dump(json_data, json_file, indent=4)
    
                        
            print('All CSV files are inserted')
            logging.info('All CSV files are inserted')
            
        elif not selected_csv_files:
            print("Database is already updated")
            logging.info("Database is already updated")
            
        # 処理時間の計測と表示
        end_time = time.time()
        elapsed_time = end_time - start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        print(f"Time spent: {minutes} minutes and {seconds} seconds")
        logging.info(f"Time spent: {minutes} minutes and {seconds} seconds")
        
    except Exception as e:   
        logging.error(f"An unknown error occurred: {str(e)}")
  
    print("Function_2: Completed\n") 
    logging.info("Function_2: Completed\n")
          
if __name__ == "__main__":
    
    # データベースに接続できている場合
    if conn:
        function_1()           # Function_1の実行
        function_2()           # Function_2の実行


# In[ ]:




