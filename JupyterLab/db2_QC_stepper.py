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

#**************************************************************************************
# ログファイルの設定
#**************************************************************************************
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("/IoT/bin/DB/debug.log")
file_handler.setLevel(logging.DEBUG)
file_handler_format = logging.Formatter('%(asctime)s : %(levelname)s - %(message)s')
file_handler.setFormatter(file_handler_format)
file_handler.setFormatter(file_handler_format)
logger.addHandler(file_handler)

#**************************************************************************************
# jsonの読み込み
#**************************************************************************************
args = sys.argv
fd = open(args[1], mode='r')
j_data = json.load(fd)
fd.close()


#**************************************************************************************
# DB接続
#**************************************************************************************
server = j_data["server"]
database = j_data["database"]
username = j_data["username"]
password = j_data["pw"]
conn = ibm_db.connect("DATABASE=" + database + ";HOSTNAME=" + server + ";PORT=50000;PROTOCOL=TCPIP;UID=" + username + ";PWD=" + password + ";", "", "")

logger.debug("************"+j_data["unit_num"]+"  "+j_data["unit_name"]+" スケールデータの書き込み START*******************")
try:
    conn = ibm_db.connect("DATABASE=" + database + ";HOSTNAME=" + server + ";PORT=50000;PROTOCOL=TCPIP;UID=" + username + ";PWD=" + password + ";", "", "")
    logger.debug('DB接続OK')
except:
    logger.exception("DB接続失敗")

#**************************************************************************************
# SQL実行
#**************************************************************************************
def DB2_exec_SQL(conn,sql,sql_rows):
    stmt = ibm_db.exec_immediate(conn, sql)
    tuple = ibm_db.fetch_tuple(stmt)
    while tuple != False:
        sql_rows.append(tuple)
        tuple = ibm_db.fetch_tuple(stmt)
    return(sql_rows)


#**************************************************************************************
# マスタテーブルを呼び出しsql_rowsに格納
#**************************************************************************************
sql = "SELECT * FROM IOT_DATA.B36A_SCALE_MASTER"
sql_rows = []
sql_rows = DB2_exec_SQL(conn,sql,sql_rows)

#**************************************************************************************
# 1.CSVを1行ずつ読み込みマスタスケールとMask_ID下3桁が一致すればスケールを計算
# 2.measured_dtをテーブルから検索してなければINSERT
#**************************************************************************************
files = glob.glob(j_data["dst_dir"])
for f in files:
    try:
        df = pd.read_csv(f,encoding="cp932", dtype=object)
        for index, row in df.iterrows():
            for i in range(0,len(sql_rows)):
                master_layer = sql_rows[i][0].replace("'","").upper()
                mask_id = row["MaskID"].upper()
                if master_layer in mask_id:
                    
                    mag_gen = float(row["MagGS_ppm"])
                    mag_x = float(row["MagX_ppm"])
                    mag_y = float(row["MagY_ppm"])
                    maskscale_x = float(sql_rows[i][1].replace("'",""))
                    maskscale_y = float(sql_rows[i][2].replace("'",""))
                    scale_data=pd.Series()
                    scale_data["SCALE_X"] = str(maskscale_x + (mag_gen*pow(10,-6)) + (mag_x*pow(10,-6)))
                    scale_data["SCALE_Y"] = str(maskscale_y + (mag_gen*pow(10,-6)) + (mag_y*pow(10,-6)))
                    scale_data["UNIT_NAME"] = j_data["unit_name"]
                    scale_data["UNIT_NUM"] = j_data["unit_num"]
                    scale_data["EQP_ID"] = j_data["eqp_id"]
                    scale_data["MATERIAL_ID"] = row["SubID"]
                    scale_data["MEASURED_DT"] = (row["Date"]+ " "+row["Time"]).replace("/","-")
                    db2column_name=[]
                    for i in range(len(row)):
                        db_num = 'a' + str(i+1)
                        db2column_name.append(db_num)
                    scale_data_index = ','.join(scale_data.index)
                    db2column_name.append(scale_data_index)
                    db2column_name = ','.join(map(str,db2column_name))
                    ins_row = pd.concat([row, scale_data], join='inner')
                    ins_row = "'"+ ins_row +"'"
                    str_value = ','.join(map(str,ins_row))
                    try:
                        str_value = str_value.replace("nan", "NULL")
                    except:
                        pass

                    sql_2 = "SELECT * FROM IOT_DATA.B36A_STEPPER_ID_PROCESS WHERE MEASURED_DT="+ ins_row["MEASURED_DT"]
                    sql_rows2 = []
                    if DB2_exec_SQL(conn,sql_2,sql_rows2):
                        pass
                    else:
                        sql_insert = "INSERT INTO IOT_DATA.B36A_STEPPER_ID_PROCESS ("+ db2column_name +") values(" + str_value + ")"
                        ibm_db.exec_immediate(conn,sql_insert)  
                        print("SQL :"+ sql_insert)
    except:
        pass
                        
logger.debug("************"+j_data["unit_num"]+"  "+j_data["unit_name"]+" スケールデータの書き込み END*********************")
    