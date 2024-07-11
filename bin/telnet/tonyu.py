#! python
# encoding: utf-8

# 綾部3棟　DB2版
# version: 1.0
# Last updated on 2022.03.08

#======================================================================
# ステータスレコード更新
#   引数情報を元に、DBにレコードを削除・追加する。
#   レコード追加に成功した場合は完了通知デバイスに1を書き込む。
# 引数:
#   コマンドライン引数ファイル名
# コマンドライン引数ファイル:
#   [Arg01]: 連携PLC_IP     例）192.168.0.10
#   [Arg02]: 号機名         例）M001
#   [Arg03]: 年月日         例）18/2/18
#   [Arg04]: 時分秒         例）20:18:15
#   [Arg05]: パネルID       例) 
#   [Arg06]: レシピコード    例) 0
#   [Arg07]: 投入数            例) 0
#   [Arg08]: 完了通知デバイス            例) EM1000
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
if not os.path.isfile('./_config.ini'):
    print("<<Error>> Can't open './_config.ini'.")
    # プログラム終了
    sys.exit()
conffile = configparser.ConfigParser()
conffile.read('./_config.ini', 'UTF-8')

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
    tonyu_table = conffile.get('リアルタイムモニタDB', 'tonyu_table')
    print("tonyu_table: " + tonyu_table)
except:
    print("<<Error>> リアルタイムモニタDB接続情報が読み込めませんでした。")
    sys.exit() # プログラム終了

# KV接続情報
kvport = 8501

# 引数
numargs = 8
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
print("Arg02(号機名):     " + m_name)
date = argvs[3]
print("Arg03(年月日):     " + date)
time = argvs[4]
print("Arg04(時分秒):     " + time)
panel_id = argvs[5]
print("Arg05(パネルID):     " + panel_id)
recipe_code = argvs[6]
print("Arg06(レシピコード):     " + recipe_code)
tonyusu = argvs[7]
print("Arg07(投入数):     " + tonyusu)
dvname = argvs[8]
print("Arg08(完了通知デバイス): " + dvname)

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
    sql = "INSERT INTO " + tonyu_table + " ("
    sql += "EQP_ID,MEASURED_DT,PANEL_ID,RECIPE_CODE,COUNT"
    sql += ") VALUES ("
    sql += "'" + m_name + "',"
    sql += "to_timestamp('20" + date + " " + time + "','yyyy-mm-dd hh24:mi:ss'),"
    sql += "'" + panel_id + "',"
    sql += "'" + recipe_code + "',"
    sql += "'" + tonyusu + "')"
    print("SQL: " + sql)
    rtn = None
    rtn = db2lib.exec_DB2_SQL(conn, sql)
    print("Result: ", end="")
    print(rtn)
    if rtn != None:
        val = "1"
    else:
        val = "9"

# KVへの完了通知送信
print("===== 完了通知送信 ===============================")
print("完了通知: " + val)
kvlib.kv_send_WR(kvip, kvport, dvname, val)

dt_en = datetime.datetime.now()
print('Proc End: ' + dt_en.strftime("%Y/%m/%d %H:%M:%S.%f"))
dt_diff = dt_en - dt_st
print("Elapsed Time[s]: %d.%06d" % (dt_diff.seconds, dt_diff.microseconds))
