#########################################################
# Update:2023/1/19
# program Name:db2_TS.py
# Process:IOT_DATAの装置別に作成されたプロセスデータテーブル(PROCESS)へプロセスデータを保存（ファイルフォーマットは全設備共通(三菱タッチパネルの標準出力ロギングcsv))
# args: 1=json設定ファイルのファイルアドレス(参照ファイルの設定値を読み込んで登録値を設定)
#########################################################

from re import I
import sys
import glob
import json
from pathlib import Path
import logging
import logging.handlers
import pandas as pd
import ibm_db
import datetime
import os
import csv
import platform

#定数
max_sqlstr_byte = 2097152 #SQL構文の最大バイト長(DB2の場合)、INSERT等の構文はこのバイト長を超える文字列だとNGになる

# 改行コード
linesep = os.linesep
if platform.system() == 'Windows':
    linesep = '\n' #何故かWindowsのCRLFは上手くcsv改行ができない

rst = 0 #処理結果(0は処理正常)
dt_st = datetime.datetime.now()

##################################       logファイルの設定　　     #######################################
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# file_handler = logging.FileHandler(r"C:\Users\user\Desktop\IoT\debug_TS.log")
file_handler = logging.FileHandler(os.path.dirname(__file__) + "/debug.log")
file_handler.setLevel(logging.INFO) #INFO以上は出力
file_handler_format = logging.Formatter('%(asctime)s : %(levelname)s - %(message)s')
file_handler.setFormatter(file_handler_format)
file_handler.setFormatter(file_handler_format)
logger.addHandler(file_handler)
logger.info("==========================================================================================================")
logger.info("Program: " + __file__)

logger.info('Proc Start: ' + dt_st.strftime('%Y/%m/%d %H:%M:%S.%f'))
logger.info('----- Python Version -------------------')
logger.info(sys.version)
#############################################################################################################

##################################       設定ファイルの読み込み　　     #######################################
files_ReadErr = [] #過去に読み取りNGで処理されたファイルリスト
Dtype = "TS" #処理データの種類

if rst == 0:
    try:
        args = sys.argv
        # fd = open(args[1], mode='r', encoding='utf-8')
        fd = open(args[1], mode='r')
        j_data = json.load(fd)
        fd.close()
        logger.info("************" + j_data["unit_num"] + "  " +j_data["unit_name"] + " " + Dtype + "の書き込み START*******************")

        # 対象スキーマ、対象テーブルを取得
        target_schema = j_data["schema"] #スキーマ名(ドットまで記載、指定なければ空文字列)
        target_table_base = j_data["table"] #対象テーブル(一時テーブルも同じ名称から作成する)
        if target_table_base == None:
            logger.error("設定ファイル 登録NG : table is null")
            rst = 1 #処理異常
        else:
            # テーブル名を設定情報を元に作成
            temp_table = "tmp_" + target_table_base + "_" + j_data["eqp_id"] + "_" + j_data["unit_num"] #「temp_対象テーブル_装置ID_ユニットNo」の構成で一時テーブルを設定(一時テーブルの参照がかぶらないように固有の値とする)
            if target_schema == None:
                target_table = target_table_base # Merge対象のテーブル名
            else:
                target_table = target_schema + '.' + target_table_base # Merge対象のテーブル名

        # 必須のデータが存在するかを確認
        # csvファイルから取得するデータ列と登録カラム名
        column_get_csv = []
        if j_data["colname_measured_dt"] == None:
            logger.error("設定ファイル 登録NG : colname_measured_dt is null")
            rst = 1 #処理異常
        else:
            # csvファイルから取得するデータ列と登録カラム名
            colname_measured_dt = 'MEASURED_DT'
            column_get_csv.append([colname_measured_dt, j_data["colname_measured_dt"]])

        # 読み込みエラーが発生したファイルの履歴ファイル保存フォルダを指定、なければ作成
        dir_readerr = os.path.dirname(__file__) + "/ReadErr/" + Dtype
        if os.path.isdir(dir_readerr) == False:
            os.makedirs(dir_readerr)

        # 読み込みエラー履歴がある場合はNGファイルアドレスをリストで取得
        path_readerr = dir_readerr + "/" + j_data["eqp_id"] + "_" + j_data["unit_num"] + ".csv" #読み込みNGのファイルアドレス保存csv
        if os.path.isfile(path_readerr)==True: #既にファイルが作成済み(過去に読み取りエラーが発生したファイルがある)
            with open(path_readerr, 'r') as file:
                reader = csv.reader(file)
                next(reader) #先頭行をスキップ(データ名を記載しているため)
                for row in reader:
                    files_ReadErr.append(row[0]) # 0:読み取りNGファイルアドレス    

        # 参照フォルダが存在するかを確認、参照フォルダが存在しない（アドレスエラー、または保存対象外）場合はrst=1を指定し、以降の処理を行わない。
        path_dst_dir = j_data["dst_dir"]
        dir_list = glob.glob(os.path.dirname(path_dst_dir))
         # if os.path.isdir(os.path.dirname(path_dst_dir)) == False:
        if not dir_list:  
            logger.error("NG: directory path not exist")
            logger.error("dst_dir: " + path_dst_dir)
            rst = 1 #処理NG

    except Exception as e:
        logger.exception(str(e))
        rst = 1 #処理異常
