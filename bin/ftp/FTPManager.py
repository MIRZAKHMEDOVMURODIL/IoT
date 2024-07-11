import os
import sys
import json
import ntpath
import datetime
import platform
import posixpath
import ftplib
import logging
import logging.handlers
import re

# 改行コード
linesep = os.linesep
if platform.system() == 'Windows':
    linesep = '\n' #何故かWindowsのCRLFは上手くcsv改行ができない

# アドレスの区切り文字設定
def path_join(*args, os = None):
    os = os if os else platform.system()
    if os == 'Windows':
        return ntpath.join(*args)
    else:
        return posixpath.join(*args)

# JSONファイル読込（コメント付きも対応）
def JSON_load(path_copylog):
    json_obj = None #空データ作成
    try:
        with open(path_copylog, 'r', encoding='utf-8') as f:      # 開く
            text = f.read()                                   # 文字列を取得
        re_text = re.sub(r'/\*[\s\S]*?\*/|//.*', '', text)    # コメントを削除
        json_obj = json.loads(re_text)  
    except Exception as e:
        logger.error("<<error>> json file read")
        logger.error(str(e))
        json_obj=None
    finally:
        return(json_obj)

#**************************************************************************************
#***************************JSONファイルのValueを更新*******************************
#**************************************************************************************
def JSON_change_value(path_json):
    
    try:
        with open(path_json, mode='wt', encoding='utf-8') as file:
            json.dump(j_data, file, ensure_ascii=False, indent=2)
        return True   
    except Exception as e:
        logger.error("<<error>> can't change json file value")
        logger.error(str(e))
        return False
#**************************************************************************************
#**************************************************************************************

#**************************************************************************************
#*******************************FTPサーバー接続*****************************************
#**************************************************************************************
def FTP_connect(ip,user,password,acct=21,timeout=500):
    
    try:
        ftp_conn = ftplib.FTP(ip,user,password,acct,timeout)
        return ftp_conn
    except Exception as e:
        logger.error("<<error>> can't Connect FTP Server")
        logger.error(str(e))
        return None
    
#**************************************************************************************
#**************************************************************************************

#**************************************************************************************
#**********************対象フォルダのファイル一覧を作成**********************************
#**************************************************************************************
def FTP_getfilelist(dst_dir):
    ftp_file = []
    try:      
        ftp_conn.cwd(dst_dir) 
        ftp_conn.dir('./', ftp_file.append)
    except Exception as e:
        logger.error("<<error>> can't get FTP File List")
        logger.error(str(e))
    finally:
        return ftp_file

#**************************************************************************************
#**********************ファイルの更新日時をAM/PM →→→ 24h表記へ変更***********************
#**************************************************************************************
def Change_tm_format(time_ampm, yymmdd):

    # AM/PM表示を24時間表示に変更
    # 0時がAM12:00と表示されるため0:00に修正
    tm_update = None
    try:
        if "PM" in time_ampm:
            tm_update = datetime.datetime.strptime(yymmdd+' '+time_ampm, '%m-%d-%y %H:%M%p') + datetime.timedelta(hours=12)
        elif "AM" and "12" in time_ampm:
            tm_update = datetime.datetime.strptime(yymmdd+' '+time_ampm, '%m-%d-%y %H:%M%p') - datetime.timedelta(hours=12)
        else:
            tm_update = datetime.datetime.strptime(yymmdd+' '+time_ampm, '%m-%d-%y %H:%M%p')
    except Exception as e:
        logger.error("<<error>> can't change time format")
        logger.error(str(e))
    finally:
        return tm_update
#**************************************************************************************
#**************************************************************************************

#**************************************************************************************
#**************limit_timeより更新時間が新しければファイルをダウンロード*******************
#**************************************************************************************
def FTP_getfiles(filepath_ref, filepath_save):

    try:
        with open(filepath_save, 'wb') as download_f: #保存先のファイルを作成
            ftp_conn.retrbinary('RETR %s' % filepath_ref, download_f.write) #参照ファイルを引用、保存
        return True
    
    except Exception as e:
        logger.error("<<error>> can't get file:", filepath_ref, filepath_save)
        logger.error(str(e))
        return False
#************************************************************************************** 
#**************************************************************************************

# グローバル変数
rst = 0 #処理結果(0は処理正常)
dt_st = datetime.datetime.now()
root_dir = path_join("/IoT", "bin") #大本のフォルダを指定
eqp_id = "" #装置ID
eqp_name = "" #装置名
unit_num = "" #ユニットNo
unit_name = "" #ユニット名
log_num = "" #ログNo(QC、TS、hokyuのみ)
target_table_base = "" #登録先テーブル名(FTPは空白)
Dtype = "FTP" #データの種類
ProcType = "FTP" #処理の種類
ftp_conn = None
j_data = None
measured_dt_latest = "" #最終履歴日時

