from re import I
import sys
import glob
import json
from pathlib import Path
import logging
import logging.handlers
import pandas as pd
import ibm_db
import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("/IoT/bin/DB/debug.log")
file_handler.setLevel(logging.DEBUG)
file_handler_format = logging.Formatter('%(asctime)s : %(levelname)s - %(message)s')
file_handler.setFormatter(file_handler_format)
file_handler.setFormatter(file_handler_format)
logger.addHandler(file_handler)


##################################       設定ファイルの読み込み　　     #######################################
args = sys.argv
fd = open(args[1], mode='r')
j_data = json.load(fd)
fd.close()
logger.debug("***************" + j_data["unit_num"]+"  "+j_data["unit_name"]+" TSの書き込みStart*****************")
#############################################################################################################


##################################              DB接続                #######################################
server = j_data["server"]
database = j_data["database"]
username = j_data["username"]
password = j_data["pw"]
try:
    conn = ibm_db.connect("DATABASE=" + database + ";HOSTNAME=" + server + ";PORT=50000;PROTOCOL=TCPIP;UID=" + username + ";PWD=" + password + ";", "", "")
    logger.debug('DB接続OK')
except:
    logger.exception("DB接続失敗")
##########################################################################################################


################################# データに"装置ID","ユニット名"等追加・単位の修正######################################
#csvファイル読み込み  
files = glob.glob(j_data["dst_dir"])
#ファイルの数だけループ処理
for f in files:
    try:
        df = pd.read_csv(f,skiprows =9, header=0,encoding="cp932", dtype=object)
        df = df.drop(index=df.index[[0,1,2]])
        column_name_list = df.columns.values
        # 単位修正する数でループ
        for num in range(len(j_data["calc_name"])):
            # 列数でループ
            for column_num in range(len(column_name_list)):
                # 1列ずつ処理
                df_column_name = column_name_list[column_num]
                # "calc_name"に該当する項目かどうか
                # ex："温度（calc_name[0]）"が列滅名に含まれているか判定後〇なら0.1（calc_unit[0]）をかける
                if j_data["calc_name"][num] in df_column_name:
                    df[df_column_name] = round(df[df_column_name].astype(int)*float(j_data["calc_unit"][num]),2)
                else:
                    pass
        column_kazu =len(df.columns)
        column_newname=[]
        for i in range(column_kazu):
            db_num = 'a' + str(i)
            column_newname.append(db_num)
        df.columns = column_newname
        df['EQP_ID'] = j_data["eqp_id"]
        df['UNIT_NAME'] = j_data["unit_name"]
        df['UNIT_NUM'] = j_data["unit_num"]
        df['LOG_NUM'] = j_data["log_num"]
        df_new = df.rename(columns={'a0': 'MEASURED_DT'})
        # データをカンマ区切りに
        str_columnname = ','.join(df_new)
        df_new = df_new.astype(str)
        # print(df_new)
    ##########################################################################################################



    ###################1行ずつ処理：テーブル内にデータがあるか確認してから挿入###################################
        for index, row in df_new.iterrows():
            row['MEASURED_DT'] =row['MEASURED_DT'].replace("/","-")
            row = "'"+ row +"'"
            str_value = ','.join(map(str,row))
            try:
                str_value = str_value.replace("'nan'", "NULL")
            except:
                pass
            sql = "SELECT * FROM IOT_DATA.B22_PROCESS WHERE UNIT_NUM="\
            + row["UNIT_NUM"] +"AND MEASURED_DT="+ row["MEASURED_DT"]+"AND LOG_NUM="+row["LOG_NUM"]
            sql_rows = []
            stmt = ibm_db.exec_immediate(conn, sql)
            tuple = ibm_db.fetch_tuple(stmt)
            while tuple != False:
                sql_rows.append(tuple)
                tuple = ibm_db.fetch_tuple(stmt)
                # #sql_rowsがない場合、新規INSERT
            if sql_rows:
                pass
            # #sql_rowsの中のリストにテーブルの中身が入る
            else:
                str_value = ','.join(row)
                sql_insert = "INSERT INTO IOT_DATA.B22_PROCESS ("+ str_columnname +") values(" + str_value + ")" 
                logger.debug("SQL_insert:"+sql_insert)
                ibm_db.exec_immediate(conn,sql_insert)
##############################################################################################################
    except Exception as e:
        logger.exception(str(e))

logger.debug("************"+j_data["unit_num"]+"  "+j_data["unit_name"]+" TSの書き込み END*********************")
   