#############################################################################################################

files_NG = [] #INSERTに失敗したファイルリスト
files_OK = [] #INSERTに成功したファイルリスト
list_sql = [] #実行するSQL構文と一括登録するレコード数、ファイルアドレスのリスト(0:SQL構文、1:登録レコード数, 2:ファイルアドレス)

# 一時テーブルに登録するデータのINSERT構文をcsvファイルを元に作成
if rst == 0:

    dt_st_process = datetime.datetime.now() #処理開始時間(デバッグ用)
    logger.info("-----   データファイル参照   -----")

    #Insert構文の基本部分(Valuesより前の構成、全構文で共通構成)

    #INSERT対象の列名
    column_insert = ['EQP_ID', 'UNIT_NUM', 'UNIT_NAME', 'MEASURED_DT', 'LOG_NUM'] #基本列名だけ記載、その他データ「A1～」の列は後で追加される

    # json設定ファイルから値を登録する対象列と項目名
    column_add_json = [["EQP_ID", "eqp_id"], 
                      ["UNIT_NUM", "unit_num"],
                      ["UNIT_NAME", "unit_name"],
                      ["LOG_NUM", "log_num"]]

    #csvファイルのリスト取得
    files = glob.glob(path_dst_dir)
    logger.debug("file cnt:" + str(len(files)))

    #ファイルの数だけループ
    for filepath in files:

        logger.debug("filepath:" + filepath)

        if filepath in files_ReadErr: #過去に読み取り失敗したファイルなら処理しない
            logger.error("Pass: This file was ReadError") 
            logger.error("filepath:" + filepath)
            continue

        # 前回読み取り出来ている、または初回読込ファイルなら処理を継続

        sqlcnt = 0 #1ファイルで作成したSQL構文数
        sql_insert = "" #INSERTのSQL構文
        sql_insert_value = "" #Values部分の構文
        cnt_insert = 0 #Insertレコード数(一括処理するので、登録行数をLogに保存)

        try:
            ################################# データに"装置ID","ユニット名"等追加・単位の修正######################################

            # csvデータをdataframeで取得
            df_csv = pd.read_csv(filepath, skiprows =9, header=0, encoding="cp932", dtype=object)
            
            # 取得したデータの行数が0の場合は飛ばして次のファイルを参照
            if len(df_csv) == 0:
                logger.error("Pass: This file not exist datarow") 
                logger.error("filepath:" + filepath)
                continue
            
            # ~~~~~~~~~~~~~~ここからcsvデータに合わせた処理を記載~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

            # 列名行とデータ行の間にある不要なデータ行を削除
            df_csv = df_csv.drop(index=df_csv.index[[0,1,2]])

            # 現状のcsvデータの列名を取得
            column_name_list = df_csv.columns.values

            # 列名でループ
            for df_column_name in column_name_list:
                
                # 単位修正する数でループ
                for num in range(len(j_data["calc_name"])):

                    # ex："温度（calc_name[0]）"が列滅名に含まれているか判定後〇なら0.1（calc_unit[0]）をかける
                    if j_data["calc_name"][num] in df_column_name:
                        # df_csv[df_column_name] = round(df_csv[df_column_name].astype(int)*float(j_data["calc_unit"][num]),2)
                        
                        try:
                            int_round = max(df_csv[df_column_name].apply(lambda x: len(x))) #有効桁数を参照データ列の文字数の最大値から設定
                        except:
                            int_round = 5 #デフォルトの有効桁数(取得に失敗した場合は有効桁数5で一旦設定)
                        if sum(c.isdigit() for c in str(j_data["calc_unit"][num])) > int_round:
                            int_round = sum(c.isdigit() for c in str(j_data["calc_unit"][num]))
                        df_csv[df_column_name] = round(df_csv[df_column_name].astype(int)*float(j_data["calc_unit"][num]),int_round)
                        break #1回一致したらその列の処理は終了、次の列名を参照
                        
                    else:
                        pass

            df_buff =pd.DataFrame({}) #空のデータフレーム作成

            # 列を丸ごと取得するcsvデータを格納
            for column_name_tb , column_name_csv in column_get_csv:
                if column_name_tb == colname_measured_dt: #登録日時のデータ(MEASURED_DT)
                    # 一旦Date型に変えてから、%Y-%m-%d %H:%M:%Sの文字列に変換
                    df_buff[column_name_tb] = (pd.to_datetime(df_csv[column_name_csv], format='%Y/%m/%d %H:%M:%S')).dt.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    # そのまま取得
                    df_buff[column_name_tb] = df_csv[column_name_csv]

            # json設定ファイルからデータを引用、保存(この時点で最大行数分はmeasured_dtから取得出来ているので)
            for colname, jsonid in column_add_json:
                df_buff[colname] = j_data[jsonid]

            # 列順再設定用の列名リストを作成
            column_reindex = [colname for colname in column_insert] #列順の並べ直し用(ベースはcolumn_insert)

            #その他データの取得開始列番を指定されていれば、その番号から後の列を参照
            if j_data["colname_other"] != None:

                #設定ファイルで指定された列番を基準にその他データを取得
                column_no_other = df_csv.columns.get_loc(j_data["colname_other"]) #整数変換

                # その他データ列を取得(終了時刻のデータ列(17列目まで)より後ろのデータを取得)
                df_other = df_csv.iloc[:, column_no_other:]

                # その他データを取り込む列名を作成(a1~)
                column_newname=[]

                # 取込対象のデータ数だけ連番で列名を作成（今回は全データ列を変更、A1～)
                for i in range(1, len(df_other.columns) + 1):
                    db_num = 'A' + str(i)
                    column_newname.append(db_num)
                    column_reindex.append(db_num) #その他データの列名を追記

                # df_otherの列名を再設定(ここで設定しないと列数が合わない)
                df_other.columns = column_newname

                # 作成したdf_otherをdf_insertに結合
                df_buff = pd.concat([df_buff, df_other], axis=1) #列方向に結合

            # 登録日時が重複している場合は、重複削除して後のデータを残す
            df_buff = df_buff.drop_duplicates(subset=colname_measured_dt, keep='last')

            # ~~~~~~~~~~~~~~ csv処理の終了 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

            # 列名をカンマ区切りで文字列結合
            str_columnname = ','.join(column_reindex)

            # 全データのデータ型を再度文字列に変更
            df_buff = df_buff.astype(str)

            # 欠損値(NaN)を文字列「NULL」に置換(念のために設定)
            df_buff = df_buff.replace('nan' ,'NULL')

            #列順を変更(sql_insert_baseに合わせる)
            df_buff = df_buff.reindex(columns = column_reindex)

            # Value構文用にカンマ区切りで結合したリストを作成
            df_insert = pd.DataFrame({})           
            for column_name in column_reindex:
                if column_name == column_reindex[0]:
                    df_cat = "'" + df_buff[column_name].astype(str) + "'" #一旦クオーテーションを付けたデータを作成
                    df_cat = df_cat.replace("'NULL'" ,'NULL') #NULLだけクオーテーション無しに設定(クオーテーションありだと文字列として登録されるため)
                    df_insert['Values'] = df_cat
                else:
                    df_cat = "'" + df_buff[column_name].astype(str) + "'" #一旦クオーテーションを付けたデータを作成
                    df_cat = df_cat.replace("'NULL'" ,'NULL') #NULLだけクオーテーション無しに設定(クオーテーションありだと文字列として登録されるため)
                    df_insert['Values'] = df_insert['Values'].str.cat(df_cat, sep=',') #各列をカンマ区切りで結合

            # dataframe列をリストに変換(処理を早くするため)
            list_insert = '(' + df_insert['Values'] + ')'

            # INSERTの基本構文を作成(列順はDataframe準拠。処理は後述の登録テーブルへのMERGEと同等、但し登録先は一時テーブル、登録データはデータファイルのValuesを結合したものを使用)           
            # 登録先を指定(一時テーブルが対象)
            sql_insert_top = "MERGE INTO " + temp_table + " AS TGT USING (VALUES "
            
            # データ元を指定(データファイルのValuesを結合したものを疑似テーブルとして使用し、カラム名を設定)
            sql_insert_buttom = ") AS INSERTDATA (" + ','.join([datarow for datarow in column_reindex]) + ")"

            # どのカラムを条件にINSERT or UPDATEを実行するか指定
            sql_insert_under = " ON ("\
                                "TGT.EQP_ID = INSERTDATA.EQP_ID"\
                                " AND TGT.UNIT_NUM = INSERTDATA.UNIT_NUM"\
                                " AND TGT.MEASURED_DT = INSERTDATA.MEASURED_DT"\
                                " AND TGT.LOG_NUM = INSERTDATA.LOG_NUM"\
                                ") "\
                                "WHEN NOT MATCHED THEN"

            sql_insert_under += ' INSERT (' + ','.join([datarow for datarow in column_reindex]) + ')'
            sql_insert_under += ' VALUES (INSERTDATA.' + ',INSERTDATA.'.join([datarow for datarow in column_reindex]) + ');' 

            #############################################################################################################

            ###############################   1行ずつ処理、SQL構文を作成し保存　　##########################################
            for str_value in list_insert:

                flg_append = True #list_sqlへ追加するかの判定(Trueで追加実行)

                # INSERT構文を作成(SQL構文をバイト数に換算した場合の最大制限があるので、それ以下まで行ごとにValueを追記する)
                if len((sql_insert_top + sql_insert_value + "," + str_value + "," + str_value + sql_insert_buttom + sql_insert_under).encode('utf-8')) >= max_sqlstr_byte:
                    #1. 文字列のバイト制限ギリギリになったらInsert実行(次回のValue追加で制限超えるのを疑似的に判定するため、同じValueを重ねて判定)
                    sql_insert = sql_insert_top + sql_insert_value + "," + str_value + sql_insert_buttom + sql_insert_under
                    cnt_insert += 1 # 登録レコード数を+1
                    list_sql.append([sql_insert, cnt_insert, filepath]) #SQLリストにSQL構文とレコード数、ファイルアドレスを登録
                    logger.debug("sql_cnt:" + str(cnt_insert) + ", sql_insert:" + sql_insert)

                    sql_insert_value = "" #Value文字列をリセット
                    cnt_insert = 0 #レコード数をリセット
                    flg_append = False #登録しない(この処理を最後にループを抜けた場合はリスト登録は行われない)
                    sqlcnt += 1 #作成構文数を+1

                else:
                    #2. バイト制限まで余裕がある場合は、Valueだけ結合
                    if sql_insert_value == "":
                        sql_insert_value = str_value
                    else:
                        sql_insert_value += "," + str_value
                    cnt_insert += 1 # 登録レコード数を+1

            if flg_append == True:
                sql_insert = sql_insert_top + sql_insert_value + sql_insert_buttom + sql_insert_under
                list_sql.append([sql_insert, cnt_insert, filepath]) #SQLリストにSQL構文とレコード数、ファイルアドレスを登録
                logger.debug("sql_cnt:" + str(cnt_insert) + ", sql_insert:" + sql_insert)
                sqlcnt += 1 #作成構文数を+1

            logger.debug("sqlcnt:" + str(sqlcnt))

            ##############################################################################################################

        except Exception as e:
            logger.exception(str(e))
            files_NG.append(filepath) #登録NGのファイルアドレスを追加
            #rst = 3 #SQL処理NG

    # 登録するデータがない（ファイルがない、または取得できたデータがない）場合はrst=1を指定し、以降の処理を行わない
    if len(list_sql) == 0:
        logger.error("NG: insert data is nothing")
        rst = 1 # 処理NG
        
    #処理時間(デバッグ用)
    dt_en_process = datetime.datetime.now()
    dt_diff_process = dt_en_process - dt_st_process
    logger.debug('Processed Time[s]: %d.%06d' % (dt_diff_process.seconds, dt_diff_process.microseconds))

