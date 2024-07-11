#########################################################
# Update:2023/1/19
# program Name:db2_QC.py
# Process:IOT_DATAの装置別に作成された紐づけデータテーブル(ID_PROCESS)へ紐づけデータを保存（ファイルフォーマットは全設備共通(三菱タッチパネルの標準出力ロギングcsv))
# args: 1=json設定ファイルのファイルアドレス(参照ファイルの設定値を読み込んで登録値を設定)
#########################################################

import sys
# import glob
import json
# from pathlib import Path
import logging
import logging.handlers
import pandas as pd
import ibm_db
import datetime
import os
import platform
# import csv
import re
import ntpath
import posixpath
# import shutil

#定数
max_sqlstr_byte = 2097152 #SQL構文の最大バイト長(DB2の場合)、INSERT等の構文はこのバイト長を超える文字列だとNGになる

# 改行コード
linesep = os.linesep
if platform.system() == 'Windows':
    linesep = '\n' #何故かWindowsのCRLFは上手くcsv改行ができない

# アドレスの区切り文字設定
def path_join(*args, os = None):
    os = os if os else platform.system()
    if os == 'Windows':
        return ntpath.join(*args)
    else:
        return posixpath.join(*args)

# JSONファイル読込（コメント付きも対応）
def JSON_load(path_copylog):
    json_obj = None #空データ作成
    try:
        with open(path_copylog, 'r', encoding='utf-8') as f:      # 開く
            text = f.read()                                   # 文字列を取得
        re_text = re.sub(r'/\*[\s\S]*?\*/|//.*', '', text)    # コメントを削除
        json_obj = json.loads(re_text)  
    except Exception as e:
        logger.error("<<error>> Error reading json file")
        logger.error(str(e))
        json_obj=None
    finally:
        return(json_obj)
    
import subprocess
def Get_IP(Type):
    IP = ""
    try:
        command = [path_join(root_dir,"ipget.sh"),str(Type)]
        ret = subprocess.run(command, stdout=subprocess.PIPE)
        IP = (ret.stdout).decode('utf-8')
    except Exception as e:
        logger.error("<<error>> can't get IP Address")
        logger.error(str(e))
    finally:
        return IP
    
rst = 0 #処理結果(0は処理正常)
dt_st = datetime.datetime.now()
root_dir = path_join("/IoT", "bin") #大本のフォルダを指定

##################################       logファイルの設定　　     #######################################
dir_log = os.path.dirname(__file__)
os.makedirs(dir_log,exist_ok=True)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO) #INFO以上は出力
log_Path = path_join(dir_log, "hist.log")
file_handler = logging.FileHandler(log_Path)
file_handler.setLevel(logging.INFO) #INFO以上は出力
file_handler_format = logging.Formatter('%(asctime)s : %(levelname)s - %(message)s')
file_handler.setFormatter(file_handler_format)
logger.addHandler(file_handler)

logger.info("==========================================================================================================")
logger.info("Program: " + __file__)

logger.info('Proc Start: ' + dt_st.strftime('%Y/%m/%d %H:%M:%S.%f'))
logger.info('----- Python Version -------------------')
logger.info(sys.version)
#############################################################################################################

##################################       設定ファイルの読み込み　　     #######################################
files_ReadErr = [] #過去に読み取りNGで処理されたファイルリスト

try:
    args = sys.argv
    j_data = JSON_load(args[1])
    if j_data is None:
        rst = 1 #処理異常

    IP_Local = Get_IP(1) # 設定されている10系のIPアドレスを取得

except Exception as e:
    logger.exception(str(e))
    rst = 1

if rst == 0:
    try:
        logger.info("************ 実行履歴の書き込み START *******************")

        # 対象スキーマ、対象テーブルを取得
        target_schema = j_data["DB_IOT"]["schema"] #スキーマ名(ドットまで記載、指定なければ空文字列)
        table_hist_latest = j_data["DB_IOT"]["HIST_LATEST"] #対象テーブル(最新履歴)
        table_hist_registered = j_data["DB_IOT"]["HIST_REGISTERED"] #対象テーブル(実行履歴)

        if (table_hist_latest is None) or (table_hist_registered is None):
            logger.error("設定ファイル 登録NG : table is null")
            rst = 1 #処理異常
        else:
            # テーブル名を設定情報を元に作成
            if target_schema is not None:
                table_hist_latest = target_schema + '.' + table_hist_latest # Merge対象のテーブル名
                table_hist_registered = target_schema + '.' + table_hist_registered # Merge対象のテーブル名

    except Exception as e:
        logger.exception(str(e))
        rst = 1

