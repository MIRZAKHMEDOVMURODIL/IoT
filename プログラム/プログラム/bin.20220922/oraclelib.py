#! python
# encoding: utf-8

# version: 0.9.5
# Last updated on 2018.9.20

#======================================================================
# cx_Oracleを用いたOracleデータベース接続用ライブラリ
#======================================================================
import cx_Oracle
import sys
import os

#======================================================================
# connect_Oracle()
#   Oracle DBに接続し、Connectionオブジェクトを取得する。
# 引数:
#   server:  サーバー名/IPアドレス
#   port:    ポート番号
#   user:    ユーザ名
#   pswd:    パスワード
#   service: サービス名
# 戻り値:
#   正常終了した場合はConnectionオブジェクト、そうでない場合はNoneを返す。
#======================================================================
def connect_Oracle(server, port, user, pswd, service):

    try:
        conn = cx_Oracle.connect(user, pswd, server + ':' + port + '/' + service)
        return conn

    except:
        print("\nError in oraclelib.connect_Oracle()")
        return None


#======================================================================
# exec_Oracle_SelectSQL()
#   OracleDBに接続済みのConnectionオブジェクトで
#   SELECT SQLを実行し、結果を取得する。
# 引数:
#   conn:   Connectionオブジェクト
#   sql:    SQL文
# 戻り値:
#   正常終了した場合はクエリー結果リスト、そうでない場合はNoneを返す。
#======================================================================
def exec_Oracle_SelectSQL(conn, sql):

    try:
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        return rows

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print("\nError in oraclelib.exec_Oracle_SelectSQL()")
        print(error.code)
        print(error.message)
        print(error.context)
        return None

#======================================================================
# exec_Oracle_SQL()
#   OracleDBに接続済みのConnectionオブジェクトで
#   SQL(INSERT/UPDATE/DELETE)を実行する。
# 引数:
#   conn:   Connectionオブジェクト
#   sql:    SQL文
# 戻り値:
#   正常終了した場合は0、そうでない場合はNoneを返す。
#======================================================================
def exec_Oracle_SQL(conn, sql):

    try:
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        return 0

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print("\nError in oraclelib.exec_Oracle_SQL()")
        print(error.code)
        print(error.message)
        print(error.context)
        return None

#======================================================================
# exec_Oracle_PRC()
#   OracleDBに接続済みのConnectionオブジェクトで
#   ストアドプロシージャを実行し、結果を取得する。
# 引数:
#   conn:   Connectionオブジェクト
#   func:    プロシージャ名
#   param:    パラメータ
# 戻り値:
#   正常終了した場合は0、そうでない場合はNoneを返す。
#======================================================================
def exec_Oracle_PRC(conn, func, param):

    try:
        cur = conn.cursor()
        cur.callproc(func,param)
        return 0

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print("\nError in oraclelib.exec_Oracle_PRC()")
        print(error.code)
        print(error.message)
        print(error.context)
        return None
