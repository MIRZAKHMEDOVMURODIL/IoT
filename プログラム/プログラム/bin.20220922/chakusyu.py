#! python
# encoding: utf-8

# version: 0.7
# Last updated on 2020.04.02

#/*****************************************************************************/
#/*                                                                           */
#/* Program name        : chakusyu.py                                         */ 
#/* Version             : 0.7                                                 */     
#/* Title               : 画像検査_着手報告プログラム                           */ 
#/* Description         :                                                     */
#/*                                                                           */ 
#/* Argument            : None                                                */ 
#/* MODIFICATION HISTORY:                                                     */
#/*    Date     Ver     Name     Description                                  */
#/* ---------- ----- ----------- -----------------------------------------    */
#/* 2022/09/21  R0.01  KC I.ina  工程コード桁数チェック 　　                    */
#/*                                                                           */
#/*                                                                           */
#/*                                                                           */
#/*****************************************************************************/


#======================================================================
# 着手処理
#   引数情報を元に着手処理を実行する。
#   処理に成功した場合は完了通知デバイスに1を、
#   失敗した場合は9(※0,1以外)を書き込む。
# 引数:
#   コマンドライン引数ファイル名
# コマンドライン引数ファイル:
#   [Arg01]: 連携PLC_IP                 例）192.168.0.10
#   [Arg02]: 応答コメント先頭デバイス   例）EM2000
#   [Arg03]: 完了通知デバイス           例）EM3000
#   [Arg04]: 作業者コード       例）ABCDEFGH
#   [Arg05]: 号機コード         例）M001
#   [Arg06]: 工程コード         例）ABCDEFGH
#   [Arg07]: 開始年月日         例）18/2/18
#   [Arg08]: 開始時分秒         例）20:18:15
#   [Arg09]: ロットNo           例）ABCDEFGH
#   [Arg10]: 予備               例）ABCDEFGH
#   [Arg11]: 予備               例）ABCDEFGH
#   [Arg12]: 予備               例）ABCDEFGH
#   [Arg13]: 予備               例）ABCDEFGH
#   [Arg14]: 予備               例）ABCDEFGH
#   [Arg15]: 予備               例）ABCDEFGH
#   [Arg16]: 予備               例）ABCDEFGH
#   [Arg17]: 予備               例）ABCDEFGH
#   [Arg18]: 予備               例）ABCDEFGH
#   [Arg19]: 予備               例）ABCDEFGH
#   [Arg20]: 予備               例）ABCDEFGH
#   [Arg21]: 予備               例）ABCDEFGH
#   [Arg22]: 予備               例）ABCDEFGH
#   [Arg23]: 予備               例）ABCDEFGH
#   [Arg24]: 予備               例）ABCDEFGH
#   [Arg25]: 予備               例）ABCDEFGH
#   [Arg26]: 予備               例）ABCDEFGH
#   [Arg27]: 予備               例）ABCDEFGH
#   [Arg28]: 予備               例）ABCDEFGH
#   [Arg29]: 予備               例）ABCDEFGH
# 戻り値:
#======================================================================

import configparser
import csv
import datetime
import kvlib
import os
import platform
import sys
import shutil
import oraclelib

# 処理開始
print('======================================================================')
print(__file__)
dt_st = datetime.datetime.now()
print('Proc Start: ' + dt_st.strftime('%Y/%m/%d %H:%M:%S.%f'))
print('----- Python Version -------------------')
print(sys.version)

# 設定ファイル読み込み
if not os.path.isfile('./_config.ini'):
    print("<<Error>> Can't open './_config.ini'.")
    # プログラム終了
    sys.exit()
conffile = configparser.ConfigParser()
conffile.read('./_config.ini', 'UTF-8')

# 生産管理DB 接続情報
print("----- 生産管理DB接続情報 ---------------")
try:
    server = conffile.get('生産管理DB', 'server')
    print("server:  " + server)
    port = conffile.get('生産管理DB', 'port')
    print("port:    " + port)
    user = conffile.get('生産管理DB', 'user')
    print("user:    " + user)
    pswd = conffile.get('生産管理DB', 'pswd')
    print("pswd:    " + pswd)
    service = conffile.get('生産管理DB', 'service')
    print("service: " + service)
    table = conffile.get('生産管理DB', 'table')
    print("table:   " + table)
except:
    print("<<Error>> 生産管理DB接続情報が読み込めませんでした。")
    sys.exit() # プログラム終了

# Oracle用のおまじない
os.environ["NLS_LANG"] = "JAPANESE_JAPAN.AL32UTF8"

# KV接続情報
kvport = 8501

# 改行コード
linesep = '\r\n'    # Windows形式 CR+LF

# 引数
numargs = 29
print('----- 引数 -----------------------------')
argvs = sys.argv
if len(argvs) != 2:
    print('<<Error>> スクリプト引数が不正です。')
    for i in range(1, len(argvs)):
        print('  Arg{0:02d}: {1}'.format(i, argvs[i]))
    sys.exit() # プログラム終了