##################################              DB接続                #######################################
if rst == 0:
    
    dt_st_process = datetime.datetime.now() #処理開始時間(デバッグ用)

    logger.info("-----   DB接続実行   -----")
    try:
        server = j_data["server"]
        database = j_data["database"]
        username = j_data["username"]
        password = j_data["pw"]
        conn = ibm_db.connect("DATABASE=" + database + ";HOSTNAME=" + server + ";PORT=50000;PROTOCOL=TCPIP;UID=" + username + ";PWD=" + password + ";", "", "")

        logger.debug('OK')

    except Exception as e:
        logger.error('NG')
        logger.exception(str(e))
        rst = 2 #DB接続NG

    #処理時間(デバッグ用)
    dt_en_process = datetime.datetime.now()
    dt_diff_process = dt_en_process - dt_st_process
    logger.debug('Processed Time[s]: %d.%06d' % (dt_diff_process.seconds, dt_diff_process.microseconds))

##########################################################################################################

############################   登録テーブルのカラム構造を取得   #############################################

if rst == 0:
    
    dt_st_process = datetime.datetime.now() #処理開始時間(デバッグ用)

    logger.info("-----   登録テーブル構造取得   -----")
    try:

        # 対象テーブルのカラム構成(列名、データ型、データ長を取得)
        sql_select = 'SELECT NAME, COLTYPE, LENGTH FROM SYSIBM.SYSCOLUMNS'\
                    ' WHERE TBNAME = ' + "'" + target_table_base + "'"\
                    ' AND TBCREATOR = ' + "'" + target_schema + "'"\
                    ' ORDER BY COLNO'
        rstset = ibm_db.exec_immediate(conn, sql_select) #create temp table実行 
        if rstset is False:
            logger.error("CNT:NG")
        else:
            logger.debug("CNT:OK")
            colname_target = []
            datarow = ibm_db.fetch_tuple(rstset)
            while datarow:
                colname_target.append([datarow[0], datarow[1], datarow[2]])
                datarow = ibm_db.fetch_tuple(rstset)
            logger.debug(colname_target)

    except Exception as e:
        logger.exception(str(e))
        rst = 3 #一時テーブル作成NG

    #処理時間(デバッグ用)
    dt_en_process = datetime.datetime.now()
    dt_diff_process = dt_en_process - dt_st_process
    logger.debug('Processed Time[s]: %d.%06d' % (dt_diff_process.seconds, dt_diff_process.microseconds))

