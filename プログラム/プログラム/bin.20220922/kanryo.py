#! python
# encoding: utf-8

# version: 0.7
# Last updated on 2020.04.02

#/*****************************************************************************/
#/*                                                                           */
#/* Program name        : kanryo.py                                           */ 
#/* Version             : 0.7                                                 */     
#/* Title               : 画像検査_完了報告プログラム                      　　  */ 
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
# 完了処理
#   引数情報を元に完了処理を実行する。
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
#   [Arg09]: 終了年月日         例）18/2/18
#   [Arg10]: 終了時分秒         例）20:18:15
#   [Arg11]: ロットNo           例）ABCDEFGH
#   [Arg12]: 処理数             例）123
#   [Arg13]: OK数               例）123
#   [Arg14]: NG数               例）123
#   [Arg15]: 画処不良モード1    例) 123
#   [Arg16]: 画処不良数1        例) 123
#   [Arg17]: 画処不良モード2    例) 123
#   [Arg18]: 画処不良数2        例) 123
#   [Arg19]: 画処不良モード3    例) 123
#   [Arg20]: 画処不良数3        例) 123
#   [Arg21]: 画処不良モード4    例) 123
#   [Arg22]: 画処不良数4        例) 123
#   [Arg23]: 画処不良モード5    例) 123
#   [Arg24]: 画処不良数5        例) 123
#   [Arg25]: 画処不良モード6    例) 123
#   [Arg26]: 画処不良数6        例) 123
#   [Arg27]: 画処不良モード7    例) 123
#   [Arg28]: 画処不良数7        例) 123
#   [Arg29]: 画処不良モード8    例) 123
#   [Arg30]: 画処不良数8        例) 123
#   [Arg31]: PLC不良モード1     例) 123
#   [Arg32]: PLC不良数1         例）123
#   [Arg33]: PLC不良モード2     例）123
#   [Arg34]: PLC不良数2         例）123
#   [Arg35]: PLC不良モード3     例）123
#   [Arg36]: PLC不良数3         例）123
#   [Arg37]: PLC不良モード4     例）123
#   [Arg38]: PLC不良数4         例）123
#   [Arg39]: PLC不良モード5     例）123
#   [Arg40]: PLC不良数5         例）123
#   [Arg41]: PLC不良モード6     例）123
#   [Arg42]: PLC不良数6         例）123
#   [Arg43]: PLC不良モード7     例）123
#   [Arg44]: PLC不良数7         例）123
#   [Arg45]: PLC不良モード8     例）123
#   [Arg46]: PLC不良数8         例）123
#   [Arg47]: 予備               例）ABCDEFGH
#   [Arg48]: 予備               例）ABCDEFGH
#   [Arg49]: 予備               例）ABCDEFGH
#   [Arg50]: 予備               例）ABCDEFGH
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
numargs = 50
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
en_date = argvs[9]
print('Arg09(終了年月日):   ' + en_date)
en_time = argvs[10]
print('Arg10(終了時分秒):   ' + en_time)
lotno = argvs[11]
print('Arg11(ロットNo):     ' + lotno)
num_prc = argvs[12]
print('Arg12(処理数):       ' + num_prc)
num_ok = argvs[13]
print('Arg13(OK数):         ' + num_ok)
num_ng = argvs[14]
print('Arg14(NG数):         ' + num_ng)
iing_mode1 = argvs[15]
print('Arg15(画処不良モード1): ' + iing_mode1)
iing_num1 = argvs[16]
print('Arg16(画処不良数1):     ' + iing_num1)
iing_mode2 = argvs[17]
print('Arg17(画処不良モード2): ' + iing_mode2)
iing_num2 = argvs[18]
print('Arg18(画処不良数2):     ' + iing_num2)
iing_mode3 = argvs[19]
print('Arg19(画処不良モード3): ' + iing_mode3)
iing_num3 = argvs[20]
print('Arg20(画処不良数3):     ' + iing_num3)
iing_mode4 = argvs[21]
print('Arg21(画処不良モード4): ' + iing_mode4)
iing_num4 = argvs[22]
print('Arg22(画処不良数4):     ' + iing_num4)
iing_mode5 = argvs[23]
print('Arg23(画処不良モード5): ' + iing_mode5)
iing_num5 = argvs[24]
print('Arg24(画処不良数5):     ' + iing_num5)
iing_mode6 = argvs[25]
print('Arg25(画処不良モード6): ' + iing_mode6)
iing_num6 = argvs[26]
print('Arg26(画処不良数6):     ' + iing_num6)
iing_mode7 = argvs[27]
print('Arg27(画処不良モード7): ' + iing_mode7)
iing_num7 = argvs[28]
print('Arg28(画処不良数7):     ' + iing_num7)
iing_mode8 = argvs[29]
print('Arg29(画処不良モード8): ' + iing_mode8)
iing_num8 = argvs[30]
print('Arg30(画処不良数8):     ' + iing_num8)
plcng_mode1 = argvs[31]
print('Arg31(PLC不良モード1):  ' + plcng_mode1)
plcng_num1 = argvs[32]
print('Arg32(PLC不良数1):      ' + plcng_num1)
plcng_mode2 = argvs[33]
print('Arg33(PLC不良モード2):  ' + plcng_mode2)
plcng_num2 = argvs[34]
print('Arg34(PLC不良数2):      ' + plcng_num2)
plcng_mode3 = argvs[35]
print('Arg35(PLC不良モード3):  ' + plcng_mode3)
plcng_num3 = argvs[36]
print('Arg36(PLC不良数3):      ' + plcng_num3)
plcng_mode4 = argvs[37]
print('Arg37(PLC不良モード4):  ' + plcng_mode4)
plcng_num4 = argvs[38]
print('Arg38(PLC不良数4):      ' + plcng_num4)
plcng_mode5 = argvs[39]
print('Arg39(PLC不良モード5):  ' + plcng_mode5)
plcng_num5 = argvs[40]
print('Arg40(PLC不良数5):      ' + plcng_num5)
plcng_mode6 = argvs[41]
print('Arg41(PLC不良モード6):  ' + plcng_mode6)
plcng_num6 = argvs[42]
print('Arg42(PLC不良数6):      ' + plcng_num6)
plcng_mode7 = argvs[43]
print('Arg43(PLC不良モード7):  ' + plcng_mode7)
plcng_num7 = argvs[44]
print('Arg44(PLC不良数7):      ' + plcng_num7)
plcng_mode8 = argvs[45]
print('Arg45(PLC不良モード8):  ' + plcng_mode8)
plcng_num8 = argvs[46]
print('Arg46(PLC不良数8):      ' + plcng_num8)

