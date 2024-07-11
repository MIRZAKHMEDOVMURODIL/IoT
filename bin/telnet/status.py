#! python
# encoding: utf-8

# 綾部3棟　DB2版
# version: 1.0
# Last updated on 2022.09.02 ishitobi

#======================================================================
# ステータスレコード更新
#   引数情報を元に、DBにレコードを削除・追加する。
#   レコード追加に成功した場合は完了通知デバイスに1を書き込む。
# 引数:
#   コマンドライン引数ファイル名
# コマンドライン引数ファイル:
#   [Arg01]: 連携PLC_IP     例）192.168.0.10
#   [Arg02]: 装置ID_ユニットNo         例）M001
#   [Arg03]: 年月日         例）18/2/18
#   [Arg04]: 時分秒         例）20:18:15
#   [Arg05]: パネルID       例) 
#   [Arg06]: レシピコード    例) 0
#   [Arg07]: E01            例) 0
#   [Arg08]: E02            例) 0
#   [Arg09]: E03            例) 0
#   [Arg10]: E04            例) 0
#   [Arg11]: E05            例) 0
#   [Arg12]: E06            例) 0
#   [Arg13]: E07            例) 0
#   [Arg14]: E08            例) 0
#   [Arg15]: E09            例) 0
#   [Arg16]: E10            例) 0
#   [Arg17]: E11            例) 0
#   [Arg18]: E12            例) 0
#   [Arg19]: E13            例) 0
#   [Arg20]: E14            例) 0
#   [Arg21]: E15            例) 0
#   [Arg22]: E16            例) 0
#   [Arg23]: 完了通知デバイス         例) EM1000
# 戻り値:
#======================================================================

import sys
import os
import datetime
import kvlib
import db2lib
import configparser

# 処理開始
print("======================================================================")
print(__file__)
dt_st = datetime.datetime.now()
print('Proc Start: ' + dt_st.strftime("%Y/%m/%d %H:%M:%S.%f"))
print('----- Python Version -------------------')
print(sys.version)

# 設定ファイル読み込み
if not os.path.isfile('./config.ini'):
    print("<<Error>> Can't open './config.ini'.")
    # プログラム終了
    sys.exit()
conffile = configparser.ConfigParser()
conffile.read('./config.ini', 'UTF-8')

# リアルタイムモニタDB接続情報
print("----- リアルタイムモニタDB接続情報 -----")
try:
    server = conffile.get('リアルタイムモニタDB', 'server')
    print("server:   " + server)
    port = conffile.get('リアルタイムモニタDB', 'port')
    print("port:     " + port)
    user = conffile.get('リアルタイムモニタDB', 'user')
    print("user:     " + user)
    pswd = conffile.get('リアルタイムモニタDB', 'pswd')
    print("pswd:     " + pswd)
    database = conffile.get('リアルタイムモニタDB', 'database')
    print("database: " + database)
    schema = conffile.get('リアルタイムモニタDB', 'schema')
    print("schema:   " + schema)
    latest_status_table = conffile.get('リアルタイムモニタDB', 'latest_status_table')
    print("latest_status_table: " + latest_status_table)

    contsE01 = conffile.get('ステータス内容', 'E01')
    print("E01: " + contsE01)
    contsE02 = conffile.get('ステータス内容', 'E02')
    print("E02: " + contsE02)
    contsE03 = conffile.get('ステータス内容', 'E03')
    print("E03: " + contsE03)
    contsE04 = conffile.get('ステータス内容', 'E04')
    print("E04: " + contsE04)
    contsE05 = conffile.get('ステータス内容', 'E05')
    print("E05: " + contsE05)
    contsE06 = conffile.get('ステータス内容', 'E06')
    print("E06: " + contsE06)
    contsE07 = conffile.get('ステータス内容', 'E07')
    print("E07: " + contsE07)
    contsE08 = conffile.get('ステータス内容', 'E08')
    print("E08: " + contsE08)
    contsE09 = conffile.get('ステータス内容', 'E09')
    print("E09: " + contsE09)
    contsE10 = conffile.get('ステータス内容', 'E10')
    print("E10: " + contsE10)
    contsE11 = conffile.get('ステータス内容', 'E11')
    print("E11: " + contsE11)
    contsE12 = conffile.get('ステータス内容', 'E12')
    print("E12: " + contsE12)
    contsE13 = conffile.get('ステータス内容', 'E13')
    print("E13: " + contsE13)
    contsE14 = conffile.get('ステータス内容', 'E14')
    print("E14: " + contsE14)
    contsE15 = conffile.get('ステータス内容', 'E15')
    print("E15: " + contsE15)
    contsE16 = conffile.get('ステータス内容', 'E16')
    print("E16: " + contsE16)