#############################################################################################################

#################################   一時テーブルを作成   ##################################################

if rst == 0:
    
    dt_st_process = datetime.datetime.now() #処理開始時間(デバッグ用)

    logger.info("-----   TEMP TABLE作成実行   -----")
    try:
        
        # インデックス設定の対象列名、一時テーブルに設定
        column_index_tmp = ['EQP_ID', 'UNIT_NUM', 'MEASURED_DT', 'LOG_NUM']

        # 列名とデータ型の構成リスト、先述の対象テーブルのカラム構成をそのまま使って一時テーブルを作成
        column_create = []
        for datarow in colname_target:
            colname = datarow[0]
            coltype = datarow[1].replace(' ', '') #スペースが入ることがあるので削除する
            collength = datarow[2] 

            # データ型とデータ長を用いてを設定用データ型に変換
            if 'VAR' in coltype or 'CHAR' in coltype:
                column_create.append([colname, coltype + '(' + str(collength) + ')']) #設定長を含めてデータ型を設定
            elif 'TIMESTMP' == coltype:
                column_create.append([colname, 'TIMESTAMP']) #返り値はTIMESTMPになるので、TIMESTAMPで設定(※SYSTEM側から返ってくるデータ型はクライアント指定のと違う場合があるので注意)
            else:
                column_create.append([colname, coltype]) #データ型をそのまま設定

        # CREATEで一時テーブル(TEMP)を作成
        sql_create = "CREATE TEMP TABLE " + temp_table + " ("
        sql_create += ','.join([clmlist[0] + ' ' + clmlist[1] for clmlist in column_create]) + ");" # 「列名 データ型」の文字列をカンマ区切りで結合

        rstset = ibm_db.exec_immediate(conn, sql_create) #create temp table実行 
        if rstset is False:
            logger.error("CREATE:NG")
            rst = 3 #一時テーブル作成NG
        else:
            logger.debug("CREATE:OK")

            # インデックス作成を実行
            sql_create = "CREATE INDEX IDX_" + temp_table + " ON " + temp_table + "(" + ','.join([datarow for datarow in column_index_tmp]) + ");"
            rstset = ibm_db.exec_immediate(conn, sql_create) #create temp table実行 

            if rstset is False:
                logger.error("INDEX:NG")
                # rst = 3 #一時テーブル作成NG
            else:
                logger.debug("INDEX:OK")

    except Exception as e:
        logger.exception(str(e))
        rst = 3 #一時テーブル作成NG

    #処理時間(デバッグ用)
    dt_en_process = datetime.datetime.now()
    dt_diff_process = dt_en_process - dt_st_process
    logger.debug('Processed Time[s]: %d.%06d' % (dt_diff_process.seconds, dt_diff_process.microseconds))