##################################       logファイルの設定　　     #######################################
os.makedirs(path_join(os.path.dirname(__file__) , "log"), exist_ok=True) #ログ保存ディレクトリを作成
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO) #INFO以上は出力
log_Path = path_join(os.path.dirname(__file__) , "log", "debug_"+ dt_st.strftime('%Y%m%d') +".log")
file_handler = logging.FileHandler(log_Path,encoding ='utf-8')
file_handler.setLevel(logging.INFO) #INFO以上は出力
file_handler_format = logging.Formatter('%(asctime)s : %(levelname)s - %(message)s')
file_handler.setFormatter(file_handler_format)
logger.addHandler(file_handler)

logger.info("==========================================================================================================")
logger.info("Program: " + __file__)
logger.info('Proc Start: ' + dt_st.strftime('%Y/%m/%d %H:%M:%S.%f'))
logger.info('----- Python Version -------------------')
logger.info(sys.version)

# jsonファイルの読み込み
try:
    args = sys.argv
    logger.debug("args: " + str(args))

    path_json = args[1]
    j_data = JSON_load(path_json)

    if j_data is None:
        rst = 1 #処理異常
    else:
        ip = j_data["ip"]
        user = j_data["user"]
        password = j_data["password"]
        dst_dir = j_data["dst_dir"]

        local_dir = j_data["local_dir"]
        os.makedirs(local_dir,exist_ok=True) #保存ディレクトリを作成

        limit_time = datetime.datetime.strptime(j_data["limit_time"],"%Y-%m-%d %H:%M:%S")
        measured_dt_latest = limit_time # 最終更新日時を設定

    if len(args) > 2:
        #共通設定ファイルが実装されるまで、暫定で装置・ユニット情報を直接送信
        eqp_id = args[2]
        eqp_name = args[3] 
        unit_num = args[4]
        unit_name = args[5]
        Dtype = args[6]
        
        if len(args)==8:
            log_num = args[7]
        logger.info("************" + eqp_id + " " + unit_num + " " + Dtype + ("" if log_num == "" else ("_" + str(log_num))) + "の書き込み START*******************")

    # # 共通設定からデータ取得
    # # 引数を取得(0:実行プログラムアドレス、1:共通設定ファイルアドレス、2:装置情報No、3:ユニットNo、4:ログNo)
    # j_data_com = JSON_load(args[1])
    # if j_data_com is None:
    #     rst = 1 #処理異常
    # else:
    #     # 装置情報(eqp_data)
    #     eqp = args[2]
    #     eqp_data = j_data_com[eqp]
    #     eqp_id = eqp_data["EQPID"] #装置ID
    #     eqp_name = eqp_data["EQPNAME"] #装置名

    #     # ユニット情報(unit_data)
    #     unit_num = args[3] #ユニットNo
    #     unit_data = eqp_data[unit_num] 
    #     unit_name = unit_data["UNIT_NAME"] #ユニット名
        
    #     # 対象データ情報(target_data)
    #     Dtype = args[4]
    #     if len(args)==6:
    #         log_num = args[5]
    #         target_data = unit_data[Dtype + "_"+ str(log_num)]
    #     else:
    #         target_data = unit_data[Dtype]

    #     # FTP情報(ftp_data)
    #     ftp_data = j_data_com["TP"]
    #     ftp_ip = ftp_data["IP"]
    #     ftp_user = ftp_data["user"]
    #     ftp_pwd = ftp_data["password"]
    #     cfg_path = target_data["config"]["FTPManager"]
    #     local_dir = target_data["ftp_dir"]

    #     j_data = JSON_load(cfg_path)
    #     if j_data is None:
    #         rst = 1 #処理異常
    #     else:  
    #         dst_dir = j_data["dst_dir"]

except Exception as e:
    logger.exception(str(e))
    rst = 1 #処理異常

if rst == 0:

    # FTPサーバー接続
    ftp_conn = FTP_connect(ip,user,password)
    if ftp_conn is not None:
        # カレントフォルダを指定し、保存ファイル一覧を取得
        ftp_file_list = FTP_getfilelist(dst_dir)
        logger.info("ftp file cnt:" + str(len(ftp_file_list)))

        if len(ftp_file_list) == 0:
            rst = -1 #参照ファイルなし

    else:
        rst = 2 # 接続NG