#############################################################################################################

files_NG = [] #INSERTに失敗したファイルリスト
files_OK = [] #INSERTに成功したファイルリスト
list_sql = [] #実行するSQL構文と一括登録するレコード数、ファイルアドレスのリスト(0:SQL構文、1:登録レコード数, 2:ファイルアドレス)

# 一時テーブルに登録するデータのINSERT構文をcsvファイルを元に作成
if rst == 0:

    dt_st_process = datetime.datetime.now() #処理開始時間(デバッグ用)
    logger.info("-----   データファイル参照   -----")

    #INSERT対象の列名(基本列名だけ記載、追加分は下記の条件で設定)
    column_hist_latest = ['IP_ADDRESS', 'PROC_TYPE', 'PRGM_NAME', 'EQP_ID', 'EQP_NAME', 'UNIT_NUM', 'UNIT_NAME', 'LOG_NUM', 'DATA_TYPE', 'REGISTERED_TABLE', 'REGISTERED_DT','MEASURED_DT']
    column_hist_registered = ['IP_ADDRESS', 'PROC_TYPE', 'PRGM_NAME', 'EQP_ID', 'EQP_NAME', 'UNIT_NUM', 'UNIT_NAME', 'LOG_NUM', 'DATA_TYPE', 'REGISTERED_TABLE', 'REGISTERED_DT', 'RESULT', 'CONTENTS','MEASURED_DT']

    path_hist_registered = path_join(root_dir, "hist_registered.log")
    try:
        ################################# データに"装置ID","ユニット名"等追加・単位の修正######################################
        # csvデータをdataframeで取得
        if os.path.isfile(path_hist_registered):
            df_csv = pd.read_csv(path_hist_registered, header=None, dtype=object)              

            # 取得したデータの行数が0の場合は飛ばして次のファイルを参照
            if len(df_csv) == 0:
                logger.error("Pass: data is nothing") 
                logger.error("filepath:" + path_hist_registered)
                rst = -1
        else:
            logger.error("Pass: data is nothing") 
            logger.error("filepath:" + path_hist_registered)
            rst = -1

    except Exception as e:
        logger.exception(str(e))
        rst = 2 # データ取得NG

        
        # ~~~~~~~~~~~~~~ここからcsvデータに合わせた処理を記載~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if rst == 0:
    try:
        # IPアドレスを先頭に追加
        df_insert = pd.DataFrame({})

        # 列名を登録カラム名に合わせて変更
        list_column = []
        for colno in range(1, len(column_hist_registered)):
            list_column.append([str(colno-1), column_hist_registered[colno]])
            df_insert[column_hist_registered[colno]] = df_csv[colno-1]
        df_insert['IP_ADDRESS'] = IP_Local

        # 列順を変更(sql_insertに合わせる)
        df_insert = df_insert.reindex(columns = column_hist_registered)

       # 全データのデータ型を再度文字列に変更
        df_insert = df_insert.astype(str)

        # 欠損値(NaN)を文字列「NULL」に置換(念のために設定)
        df_insert['MEASURED_DT'] = df_insert['MEASURED_DT'].replace('nan' ,"NULL")
        df_insert = df_insert.replace('nan' ,"")

        cnt_insert = 0 #Insertレコード数(一括処理するので、登録行数をLogに保存)

        if len(df_insert[(df_insert["RESULT"] == '0')]) > 0:
            
            df_insert_latest = df_insert[(df_insert["RESULT"] == '0')]

            # 最終行(登録日時が最新のデータ)を残して削除
            df_insert_latest = df_insert_latest.drop_duplicates(subset=['IP_ADDRESS', 'PROC_TYPE', 'EQP_ID', 'UNIT_NUM', 'LOG_NUM', 'DATA_TYPE'], keep='last')

            for column_name in column_hist_latest:
                df_cat = "'" + df_insert_latest[column_name].astype(str) + "'" #一旦クオーテーションを付けたデータを作成
                df_cat = df_cat.replace("'NULL'" ,'NULL') #NULLだけクオーテーション無しに設定(クオーテーションありだと文字列として登録されるため)
                if column_name == column_hist_latest[0]:
                    df_insert_latest['Values'] = df_cat
                else:
                    df_insert_latest['Values'] = df_insert_latest['Values'].str.cat(df_cat, sep=',') #各列をカンマ区切りで結合

            list_insert = '(' + df_insert_latest['Values'] + ')'

            # INSERTの基本構文を作成(列順はDataframe準拠。処理は後述の登録テーブルへのMERGEと同等、但し登録先は一時テーブル、登録データはデータファイルのValuesを結合したものを使用)           
            # 登録先を指定(一時テーブルが対象)
            sql_insert_top = "MERGE INTO " + table_hist_latest + " AS TGT USING (VALUES "
            
            # データ元を指定(データファイルのValuesを結合したものを疑似テーブルとして使用し、カラム名を設定)
            sql_insert_buttom = ") AS INSERTDATA (" + ','.join([datarow for datarow in column_hist_latest]) + ")"

            sql_insert_under = " ON ("\
                        "TGT.IP_ADDRESS = INSERTDATA.IP_ADDRESS"\
                        " AND TGT.PROC_TYPE = INSERTDATA.PROC_TYPE"\
                        " AND TGT.EQP_ID = INSERTDATA.EQP_ID"\
                        " AND TGT.UNIT_NUM = INSERTDATA.UNIT_NUM"\
                        " AND TGT.LOG_NUM = INSERTDATA.LOG_NUM"\
                        " AND TGT.DATA_TYPE = INSERTDATA.DATA_TYPE"\
                    ") "\
                    "WHEN NOT MATCHED THEN"

            sql_insert_under += ' INSERT (' + ','.join([datarow for datarow in column_hist_latest]) + ')'
            sql_insert_under += ' VALUES (INSERTDATA.' + ',INSERTDATA.'.join([datarow for datarow in column_hist_latest]) + ')' 

            sql_insert_under += " WHEN MATCHED THEN"\
                                " UPDATE SET TGT.REGISTERED_DT = INSERTDATA.REGISTERED_DT"\
                                ", TGT.PRGM_NAME = INSERTDATA.PRGM_NAME"\
                                ", TGT.EQP_NAME = INSERTDATA.EQP_NAME"\
                                ", TGT.UNIT_NAME = INSERTDATA.UNIT_NAME"\
                                ", TGT.REGISTERED_TABLE = INSERTDATA.REGISTERED_TABLE"\
                                ", TGT.MEASURED_DT = INSERTDATA.MEASURED_DT"
            sql_insert_under += ";"
            #############################################################################################################

            ###############################   1行ずつ処理、SQL構文を作成し保存　　##########################################
            sqlcnt = 0
            sql_insert_value = ""
            
            for str_value in list_insert:

                flg_append = True #list_sqlへ追加するかの判定(Trueで追加実行)

                # INSERT構文を作成(SQL構文をバイト数に換算した場合の最大制限があるので、それ以下まで行ごとにValueを追記する)
                if len((sql_insert_top + sql_insert_value + "," + str_value + "," + str_value + sql_insert_buttom + sql_insert_under).encode('utf-8')) >= max_sqlstr_byte:
                    #1. 文字列のバイト制限ギリギリになったらInsert実行(次回のValue追加で制限超えるのを疑似的に判定するため、同じValueを重ねて判定)
                    sql_insert = sql_insert_top + sql_insert_value + "," + str_value + sql_insert_buttom + sql_insert_under
                    cnt_insert += 1 # 登録レコード数を+1
                    list_sql.append([sql_insert, cnt_insert]) #SQLリストにSQL構文とレコード数、ファイルアドレスを登録
                    logger.debug("sql_cnt:" + str(cnt_insert) + ", sql_insert:" + sql_insert)

                    sql_insert_value = "" #Value文字列をリセット
                    cnt_insert = 0 #レコード数をリセット
                    flg_append = False #登録しない(この処理を最後にループを抜けた場合はリスト登録は行われない)
                    sqlcnt += 1 #作成構文数を+1

                else:
                    #2. バイト制限まで余裕がある場合は、Valueだけ結合
                    if sql_insert_value == "":
                        sql_insert_value = str_value
                    else:
                        sql_insert_value += "," + str_value
                    cnt_insert += 1 # 登録レコード数を+1

            if flg_append == True:
                sql_insert = sql_insert_top + sql_insert_value + sql_insert_buttom + sql_insert_under
                list_sql.append([sql_insert, cnt_insert]) #SQLリストにSQL構文とレコード数、ファイルアドレスを登録
                logger.debug("sql_cnt:" + str(cnt_insert) + ", sql_insert:" + sql_insert)
                sqlcnt += 1 #作成構文数を+1

            logger.debug("sqlcnt:" + str(sqlcnt))

        # エラー履歴のデータを抽出
        if len(df_insert[(df_insert["RESULT"] != '0')]) > 0:

            df_insert_registered = df_insert[(df_insert["RESULT"] != '0')]

            for column_name in column_hist_registered:
                df_cat = "'" + df_insert_registered[column_name].astype(str) + "'" #一旦クオーテーションを付けたデータを作成
                df_cat = df_cat.replace("'NULL'" ,'NULL') #NULLだけクオーテーション無しに設定(クオーテーションありだと文字列として登録されるため)
                if column_name == column_hist_registered[0]:
                    df_insert_registered['Values'] = df_cat
                else:
                    df_insert_registered['Values'] = df_insert_registered['Values'].str.cat(df_cat, sep=',') #各列をカンマ区切りで結合

            list_insert = '(' + df_insert_registered['Values'] + ')'

            # INSERTの基本構文を作成(列順はDataframe準拠。処理は後述の登録テーブルへのMERGEと同等、但し登録先は一時テーブル、登録データはデータファイルのValuesを結合したものを使用)           
            # 登録先を指定(一時テーブルが対象)
            sql_insert_top = "MERGE INTO " + table_hist_registered + " AS TGT USING (VALUES "
            
            # データ元を指定(データファイルのValuesを結合したものを疑似テーブルとして使用し、カラム名を設定)
            sql_insert_buttom = ") AS INSERTDATA (" + ','.join([datarow for datarow in column_hist_registered]) + ")"

            sql_insert_under = " ON ("\
                        "TGT.IP_ADDRESS = INSERTDATA.IP_ADDRESS"\
                        " AND TGT.PROC_TYPE = INSERTDATA.PROC_TYPE"\
                        " AND TGT.EQP_ID = INSERTDATA.EQP_ID"\
                        " AND TGT.UNIT_NUM = INSERTDATA.UNIT_NUM"\
                        " AND TGT.LOG_NUM = INSERTDATA.LOG_NUM"\
                        " AND TGT.DATA_TYPE = INSERTDATA.DATA_TYPE"\
                        " AND TGT.REGISTERED_DT = INSERTDATA.REGISTERED_DT"\
                    ") "\
                    "WHEN NOT MATCHED THEN"

            sql_insert_under += ' INSERT (' + ','.join([datarow for datarow in column_hist_registered]) + ')'
            sql_insert_under += ' VALUES (INSERTDATA.' + ',INSERTDATA.'.join([datarow for datarow in column_hist_registered]) + ')' 
            sql_insert_under += ";"
            #############################################################################################################

            ###############################   1行ずつ処理、SQL構文を作成し保存　　##########################################
            sqlcnt = 0
            sql_insert_value = ""
            for str_value in list_insert:

                flg_append = True #list_sqlへ追加するかの判定(Trueで追加実行)

                # INSERT構文を作成(SQL構文をバイト数に換算した場合の最大制限があるので、それ以下まで行ごとにValueを追記する)
                if len((sql_insert_top + sql_insert_value + "," + str_value + "," + str_value + sql_insert_buttom + sql_insert_under).encode('utf-8')) >= max_sqlstr_byte:
                    #1. 文字列のバイト制限ギリギリになったらInsert実行(次回のValue追加で制限超えるのを疑似的に判定するため、同じValueを重ねて判定)
                    sql_insert = sql_insert_top + sql_insert_value + "," + str_value + sql_insert_buttom + sql_insert_under
                    cnt_insert += 1 # 登録レコード数を+1
                    list_sql.append([sql_insert, cnt_insert]) #SQLリストにSQL構文とレコード数、ファイルアドレスを登録
                    logger.debug("sql_cnt:" + str(cnt_insert) + ", sql_insert:" + sql_insert)

                    sql_insert_value = "" #Value文字列をリセット
                    cnt_insert = 0 #レコード数をリセット
                    flg_append = False #登録しない(この処理を最後にループを抜けた場合はリスト登録は行われない)
                    sqlcnt += 1 #作成構文数を+1

                else:
                    #2. バイト制限まで余裕がある場合は、Valueだけ結合
                    if sql_insert_value == "":
                        sql_insert_value = str_value
                    else:
                        sql_insert_value += "," + str_value
                    cnt_insert += 1 # 登録レコード数を+1

            if flg_append == True:
                sql_insert = sql_insert_top + sql_insert_value + sql_insert_buttom + sql_insert_under
                list_sql.append([sql_insert, cnt_insert]) #SQLリストにSQL構文とレコード数、ファイルアドレスを登録
                logger.debug("sql_cnt:" + str(cnt_insert) + ", sql_insert:" + sql_insert)
                sqlcnt += 1 #作成構文数を+1

            logger.debug("sqlcnt:" + str(sqlcnt))

        ##############################################################################################################

    except Exception as e:
        logger.exception(str(e))
        rst = 3 #SQL処理NG

    # 取得したデータの行数が0の場合は飛ばして次のファイルを参照
    # logger.info(list_sql)
    if len(list_sql) == 0:
        logger.error("Pass: data is nothing") 
        rst = -1

    #処理時間(デバッグ用)
    dt_en_process = datetime.datetime.now()
    dt_diff_process = dt_en_process - dt_st_process
    logger.debug('Processed Time[s]: %d.%06d' % (dt_diff_process.seconds, dt_diff_process.microseconds))