#############################################################################################################

insertcnt = 0 #TEMP TABLEへINSERT出来たレコード数
if rst == 0:
    if len(list_sql) > 0: #実行するSQL構文がある場合
        
        ###############################   SQL構文を一時テーブルに処理実行　　##########################################

        dt_st_process = datetime.datetime.now() #処理開始時間(デバッグ用)

        logger.info("-----   INSERT処理実行   -----")
        for sql_insert , cnt_insert , filepath in list_sql:

            if filepath not in files_NG:
                
                # INSERT失敗したファイルのSQL構文でなければINSERT実行
                logger.debug("insert cnt:" + str(cnt_insert))
                logger.debug("insert sql:" + sql_insert[:200] + "……")
                logger.debug("insert filepath:" + filepath)

                #該当データがない場合(cnt_insert=0)は処理を飛ばす
                if cnt_insert == 0: 
                    logger.debug("Pass: insert cnt = 0")  
                    continue
                
                #登録するValueが取得出来ている場合は処理継続
                try:
                    dt_st_sql = datetime.datetime.now() #SQL開始時間(デバッグ用)
                    rstset = ibm_db.exec_immediate(conn, sql_insert) #Insert実行
                    dt_en_sql = datetime.datetime.now() #SQL終了時間(デバッグ用)
                    if rstset is False:
                        logger.error("NG")
                        dt_diff_sql = dt_en_sql - dt_st_sql
                        logger.debug('SQL Time[s]: %d.%06d' % (dt_diff_sql.seconds, dt_diff_sql.microseconds))
                        
                    else:
                        logger.debug("OK")
                        dt_diff_sql = dt_en_sql - dt_st_sql
                        logger.debug('SQL Time[s]: %d.%06d' % (dt_diff_sql.seconds, dt_diff_sql.microseconds))
                        files_OK.append(filepath) #全SQL成功したらOKファイルリスト追加
                        files_OK = sorted(files_OK) #重複削除

                except Exception as e:
                    logger.error("NG")
                    logger.exception(str(e))
                    if not filepath in files_NG:
                        files_NG.append(filepath) #登録NGのファイルアドレスを追加
                    files_NG = sorted(files_NG) #重複削除
                    if len(files_OK) > 0:
                        if filepath in files_OK:
                            files_OK.remove(filepath) #登録OKのファイルアドレスを削除

        try:
            sql_select ="SELECT COUNT(*) AS CNT FROM " + temp_table
            dt_st_sql = datetime.datetime.now() #SQL開始時間(デバッグ用)
            rstset = ibm_db.exec_immediate(conn, sql_select) #SELECT CNT実行
            dt_en_sql = datetime.datetime.now() #SQL終了時間(デバッグ用)
            if rstset is False:
                logger.error("CNT:NG")
                dt_diff_sql = dt_en_sql - dt_st_sql
                logger.debug('SQL Time[s]: %d.%06d' % (dt_diff_sql.seconds, dt_diff_sql.microseconds))
            else:
                logger.debug("CNT:OK")
                dt_diff_sql = dt_en_sql - dt_st_sql
                logger.debug('SQL Time[s]: %d.%06d' % (dt_diff_sql.seconds, dt_diff_sql.microseconds))
                datarow = ibm_db.fetch_tuple(rstset)
                insertcnt = datarow[0] #CNTを取得
                logger.debug("recordcnt:" + str(insertcnt))
                
        except Exception as e:
            logger.error("CNT ERROR")
            logger.exception(str(e))

        #処理時間(デバッグ用)
        dt_en_process = datetime.datetime.now()
        dt_diff_process = dt_en_process - dt_st_process
        logger.debug('Processed Time[s]: %d.%06d' % (dt_diff_process.seconds, dt_diff_process.microseconds))

    else:
        logger.exception("登録SQL数:0")
        rst = 4 #一時テーブル作成NG
        ##############################################################################################################

    # 登録OKのファイル0の場合（レコードなし、または途中のデータが登録不可で処理中断)
    if len(files_OK) == 0:
        rst = 4 #一時テーブルにレコード未登録