# コマンドライン引数ファイルから引数の読み込み
f = open(sys.argv[1], 'r', encoding='cp932')
argvs = ['']
for row in f:
    argvs.append(row.rstrip('\n'))
if len(argvs) < numargs + 1:
    print('<<Error>> 引数の数が不足しています。(' + str(len(argvs) - 1) + ' < ' + str(numargs) + ')')
    for i in range(1, len(argvs)):
        print('  Arg{0:02d}: {1}'.format(i, argvs[i]))
    sys.exit() # プログラム終了

kvip = argvs[1]
print('Arg01(連携PLC_IP):               ' + kvip)
m_dmname = argvs[2]
print('Arg02(応答コメント先頭デバイス): ' + m_dmname)
r_dmname = argvs[3]
print('Arg03(完了通知デバイス):         ' + r_dmname)
w_code = argvs[4]
print('Arg04(作業者コード): ' + w_code)
m_code = argvs[5]
print('Arg05(号機コード):   ' + m_code)
p_code = argvs[6]
print('Arg06(工程コード):   ' + p_code)
st_date = argvs[7]
print('Arg07(開始年月日):   ' + st_date)
st_time = argvs[8]
print('Arg08(開始時分秒):   ' + st_time)
lotno = argvs[9]
print('Arg09(ロットNo):     ' + lotno)

for i in range(10, 30):
    print('Arg%02d(予備):         %s' % (i, argvs[i]))

# 正常時のPLCへの完了通知内容
val = '1'
msg = lotno + ' 着手成功'

# ロットNoチェック
if lotno == '':
    val = '2'
    msg = 'ロットNo空欄エラー'
    print('<<Error>> ロットNo空欄エラー')

# R0.01 Add Start
# 工程コード桁数チェック
if len(p_code) != 4:
    val = '2'
    msg = '工程コード桁数不足'
    print('<<Error>> 工程コード入力エラー')
# R0.01 Add End

print('===== システム着工処理 ===========================')

# DB接続
print('----- DB接続 ---------------------------')
conn = None
conn = oraclelib.connect_Oracle(server, port, user, pswd, service)
if conn != None:
    print('DB接続成功')

    print('----- SQL実行 --------------------------')
    sql = "INSERT INTO " + table + " ("
    sql += "CompanyCD,"
    sql += "RegisteredPerson,"
    sql += "RegisteredDT,"
    sql += "UpdatedPerson,"
    sql += "UpdatedDT,"
    sql += "TANMATSU_ID,"
    sql += "JIGYOBU_CD,"
    sql += "flot_no,"
    sql += "fproc_id,"
    sql += "flot_qty,"
    sql += "start_date,"
    sql += "end_date,"
    sql += "ryohin_qty,"
    sql += "furyo_qty,"
    sql += "user_id,"
    sql += "JISSEKI_SYUSEI_FLG"
    sql += ") VALUES ("
    sql += "'00',"
    sql += "'" + w_code + "',"
    sql += "to_date('20" + st_date + " " + st_time + "','yyyy-mm-dd hh24:mi:ss'),"
    sql += "'" + w_code + "',"
    sql += "to_date('20" + st_date + " " + st_time + "','yyyy-mm-dd hh24:mi:ss'),"
    sql += "'PRS',"
    sql += "'HA',"
    sql += "'" + lotno + "',"
    sql += "'" + p_code + "',"
    sql += "0,"
    sql += "to_date('20" + st_date + " " + st_time + "','yyyy-mm-dd hh24:mi:ss'),"
    sql += "to_date('20" + st_date + " " + st_time + "','yyyy-mm-dd hh24:mi:ss'),"
    sql += "0,"
    sql += "0,"
    sql += "'" + w_code + "',"
    sql += "'2')"
    print('SQL: ' + sql)
    rtn = None
    rtn = oraclelib.exec_Oracle_SQL(conn, sql)
    print('Result: ', end='')
    print(rtn)
    if rtn != None:
        msg = lotno + ' 着手成功'
        print(msg)
        val = '1'
    else:
        msg = '<<Error>> '  + lotno + ' SQL Insert失敗'
        print(msg)
        val = '2'

else:
    msg = '<<Error>> DB接続失敗'
    print(msg)
    val = '2'

# KVへの応答コメント送信
print('===== 応答コメント送信 ===========================')
print('Start: ' + datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S.%f'))
print('応答コメント: ' + msg)
vals = kvlib.str2sjisvals(msg)
kvlib.kv_send_WRS(kvip, kvport, m_dmname, vals)

# KVへの完了通知送信
print('===== 完了通知送信 ===============================')
print('Start: ' + datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S.%f'))
print('完了通知: ' + val)
kvlib.kv_send_WR(kvip, kvport, r_dmname, val)

# End
dt_en = datetime.datetime.now()
print('Proc End: ' + dt_en.strftime('%Y/%m/%d %H:%M:%S.%f'))
dt_diff = dt_en - dt_st
print('Elapsed Time[s]: %d.%06d' % (dt_diff.seconds, dt_diff.microseconds))
