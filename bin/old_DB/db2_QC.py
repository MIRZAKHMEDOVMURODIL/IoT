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
logger.debug("************"+j_data["unit_num"]+"  "+j_data["unit_name"]+" QCの書き込み START*******************")
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
##########################################################################################################################


################################# データに"装置ID","ユニット名"追加、単位の修正、加工等######################################
#csvファイル読み込み  
files = glob.glob(j_data["dst_dir"])
#ファイルの数だけループ
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
        abc =pd.Series()
        for index, row in df.iterrows():
            
        #     #時間データを加工しabcに格納
            df_starttime = row[5] +"-"+row[6]+"-"+row[7]+" "+row[8]+":"+row[9]+":"+row[10]
            df_endtime = row[11] +"-"+row[12]+"-"+row[13]+" "+row[14]+":"+row[15]+":"+row[16]
            if not df_starttime == '0-0-0 0:0:0' and not df_endtime == '0-0-0 0:0:0':
                df_starttime = datetime.datetime.strptime(df_starttime, '%Y-%m-%d %H:%M:%S')
                df_starttime = df_starttime.strftime('%Y-%m-%d %H:%M:%S')
                df_endtime = datetime.datetime.strptime(df_endtime, '%Y-%m-%d %H:%M:%S')
                df_endtime = df_endtime.strftime('%Y-%m-%d %H:%M:%S')
            #     # 設定ファイルの情報を格納
                abc["EQP_ID"] = j_data["eqp_id"]
                abc['UNIT_NUM'] = j_data["unit_num"]
                abc['UNIT_NAME'] = j_data["unit_name"]
                abc["MEASURED_DT"] = row[0].replace("/","-")
                abc["LOG_NUM"] = j_data["log_num"]
                abc["ST_TIME"] = df_starttime
                abc["END_TIME"] = df_endtime
                abc["MATERIAL_ID"] = row[3]
                abc["RECIPE_CODE"] = row[4]
            #     #上記で作成した列までの列番号を作成し、その列を削除
                del_list = df.columns[0:17]
                row = row.drop(del_list)
                # # プロセスデータの列名をA1~に書き換え
                y = len(row)
                col_namelist=[]
                for i in range(y):
                    col_name = 'a' + str(i+1)
                    col_namelist.append(col_name)
                row.index = col_namelist
                row = row.append(abc)
                str_columnname = ','.join(row.index)
                row = row.astype(str)
                row = "'"+ row +"'"
                str_value = ','.join(map(str,row))
                try:
                    str_value = str_value.replace("nan", "NULL")
                except:
                    pass
##########################################################################################################################


#################################### テーブル内にデータがあるか確認してから挿入###################################
                sql = "SELECT * FROM IOT_DATA.B22_ID_PROCESS WHERE ST_TIME="\
                + row["ST_TIME"] +"AND END_TIME="+ row["END_TIME"] +"AND LOG_NUM="+ row["LOG_NUM"]
                sql_rows = []
                stmt = ibm_db.exec_immediate(conn, sql)
                tuple = ibm_db.fetch_tuple(stmt)
                while tuple != False:
                    sql_rows.append(tuple)
                    tuple = ibm_db.fetch_tuple(stmt)
                    # #sql_rowsがない場合、新規INSERT
                if sql_rows:
                    pass
                else:
                    str_value = ','.join(row)
                    sql_insert = "INSERT INTO IOT_DATA.B22_ID_PROCESS ("+ str_columnname +") values(" + str_value + ")" 
                    logger.debug("SQL_insert:"+sql_insert)
                    ibm_db.exec_immediate(conn,sql_insert) 
            else:
                pass
    except Exception as e:
        logger.exception(str(e))
logger.debug("************"+j_data["unit_num"]+"  "+j_data["unit_name"]+" QCの書き込み END*********************")
    