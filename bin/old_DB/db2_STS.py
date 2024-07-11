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

logger.debug("************"+j_data["unit_num"]+"  "+j_data["unit_name"]+" STSの書き込み START*******************")
logger.debug('DB接続OK')
#csvファイル読み込み  
files = glob.glob(j_data["dst_dir"])
#ファイルの数だけループ
for f in files:
    try:
            # print(f)
        #1行目にデータが無ければスキップ
        df = pd.read_csv(f,skiprows =14, encoding="cp932", dtype=object)
        df['date_diff'] = pd.to_datetime(df['RESTORED'],errors='coerce') - pd.to_datetime(df['OCCURRED'],errors='coerce')
        df['diff_time'] = df['date_diff'].map(lambda x: x.total_seconds())
        
        # #日時が重複した行を削除
        df_in = df.drop_duplicates(subset=['OCCURRED', 'RESTORED'], keep='last')
        df_in_1 =df_in.drop(['UPPER_NO','MIDDLE_NO','CHECKED','LEVEL','GROUP',"STATUS","date_diff"],axis=1)
        # # 列の生成
        df_in_2 =pd.DataFrame({})
        df_in_2['OCCURRED_DT'] = (df_in_1["OCCURRED"])
        df_in_2['RELEASED_DT'] = (df_in_1["RESTORED"])
        df_in_2['PASSED_TIME'] = (df_in_1["diff_time"])
        df_in_2['STATUS_CODE'] = (df_in_1["COMMENT_NO"])
        df_in_2['STATUS_CONTENTS'] = (df_in_1["COMMENT"])
        df_in_2['EQP_ID'] = (j_data["eqp_id"])
        df_in_2['UNIT_NUM'] = (j_data["unit_num"])
        df_in_2['UNIT_NAME'] = (j_data["unit_name"])
        # print(df_in_2)
        str_columnname = ','.join(df_in_2) 
        # 1行ずつ処理
        for index, row in df_in_2.iterrows():
            row['EQP_ID'] = str(row["EQP_ID"])
            row['UNIT_NUM'] = str(row["UNIT_NUM"])
            row['UNIT_NAME'] = str(row["UNIT_NAME"])
            row['OCCURRED_DT'] =row['OCCURRED_DT'].replace("/","-")
            row['STATUS_CONTENTS'] = str(row["STATUS_CONTENTS"])
            row['STATUS_CODE'] = str(row["STATUS_CODE"])

            # passed_timeがnullの場合、occurred_dtに現在時刻を入れて差分計算
            if pd.isnull(row["PASSED_TIME"]):
                # strftime：日付 -→ 文字列、strptime：文字列 -→ 日付
                row["RELEASED_DT"] = datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
                row["RELEASED_DT"] = datetime.datetime.strptime(row["RELEASED_DT"], '%Y-%m-%d %H:%M:%S')
                row['OCCURRED_DT'] = datetime.datetime.strptime(row['OCCURRED_DT'], '%Y-%m-%d %H:%M:%S')
                sabun = (row["RELEASED_DT"] - row['OCCURRED_DT']).total_seconds()
                # 日付型 -→　文字列
                row["PASSED_TIME"] = str(sabun)
                row["RELEASED_DT"] = str(row["RELEASED_DT"])
                row["OCCURRED_DT"] = str(row["OCCURRED_DT"])
                # row["PASSED_TIME"] = str(sabun.seconds)
            else:
                row['RELEASED_DT'] = row['RELEASED_DT'].replace("/","-")
                row['PASSED_TIME'] = str(row["PASSED_TIME"])
            row2 = "'"+ row +"'"
            # eqp_id unit_num released_dt status_contentsが重複しないか確認
            # try:
            sql = "SELECT * FROM IOT_DATA.STATUS WHERE EQP_ID="+ row2["EQP_ID"] +"AND OCCURRED_DT="\
            + row2["OCCURRED_DT"] + "AND STATUS_CONTENTS="+ row2['STATUS_CONTENTS'] + "AND UNIT_NUM="+ row2['UNIT_NUM']
            sql_rows = []
            stmt = ibm_db.exec_immediate(conn, sql)
            tuple = ibm_db.fetch_tuple(stmt)
            while tuple != False:
                sql_rows.append(tuple)
                tuple = ibm_db.fetch_tuple(stmt)
            #sql_rowsのRELEASED_DTとrowのRELEASED_DTがイコールでない場合UPDATE、イコールの場合何もしない。
            #sql_rowsがない場合、新規INSERT
            if sql_rows:
                released_time = sql_rows[0][4]
                row["RELEASED_DT"] = datetime.datetime.strptime(row["RELEASED_DT"], '%Y-%m-%d %H:%M:%S')
                if not released_time == row["RELEASED_DT"]:
                    sql_update = "UPDATE IOT_DATA.STATUS SET RELEASED_DT="+ row2["RELEASED_DT"] +",PASSED_TIME="+row2["PASSED_TIME"]+" WHERE EQP_ID="\
                    + row2["EQP_ID"] +"AND OCCURRED_DT="\
                    + row2["OCCURRED_DT"] + "AND STATUS_CONTENTS="+ row2['STATUS_CONTENTS']+ "AND UNIT_NUM="+ row2['UNIT_NUM'] 
                    ibm_db.exec_immediate(conn,sql_update)
                    logger.debug("SQL_update:"+sql_update)
                elif released_time == row["RELEASED_DT"]:
                    pass
            else:
                str_value = ','.join(row2)
                sql_insert = "INSERT INTO IOT_DATA.STATUS ("+ str_columnname +") values(" + str_value + ")" 
                logger.debug("SQL_insert:"+sql_insert)
                ibm_db.exec_immediate(conn,sql_insert)
    except Exception as e:
        logger.exception(str(e))
logger.debug("************"+j_data["unit_num"]+"  "+j_data["unit_name"]+" STSの書き込み END*********************")