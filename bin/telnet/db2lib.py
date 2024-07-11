#! python
# encoding: utf-8

# version: 1.0
# Last updated on 2020.10.14

#======================================================================
# ibm_dbを用いたDB2データベース接続用ライブラリ
#======================================================================
import ibm_db
import sys
import os

#======================================================================
# connect_DB2()
#   DB2に接続し、Connectionオブジェクトを取得する。
# 引数:
#   server:   サーバー名/IPアドレス
#   port:     ポート番号
#   user:     ユーザ名
#   pswd:     パスワード
#   database: データベース名
# 戻り値:
#   正常終了した場合はConnectionオブジェクト、そうでない場合はNoneを返す。
#======================================================================
def connect_DB2(server, port, user, pswd, database):

    try:
        conn = ibm_db.connect("DATABASE=" + database + ";HOSTNAME=" + server + ";PORT=" + port + ";PROTOCOL=TCPIP;UID=" + user + ";PWD=" + pswd + ";", "", "")
        return conn

    except:
        print("\nError in db2lib.connect_DB2()")
        return None


#======================================================================
# exec_DB2_SelectSQL()
#   DB2に接続済みのConnectionオブジェクトで
#   SELECT SQLを実行し、結果を取得する。
# 引数:
#   conn:   Connectionオブジェクト
#   sql:    SQL文
# 戻り値:
#   正常終了した場合はクエリー結果リスト、そうでない場合はNoneを返す。
#======================================================================
def exec_DB2_SelectSQL(conn, sql):

    try:
        rows = []
        stmt = ibm_db.exec_immediate(conn, sql)
        tuple = ibm_db.fetch_tuple(stmt)
        while tuple != False:
            rows.append(tuple)
            tuple = ibm_db.fetch_tuple(stmt)
        if rows:
            return rows
        else:
            return None

    except:
        print("\nError in db2lib.exec_DB2_SelectSQL()")
        print(ibm_db.stmt_errormsg().encode('cp932', "ignore"))
        return None

#======================================================================
# exec_DB2_SQL()
#   DB2に接続済みのConnectionオブジェクトで
#   SQL(INSERT/UPDATE/DELETE)を実行する。
# 引数:
#   conn:   Connectionオブジェクト
#   sql:    SQL文
# 戻り値:
#   正常終了した場合は0、そうでない場合はNoneを返す。
#======================================================================
def exec_DB2_SQL(conn, sql):

    try:
        stmt = ibm_db.exec_immediate(conn, sql)
        
        return 0

    except: 
        print("\nError in db2lib.exec_DB2_SQL()")
        print(ibm_db.stmt_errormsg().encode('cp932', "ignore"))
        return None

