import sys
import glob
import json
from pathlib import Path
import logging
import logging.handlers
import pandas as pd
import ibm_db
import db2lib
import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("/IoT/bin/DB/debug.log")
file_handler.setLevel(logging.DEBUG)
file_handler_format = logging.Formatter('%(asctime)s : %(levelname)s - %(message)s')
file_handler.setFormatter(file_handler_format)
file_handler.setFormatter(file_handler_format)
logger.addHandler(file_handler)
#jsonファイル読み込み
args = sys.argv
fd = open(args[1], mode='r')
j_data = json.load(fd)
fd.close()

# DB接続
server = j_data["server"]
database = j_data["database"]
username = j_data["username"]
password = j_data["pw"]
conn = ibm_db.connect("DATABASE=" + database + ";HOSTNAME=" + server + ";PORT=50000;PROTOCOL=TCPIP;UID=" + username + ";PWD=" + password + ";", "", "")

logger.debug("************"+j_data["unit_num"]+"  "+j_data["unit_name"]+" COUNTの書き込み START*******************")
logger.debug('DB接続OK')
#csvファイル読み込み  
files = glob.glob(j_data["dst_dir"])
kousin_time =[]
#ファイルの数だけループ
for f in files:
    try:
        df = pd.read_csv(f,skiprows =13,usecols=[0,3,4], header=None,encoding="cp932", dtype=object)
        y =len(df.columns)
        h_name=[]
        for i in range(y):
            db_num = 'a' + str(i)
            h_name.append(db_num)
        df.columns = h_name
        # print(df)
        df['EQP_ID'] = j_data["eqp_id"]
        df['UNIT_NAME'] = j_data["unit_name"]
        df['UNIT_NUM'] = j_data["unit_num"]
        df["a0"] = pd.to_datetime(df["a0"])
        df["TAKTTIME"] = df["a0"].diff().map(lambda x: x.total_seconds())
        df_new = df.rename(columns={'a0': 'MEASURED_DT','a1': 'COUNT','a2': 'MATERIAL_ID'})
        str_columnname = ','.join(df_new)
        df_new = df_new.astype(str)
        # print(df_new)
        for index, row in df_new.iterrows():
            try:
                row['MEASURED_DT'] = row['MEASURED_DT'].replace("/","-")
                row = "'"+ row +"'"
                str_value = ','.join(map(str,row))
                try:
                    str_value = str_value.replace("'nan'", "NULL")
                except:
                    pass
                # SELECTでレコードが既存か確認
                sql = "SELECT * FROM IOT_DATA.COUNT WHERE EQP_ID="+ row["EQP_ID"] +"AND UNIT_NUM="\
                + row["UNIT_NUM"] + "AND MEASURED_DT="+ row['MEASURED_DT'] 
                sql_rows = []
                stmt = ibm_db.exec_immediate(conn, sql)
                tuple = ibm_db.fetch_tuple(stmt)
                while tuple != False:
                    sql_rows.append(tuple)
                    tuple = ibm_db.fetch_tuple(stmt)
                #sql_rowsのRELEASED_DTとrowのRELEASED_DTがイコールでない場合UPDATE、イコールの場合何もしない。
                if sql_rows:
                    pass
                #sql_rowsがなければ新規挿入 
                else:
                    sql_insert = "INSERT INTO IOT_DATA.COUNT ("+ str_columnname +") values(" + str_value + ")" 
                    logger.debug("SQL_insert:"+sql_insert)
                    ibm_db.exec_immediate(conn,sql_insert)
            except:
                pass
    except Exception as e:
        logger.exception(str(e))
logger.debug("************"+j_data["unit_num"]+"  "+j_data["unit_name"]+" COUNTの書き込み END*********************")
   