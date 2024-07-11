'''
Created on 2020/04/03

@author: suzuki
'''

import oraclelib

if __name__ == '__main__':
    server = '10.9.110.165'
    port = '1521'
    user = 'XBB'
    pswd = 'oracle'
    service = 'XBB'

    conn = None
    conn = oraclelib.connect_Oracle(server, port, user, pswd, service)
    if conn != None:
        print("DB接続成功")
    else:
        print("DB接続失敗")