#################################              DB接続                #######################################
if rst == 0:
    
    dt_st_process = datetime.datetime.now() #処理開始時間(デバッグ用)

    logger.info("-----   DB接続実行   -----")
    try:
        server = j_data["DB_IOT"]["server"]
        database = j_data["DB_IOT"]["database"]
        username = j_data["DB_IOT"]["username"]
        password = j_data["DB_IOT"]["pw"]
        conn = ibm_db.connect("DATABASE=" + database + ";HOSTNAME=" + server + ";PORT=50000;PROTOCOL=TCPIP;UID=" + username + ";PWD=" + password + ";", "", "")

        #logger.debug("************"+j_data["unit_num"]+"  "+j_data["unit_name"]+" ALMの書き込み START*******************")
        logger.debug('OK')

    except Exception as e:
        logger.error('NG')
        logger.exception(str(e))
        rst = 2 #DB接続NG

    #処理時間(デバッグ用)
    dt_en_process = datetime.datetime.now()
    dt_diff_process = dt_en_process - dt_st_process
    logger.debug('Processed Time[s]: %d.%06d' % (dt_diff_process.seconds, dt_diff_process.microseconds))

##########################################################################################################

insertcnt = 0 #TEMP TABLEへINSERT出来たレコード数
if rst == 0:
    if len(list_sql) > 0: #実行するSQL構文がある場合
        
        ###############################   SQL構文を一時テーブルに処理実行　　##########################################

        dt_st_process = datetime.datetime.now() #処理開始時間(デバッグ用)

        logger.info("-----   INSERT処理実行   -----")
        for sql_insert , cnt_insert in list_sql:

            # INSERT失敗したファイルのSQL構文でなければINSERT実行
            logger.debug("insert cnt:" + str(cnt_insert))
            logger.debug("insert sql:" + sql_insert[:200] + "……")
            #該当データがない場合(cnt_insert=0)は処理を飛ばす
            if cnt_insert == 0: 
                logger.debug("Pass: insert cnt = 0")  
                continue
            
            #登録するValueが取得出来ている場合は処理継続
            try:
                dt_st_sql = datetime.datetime.now() #SQL開始時間(デバッグ用)
                rstset = ibm_db.exec_immediate(conn, sql_insert) #Insert実行
                dt_en_sql = datetime.datetime.now() #SQL終了時間(デバッグ用)
                if rstset is False:
                    logger.error("NG")
                    dt_diff_sql = dt_en_sql - dt_st_sql
                    logger.debug('SQL Time[s]: %d.%06d' % (dt_diff_sql.seconds, dt_diff_sql.microseconds))
                    
                else:
                    logger.debug("OK")
                    dt_diff_sql = dt_en_sql - dt_st_sql
                    logger.debug('SQL Time[s]: %d.%06d' % (dt_diff_sql.seconds, dt_diff_sql.microseconds))

            except Exception as e:
                logger.error("NG")
                logger.exception(str(e))

        #処理時間(デバッグ用)
        dt_en_process = datetime.datetime.now()
        dt_diff_process = dt_en_process - dt_st_process
        logger.debug('Processed Time[s]: %d.%06d' % (dt_diff_process.seconds, dt_diff_process.microseconds))

    else:
        logger.exception("登録SQL数:0")
        rst = 3 #一時テーブル作成NG
        ##############################################################################################################

    ##########################                DB2接続終了                 ########################################
    try:
        logger.info("-----   DB接続終了   -----")
        ibm_db.close(conn) #接続終了
        logger.debug("OK")
    except Exception as e:
        logger.error("NG")
        logger.exception(str(e))

    ##############################################################################################################

if rst == 0:
    os.remove(path_hist_registered) #正常登録の場合はファイル削除

# End
dt_en = datetime.datetime.now()
logger.info('Proc End: ' + dt_en.strftime('%Y/%m/%d %H:%M:%S.%f'))
dt_diff = dt_en - dt_st
logger.info('Elapsed Time[s]: %d.%06d' % (dt_diff.seconds, dt_diff.microseconds))

logger.info("==========================================================================================================")