except:
    print("<<Error>> リアルタイムモニタDB接続情報が読み込めませんでした。")
    sys.exit() # プログラム終了

# KV接続情報
kvport = 8501

# 引数
numargs = 23
print("----- 引数 -----------------------------")
argvs = sys.argv
if len(argvs) != 2:
    print("<<Error>> スクリプト引数が不正です。")
    for i in range(1, len(argvs)):
        print("  Arg{0:02d}: {1}".format(i, argvs[i]))
    sys.exit() # プログラム終了

# コマンドライン引数ファイルから引数の読み込み
f = open(sys.argv[1], 'r', encoding='cp932')
argvs = ['']
for row in f:
    argvs.append(row.rstrip('\n'))
if len(argvs) < numargs + 1:
    print("<<Error>> 引数の数が不足しています。(" + str(len(argvs) - 1) + " < " + str(numargs) + ")")
    for i in range(1, len(argvs)):
        print("  Arg{0:02d}: {1}".format(i, argvs[i]))
    sys.exit() # プログラム終了

kvip = argvs[1]
print("Arg01(連携PLC_IP): " + kvip)
m_name = argvs[2]
print("Arg02(装置ID_ユニットNo):     " + m_name)
date = argvs[3]
print("Arg03(年月日):     " + date)
time = argvs[4]
print("Arg04(時分秒):     " + time)
panel_id = argvs[5]
print("Arg05(パネルID):     " + panel_id)
recipe_code = argvs[6] 
print("Arg06(レシピコード):     " + recipe_code)
StatusID=""
Status=""
if argvs[7]=="1":
    StatusID="E01"
    Status=contsE01
elif argvs[8]=="1":
    StatusID="E02"
    Status=contsE02
elif argvs[9]=="1":
    StatusID="E03"
    Status=contsE03
elif argvs[10]=="1":
    StatusID="E04"
    Status=contsE04
elif argvs[11]=="1":
    StatusID="E05"
    Status=contsE05
elif argvs[12]=="1":
    StatusID="E06"
    Status=contsE06
elif argvs[13]=="1":
    StatusID="E07"
    Status=contsE07
elif argvs[14]=="1":
    StatusID="E08"
    Status=contsE08
elif argvs[15]=="1":
    StatusID="E09"
    Status=contsE09
elif argvs[16]=="1":
    StatusID="E10"
    Status=contsE10
elif argvs[17]=="1":
    StatusID="E11"
    Status=contsE11
elif argvs[18]=="1":
    StatusID="E12"
    Status=contsE12
elif argvs[19]=="1":
    StatusID="E13"
    Status=contsE13
elif argvs[20]=="1":
    StatusID="E14"
    Status=contsE14
elif argvs[21]=="1":
    StatusID="E15"
    Status=contsE15
elif argvs[22]=="1":
    StatusID="E16"
    Status=contsE16


print("Arg07-11:                " + argvs[7] + " " + argvs[8] + " " + argvs[9] + " " + argvs[10] + " " + argvs[11])
print("Arg12-16:                " + argvs[12] + " " + argvs[13] + " " + argvs[14] + " " + argvs[15] + " " + argvs[16])
print("Arg17-22:                " + argvs[17] + " " + argvs[18] + " " + argvs[19] + " " + argvs[20] + " " + argvs[21] + " " + argvs[22])
print("Arg07-22(ステータスID):  " + StatusID)
print("Arg07-22(ステータス):    " + Status)
dvname = argvs[23]
print("Arg23(完了通知デバイス): " + dvname)

