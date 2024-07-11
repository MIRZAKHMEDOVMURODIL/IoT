import sys
import glob
import json
from pathlib import Path
import logging
import logging.handlers
import pandas as pd
import ibm_db
import datetime

##################################       logファイルの設定　　     #######################################
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("/IoT/bin/DB/debug.log")
file_handler.setLevel(logging.DEBUG)
file_handler_format = logging.Formatter('%(asctime)s : %(levelname)s - %(message)s')
file_handler.setFormatter(file_handler_format)
file_handler.setFormatter(file_handler_format)
logger.addHandler(file_handler)
#############################################################################################################


##################################       設定ファイルの読み込み　　     #######################################
args = sys.argv
fd = open(args[1], mode='r')
j_data = json.load(fd)
fd.close()
#############################################################################################################


##################################              DB接続                #######################################
server = j_data["server"]
database = j_data["database"]
username = j_data["username"]
password = j_data["pw"]
conn = ibm_db.connect("DATABASE=" + database + ";HOSTNAME=" + server + ";PORT=50000;PROTOCOL=TCPIP;UID=" + username + ";PWD=" + password + ";", "", "")

logger.debug("************"+j_data["unit_num"]+"  "+j_data["unit_name"]+" ALMの書き込み START*******************")
logger.debug('DB接続OK')
##########################################################################################################


################################# データに"装置ID","ユニット名"等追加　######################################
#csvファイル読み込み  
files = glob.glob(j_data["dst_dir"])
#ファイルの数だけループ
for f in files:
    try:
        df = pd.read_csv(f,skiprows =14, encoding="cp932", dtype=object)
        # 時間の差分を計算して秒に変換
        df['diff'] = pd.to_datetime(df['RESTORED'],errors='coerce') - pd.to_datetime(df['OCCURRED'],errors='coerce')
        df['passed_time'] = df['diff'].map(lambda x: x.total_seconds())

        # 新しいデータフレームに必要な情報を抜粋してゆく
        new_df =pd.DataFrame({})
        new_df['OCCURRED_DT'] = (df["OCCURRED"])
        new_df['RELEASED_DT'] = (df["RESTORED"])
        new_df['PASSED_TIME'] = (df["passed_time"])
        new_df['ALM_MESSAGE'] = (df["COMMENT"])
        new_df['EQP_ID'] = (j_data["eqp_id"])
        new_df['UNIT_NUM'] = (j_data["unit_num"])
        new_df['UNIT_NAME'] = (j_data["unit_name"])
        new_df['ALM_CODE'] = (df["COMMENT_NO"])
        str_columnname = ','.join(new_df)
#############################################################################################################


#######################################   1行ずつ処理   ######################################################
    
        for index, pre_row in new_df.iterrows():
            # DB挿入のため文字列に変換
            pre_row['ALM_MESSAGE'] = str(pre_row["ALM_MESSAGE"])
            pre_row['EQP_ID'] = str(pre_row["EQP_ID"])
            pre_row['UNIT_NUM'] = str(pre_row["UNIT_NUM"])
            pre_row['UNIT_NAME'] = str(pre_row["UNIT_NAME"])
            # 上記で開始-終了の差分計算ができていないときは現在時刻を入れて経過時間PASSED_TIMEを計算
            if pd.isnull(pre_row["PASSED_TIME"]):
                pre_row["RELEASED_DT"] = datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
                pre_row["RELEASED_DT"] = datetime.datetime.strptime(pre_row["RELEASED_DT"], '%Y-%m-%d %H:%M:%S')
                pre_row['OCCURRED_DT'] = pre_row['OCCURRED_DT'].replace("/","-")
                pre_row['OCCURRED_DT'] = datetime.datetime.strptime(pre_row['OCCURRED_DT'], '%Y-%m-%d %H:%M:%S')
                sabun = (pre_row["RELEASED_DT"] - pre_row['OCCURRED_DT']).total_seconds()
                # DB挿入のため時間関係を文字列に変換
                pre_row["PASSED_TIME"] = str(sabun)
                pre_row["RELEASED_DT"] = str(pre_row["RELEASED_DT"])
                pre_row["OCCURRED_DT"] = str(pre_row["OCCURRED_DT"])
                # pre_row["PASSED_TIME"] = str(sabun.seconds)
            # 経過時間がある場合はDB挿入用にデータ加工
            else:
                pre_row['OCCURRED_DT'] = pre_row['OCCURRED_DT'].replace("/","-")
                pre_row['RELEASED_DT'] = pre_row['RELEASED_DT'].replace("/","-")
                pre_row['PASSED_TIME'] = str(pre_row["PASSED_TIME"])
            # DB挿入用にシングルクォーテーションで囲い、カンマ区切りにする
            post_row = "'"+ pre_row +"'"

            # SELECTでレコードが既存か確認
            sql = "SELECT * FROM IOT_DATA.ALARM WHERE EQP_ID="+ post_row["EQP_ID"] +"AND UNIT_NUM="\
            + post_row["UNIT_NUM"] + "AND ALM_MESSAGE="+ post_row['ALM_MESSAGE'] + \
            "AND OCCURRED_DT="+ post_row['OCCURRED_DT']
            sql_rows = []
            stmt = ibm_db.exec_immediate(conn, sql)
            tuple = ibm_db.fetch_tuple(stmt)
            while tuple != False:
                sql_rows.append(tuple)
                tuple = ibm_db.fetch_tuple(stmt)
            #sql_rowsのRELEASED_DTとrowのRELEASED_DTがイコールでない場合UPDATE、イコールの場合何もしない。
            if sql_rows:
                released_time = sql_rows[0][5]
                pre_row["RELEASED_DT"] = datetime.datetime.strptime(pre_row["RELEASED_DT"], '%Y-%m-%d %H:%M:%S')
                if not released_time == pre_row["RELEASED_DT"]:
                    sql_update = "UPDATE IOT_DATA.ALARM SET RELEASED_DT="+ post_row["RELEASED_DT"] +",PASSED_TIME="+post_row["PASSED_TIME"]+" WHERE EQP_ID="\
                    + post_row["EQP_ID"] +"AND OCCURRED_DT="+ post_row["OCCURRED_DT"] + "AND ALM_MESSAGE="\
                    + post_row['ALM_MESSAGE']+ "AND UNIT_NUM="+ post_row['UNIT_NUM']
                    ibm_db.exec_immediate(conn,sql_update)
                    logger.debug("SQL_update:"+sql_update)
                elif released_time == pre_row["RELEASED_DT"]:
                    pass
            #sql_rowsがなければ新規挿入 
            else:
                str_value = ','.join(post_row)
                sql_insert = "INSERT INTO IOT_DATA.ALARM ("+ str_columnname +") values(" + str_value + ")" 
                logger.debug("SQL_insert:"+sql_insert)
                ibm_db.exec_immediate(conn,sql_insert)
##############################################################################################################
    except Exception as e:
        logger.exception(str(e))
logger.debug("************"+j_data["unit_num"]+"  "+j_data["unit_name"]+" ALMの書き込み END*********************")