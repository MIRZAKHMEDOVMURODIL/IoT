#! python
# encoding: utf-8

# version: 2.0
# Last updated on 2019.12.10

#======================================================================
# Keyence KV 通信用ライブラリ
#======================================================================

import socket

#======================================================================
# kv_send_WR()
#   KVにデータを書き込む。
# 引数:
#   ip:     KV IPアドレス
#   port:   ポート番号
#   dmname: 書き込み先DM名
#   val:    書き込み値
# 戻り値:
#   正常終了した場合は0、そうでない場合は1を返す。
#======================================================================
def kv_send_WR(ip, port, dmname, val):

    message = "WR " + dmname + " " + val + "\r"

    print("  kvlib.kv_send_WR() host:    " + str(ip) + ":" + str(port))
    print("  kvlib.kv_send_WR() message: " + message)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message.encode(), (ip, port))

    return 0


#======================================================================
# kv_send_WRS()
#   KVに連続データを書き込む。
# 引数:
#   ip:     KV IPアドレス
#   port:   ポート番号
#   dmname: 書き込み先DM名
#   vals:   書き込み値リスト
# 戻り値:
#   正常終了した場合は0、そうでない場合は1を返す。
#======================================================================
def kv_send_WRS(ip, port, dmname, vals):

    message = "WRS " + dmname + " " + str(len(vals))

    for val in vals:
        message += " " + val
    message += "\r"

    print("  kvlib.kv_send_WRS() host:    " + str(ip) + ":" + str(port))
    print("  kvlib.kv_send_WRS() message: " + message)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message.encode(), (ip, port))

    return 0

#======================================================================
# str2sjisvals()
#   文字列をシフトJISコード10進数の数字文字列のリストに変換する。
#   終端文字としてリストの末尾には"0"を付与する。
# 引数:
#   msg:    変換対象文字列
# 戻り値:
#   文字列リストを返す。
#======================================================================
def str2sjisvals(msg):
    bytesdata = b''
    for char in msg:
        bytesdata += char.encode('shift-jis')
    vals=[]
    numbytes = len(bytesdata) 
    for i in range(0, numbytes - 1, 2):
        vals.append(str(int.from_bytes(bytesdata[i:i+2], 'big')))
    if numbytes % 2 == 1:
        vals.append(str(int.from_bytes(bytesdata[numbytes - 1:numbytes], 'big') << 8))
    vals.append("0")    
    
    return vals

#======================================================================
# kv_send_WRSL()
#   KVに連続データを書き込む。
# 引数:
#   ip:     KV IPアドレス
#   port:   ポート番号
#   dmname: 書き込み先DM名
#   vals:   書き込み値リスト
# 戻り値:
#   正常終了した場合は0、そうでない場合は1を返す。
#======================================================================
def kv_send_WRSL(ip, port, dmname, vals):

    message = "WRS " + dmname + ".L " + str(len(vals))

    for val in vals:
        message += " " + str(val)
    message += "\r"

    print("  kvlib.kv_send_WRS() host:    " + str(ip) + ":" + str(port))
    print("  kvlib.kv_send_WRS() message: " + message)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message.encode(), (ip, port))

    return 0