# DBレコード追加
print("===== DBレコード追加 =============================")

# DB接続
print("----- DB接続 ---------------------------")
conn = None
conn = db2lib.connect_DB2(server, port, user, pswd, database)
if conn != None:
    print("DB接続成功")

    # SQL実行
    print("----- SQL実行 --------------------------")
    # 現在データ取得
    sql = "SELECT EQPID_UNITNUM, OCCURED_DT, RELEASED_DT, MATERIAL_ID, RECIPE_CODE, STATUS, STATUS_CONTENTS "
    sql += "FROM " + latest_status_table + " WHERE EQPID_UNITNUM = '" + m_name + "'"
    print("SQL: " + sql)
    rows = None
    rows = db2lib.exec_DB2_SelectSQL(conn, sql)
    print("Result: ", end="")
    print(rows)
    # データが存在する場合
    if rows != None:
        # len(rows) > 0：データが存在する
        if len(rows) > 0:
            for row in rows:
                # 同じStatusIDの場合はRELEASED_DATEのみ更新
                if row[5] == StatusID:
                    sql = "UPDATE " + latest_status_table + " "
                    sql += "SET RELEASED_DT = to_timestamp('20" + date + " " + time + "','yyyy-mm-dd hh24:mi:ss') "
                    sql += "WHERE EQPID_UNITNUM = '" + m_name + "'"
                    print("SQL: " + sql)
                    rtn = None
                    rtn = db2lib.exec_DB2_SQL(conn, sql)
                    print("Result: ", end="")
                    print(rtn)
                    if rtn != None:
                        val = "1"
                    else:
                        val = "9"
                
                # 異なるStatusIDの場合はEQP_ID以外を更新
                else:
                    sql = "UPDATE " + latest_status_table + " "
                    sql += "SET OCCURED_DT = to_timestamp('20" + date + " " + time + "','yyyy-mm-dd hh24:mi:ss'),"
                    sql += "RELEASED_DT = to_timestamp('20" + date + " " + time + "','yyyy-mm-dd hh24:mi:ss'),"
                    
                    sql += "STATUS = '" + StatusID + "', "
                    sql += "STATUS_CONTENTS = '" + Status + "' "
                    sql += "WHERE EQPID_UNITNUM = '" + m_name + "'"
                    print("SQL: " + sql)
                    rtn = None
                    rtn = db2lib.exec_DB2_SQL(conn, sql)
                    print("Result: ", end="")
                    print(rtn)
                    if rtn != None:
                        val = "1"
                    else:
                        val = "9"
                break

        # データが存在しない場合はINSERT
        else:
           pass
    else:
        sql = "INSERT INTO " + latest_status_table + " ("
        sql += "EQPID_UNITNUM,OCCURED_DT,RELEASED_DT,STATUS,STATUS_CONTENTS"
        sql += ") VALUES ("
        sql += "'" + m_name + "',"
        sql += "to_timestamp('20" + date + " " + time + "','yyyy-mm-dd hh24:mi:ss'),"
        sql += "to_timestamp('20" + date + " " + time + "','yyyy-mm-dd hh24:mi:ss'),"
        sql += "'" + StatusID + "',"
        sql += "'" + Status + "'"
        sql += ")"
        print("SQL: " + sql)
        rtn = None
        rtn = db2lib.exec_DB2_SQL(conn, sql)
        print("Result: ", end="")
        print(rtn)
        if rtn != None:
            val = "1"
        else:
            val = "9"

else:
    print("Error: DB接続エラー")
    val = "9"

# KVへの完了通知送信
print("===== 完了通知送信 ===============================")
print("完了通知: " + val)
kvlib.kv_send_WR(kvip, kvport, dvname, val)

dt_en = datetime.datetime.now()
print('Proc End: ' + dt_en.strftime("%Y/%m/%d %H:%M:%S.%f"))
dt_diff = dt_en - dt_st
print("Elapsed Time[s]: %d.%06d" % (dt_diff.seconds, dt_diff.microseconds))