if rst == 0 and insertcnt > 0:
    ##########################   一時テーブルのデータを登録テーブルにMERGE   ########################################
    
    dt_st_process = datetime.datetime.now() #処理開始時間(デバッグ用)

    logger.info("-----   MERGE処理実行   -----")
    try:
        # UPDATEは無し、主キーが未登録のデータのみINSERT
        sql_merge = "MERGE INTO " + target_table + " AS TGT "\
                    "USING " + temp_table + " AS TMP "\
                    "ON ("\
                        "TGT.EQP_ID = TMP.EQP_ID"\
                        " AND TGT.UNIT_NUM = TMP.UNIT_NUM"\
                        " AND TGT.MEASURED_DT = TMP.MEASURED_DT"\
                        " AND TGT.LOG_NUM = TMP.LOG_NUM"\
                    ") "\
                    "WHEN NOT MATCHED THEN"

        sql_merge += " INSERT (" + ','.join([datarow[0] for datarow in colname_target]) + ')'
        sql_merge += ' VALUES (TMP.' + ',TMP.'.join([datarow[0] for datarow in colname_target]) + ');' #登録テーブルのカラムを全対象にしてINSERT(一時テーブルも同一構成なので、そのまま登録できる)

        #MERGE処理を実行
        logger.debug("SQL_merge:" + sql_merge)
        rstset = ibm_db.exec_immediate(conn, sql_merge)
        if rstset is False:
            logger.error("NG")
            rst = 5 #MERGE処理NG
        else:
            logger.debug("OK")

    except Exception as e:
        logger.exception(str(e))
        rst = 5 #MERGE処理NG
        files_NG = files #全ファイルの登録が出来ていないので、NGリストを全ファイルに設定

    #処理時間(デバッグ用)
    dt_en_process = datetime.datetime.now()
    dt_diff_process = dt_en_process - dt_st_process
    logger.debug('Processed Time[s]: %d.%06d' % (dt_diff_process.seconds, dt_diff_process.microseconds))

    #############################################################################################################