for i in range(47, 51):
    print('Arg%02d(予備):         %s' % (i, argvs[i]))

# 正常時のPLCへの完了通知内容
val = '1'
msg = lotno + ' 完了成功'

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

print('===== システム完工処理 ===========================')

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
    sql += "add9,"
    sql += "ryohin_qty,"
    sql += "furyo_qty,"
    sql += "furyo_qty01,"
    sql += "furyo_qty02,"
    sql += "furyo_qty03,"
    sql += "furyo_qty04,"
    sql += "furyo_qty05,"
    sql += "furyo_qty06,"
    sql += "furyo_qty07,"
    sql += "furyo_qty08,"
    sql += "furyo_qty09,"
    sql += "furyo_qty10,"
    sql += "furyo_qty11,"
    sql += "furyo_qty12,"
    sql += "furyo_qty13,"
    sql += "furyo_qty14,"
    sql += "furyo_qty15,"
    sql += "furyo_qty16,"
    sql += "user_id,"
    sql += "JISSEKI_SYUSEI_FLG"
    sql += ") VALUES ("
    sql += "'00',"
    sql += "'" + w_code + "',"
    sql += "to_date('20" + en_date + " " + en_time + "','yyyy-mm-dd hh24:mi:ss'),"
    sql += "'" + w_code + "',"
    sql += "to_date('20" + en_date + " " + en_time + "','yyyy-mm-dd hh24:mi:ss'),"
    sql += "'PRS',"
    sql += "'HA',"
    sql += "'" + lotno + "',"
    sql += "'" + p_code + "',"
    sql += "0,"
    sql += "to_date('20" + st_date + " " + st_time + "','yyyy-mm-dd hh24:mi:ss'),"
    sql += "to_date('20" + en_date + " " + en_time + "','yyyy-mm-dd hh24:mi:ss'),"
    sql += "'" + p_code + "',"
    sql += num_ok + ","
    sql += num_ng + ","
    sql += iing_mode1 + ","
    sql += iing_num1 + ","
    sql += iing_mode2 + ","
    sql += iing_num2 + ","
    sql += iing_mode3 + ","
    sql += iing_num3 + ","
    sql += iing_mode4 + ","
    sql += iing_num4 + ","
    sql += iing_mode5 + ","
    sql += iing_num5 + ","
    sql += iing_mode6 + ","
    sql += iing_num6 + ","
    sql += iing_mode7 + ","
    sql += iing_num7 + ","
    sql += iing_mode8 + ","
    sql += iing_num8 + ","
    sql += "'" + w_code + "',"
    sql += "'0')"
    print('SQL: ' + sql)
    rtn = None
    rtn = oraclelib.exec_Oracle_SQL(conn, sql)
    print('Result: ', end='')
    print(rtn)
    if rtn != None:
        msg = lotno + ' 完了成功'
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