if rst == 0:
       
    list_tm_update =[] #取得完了ファイルの更新日時

    try:
        for line in ftp_file_list:
            
            # データ行を分割
            split_row = line.encode('Latin-1').decode('utf-8').split(maxsplit = 9)

            # 各データを格納
            filename = split_row[-1] #ファイル名
            filebase = os.path.splitext(filename)[0] #ファイル名(拡張子無し)
            exp = os.path.splitext(filename)[1] #拡張子

            time_ampm = split_row[1] #ファイル更新時間(AMPM表記)
            yymmdd = split_row[0] #ファイル更新日付

            tm_update = Change_tm_format(time_ampm, yymmdd) #時刻データをdatetimeに変換

            if tm_update is not None: #時刻データの変換に失敗している場合は処理スキップ
                if tm_update > limit_time: #前回処理時間より後のデータなら処理実行

                    #参照ファイルアドレス
                    filepath_ref = path_join(dst_dir, filename) 

                    # 保存先の年月フォルダを作成
                    root_save = path_join(local_dir, tm_update.strftime("%Y%m"))
                    os.makedirs(root_save, exist_ok=True)

                    # 特定のファイル名のみ末尾に現在時刻を追記
                    if "ALM" in filename or "STS" in filename: 
                        filepath_save = path_join(root_save, filebase + "_" + dt_st.strftime("%Y%m%d_%H%M%S") + exp) # ファイル名末尾に時刻を追加
                    else:
                        filepath_save = path_join(root_save, filename) # 元のファイル名を使用

                    # 保存処理を実行し、成功したら更新日時をリストに保存
                    if FTP_getfiles(filepath_ref, filepath_save):
                        logger.debug("Downloaded files: [" + filename + "]["+ str(tm_update) +"]")
                        list_tm_update.append(tm_update.strftime('%Y-%m-%d %H:%M:%S'))

    except Exception as e:
        logger.error("<<error>> can't download files")
        logger.error(str(e))

    logger.info("get file cnt:" + str(len(list_tm_update)))

    if len(list_tm_update) > 0:
        max_tm_update = max(list_tm_update)
        logger.info("max_tm_update:" + max_tm_update)
        measured_dt_latest = max_tm_update # 最終更新日時を設定
        j_data["limit_time"] = max_tm_update # 最終更新日時を設定
        if JSON_change_value(path_json): #jsonファイルへ保存を実行
            logger.info("limit_time:" + max_tm_update) 
    else:
        rst = -1 #保存ファイルなし

if rst == 0 or rst == -1: #FTP接続が完了している場合はclose実行
    ftp_conn.close()

# End
dt_en = datetime.datetime.now()
logger.info('Proc End: ' + dt_en.strftime('%Y/%m/%d %H:%M:%S.%f'))
dt_diff = dt_en - dt_st
logger.info('Elapsed Time[s]: %d.%06d' % (dt_diff.seconds, dt_diff.microseconds))

#処理履歴を保存(jsonファイル読込NGと登録データなしは記録しない(rst=1以外を記録))
if rst > 1 or rst == 0:
    log_hist = "hist_registered.log"
    msg_rst = ""
    if rst == 2:
        msg_rst = "FTP接続エラー"

    with open(path_join(root_dir, log_hist) , 'a') as file:
        # # 0:処理タイプ, 1:実行プログラム名, 2:装置ID, 3:装置名 4:ユニットNo, 5:ユニット名, 6:logNo, 7:登録データ種類, 8:登録先テーブル名(FTPは空白) 9:処理完了時間, 10:エラーNo, 11:エラー詳細
        # file.write('"' + ProcType + '"' + ',' +
        #            '"' + os.path.basename(__file__) + '"' + ',' +
        #            '"' + eqp_id + '"' + ',' +
        #            '"' + eqp_name + '"' + ',' +
        #            '"' + unit_num + '"' + ',' +
        #            '"' + unit_name + '"' + ',' +
        #            '"' + str(log_num) + '"' + ',' + 
        #            '"' + Dtype + '"' + ',' + 
        #            '"' + target_table_base + '"' + ',' + 
        #            '"' + dt_en.strftime('%Y-%m-%d %H:%M:%S') + '"' + ',' + 
        #            '"' + str(rst) + '"' + ',' + 
        #            '"' + msg_rst + '"' + linesep) 

        # 0:処理タイプ, 1:実行プログラム名, 2:装置ID, 3:装置名 4:ユニットNo, 5:ユニット名, 6:logNo, 7:登録データ種類, 8:登録先テーブル名(FTPは空白) 9:処理完了時間, 10:エラーNo, 11:エラー詳細, 12:最終データ発生日時
        file.write('"' + ProcType + '"' + ',' +
                   '"' + os.path.basename(__file__) + '"' + ',' +
                   '"' + eqp_id + '"' + ',' +
                   '"' + eqp_name + '"' + ',' +
                   '"' + unit_num + '"' + ',' +
                   '"' + unit_name + '"' + ',' +
                   '"' + str(log_num) + '"' + ',' + 
                   '"' + Dtype + '"' + ',' + 
                   '"' + target_table_base + '"' + ',' + 
                   '"' + dt_en.strftime('%Y-%m-%d %H:%M:%S') + '"' + ',' + 
                   '"' + str(rst) + '"' + ',' + 
                   '"' + msg_rst + '"' + ',' + 
                   '"' + measured_dt_latest + '"' + linesep)
        
# 変数の解放
del ftp_conn
del j_data

if rst != 1:
    logger.info("************" + eqp_id + " " + unit_num + " " + Dtype + ("" if log_num == "" else ("_" + str(log_num))) + "の書き込み END*******************")

logger.info("==========================================================================================================" + linesep)