# 一時テーブルまで作成済みなら一時テーブル削除(無くてもいいが一応実行)
if rst == 0 or rst >= 3:
    #########################             一時テーブルの削除              ########################################
    try:
        logger.info("-----   TEMP TABLE削除   -----")
        sql_drop = "DROP TABLE " + temp_table +" ;"
        stmt = ibm_db.exec_immediate(conn, sql_drop)
        logger.debug("OK")
    except Exception as e:
        logger.error("NG")
        logger.exception(str(e))
    
    #############################################################################################################

    ##########################                DB2接続終了                 ########################################
    try:
        logger.info("-----   DB接続終了   -----")
        ibm_db.close(conn) #接続終了
        logger.debug("OK")
    except Exception as e:
        logger.error("NG")
        logger.exception(str(e))

    ##############################################################################################################

   ##########################            登録NGファイル処理              ########################################
try:
    if len(files_NG) > 0:
        # 登録NGのファイルアドレスを指定csvに追記
        with open(path_readerr, 'a') as file:
            for filepath in files_NG:
                file.write('"' + filepath + '"' + linesep) # 0:ロットNo, 1:着手時間        

except Exception as e:
    logger.exception(str(e))
   ##############################################################################################################

# End
dt_en = datetime.datetime.now()
logger.info('Proc End: ' + dt_en.strftime('%Y/%m/%d %H:%M:%S.%f'))
dt_diff = dt_en - dt_st
logger.info('Elapsed Time[s]: %d.%06d' % (dt_diff.seconds, dt_diff.microseconds))

logger.info("************" + j_data["unit_num"] + "  " +j_data["unit_name"] + " " + Dtype + "の書き込み END*******************")
logger.info("==========================================================================================================")