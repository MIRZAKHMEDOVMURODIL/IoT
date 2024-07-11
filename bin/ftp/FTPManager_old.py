import os
import sys
import json
import ntpath
import shutil
import pathlib
import datetime
import platform
import posixpath
import argparse
from glob import glob
import ftplib
import parser
from glob import glob
from enum import Enum
import logging
import logging.handlers
import traceback


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("/IoT/bin/ftp/log/debug.log")
file_handler.setLevel(logging.DEBUG)
file_handler_format = logging.Formatter('%(asctime)s : %(levelname)s - %(message)s')
file_handler.setFormatter(file_handler_format)
file_handler.setFormatter(file_handler_format)
logger.addHandler(file_handler)


def path_join(*args, os = None):
    os = os if os else platform.system()
    if os == 'windows':
        return ntpath.join(*args)
    else:
        return posixpath.join(*args)

#**************************************************************************************
#*******************************JSONファイルの情報を取得*********************************
#**************************************************************************************
def JSON_load(args):
    args = sys.argv
    fd = open(args[1], mode='r')
    j_data = json.load(fd)
    fd.close()
    ip = j_data["ip"]
    user = j_data["user"]
    password = j_data["password"]
    dst_dir = j_data["dst_dir"]
    local_dir = j_data["local_dir"]
    limit_time = j_data["limit_time"]
    limit_time = datetime.datetime.strptime(limit_time,"%Y-%m-%d %H:%M:%S")
    json_name = args[1]
    return(ip,user,password,dst_dir,local_dir,limit_time,j_data,json_name)
#********** 戻り値：FTPサーバの接続情報（IPアドレス、ユーザー名、パスワード等）*************
#**************************************************************************************




#**************************************************************************************
#*******************************FTPサーバー接続*****************************************
#**************************************************************************************
def FTP_connect(ip,user,password):
    try:
        return ftplib.FTP(ip,user,password,21,500)
    except:
        return()
#**************************************************************************************
#**************************************************************************************




#**************************************************************************************
#**********************対象フォルダのファイル一覧を作成**********************************
#**************************************************************************************
def FTP_getfilelist(ftp,dst_dir,local_dir,limit_time):

    try:
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)
        else:
            pass
        ftp_file =[]
        ftp.cwd(dst_dir)
        logger.debug(" FTP接続成功")
        
        logger.debug(" "+str(limit_time) + " 以降のデータを取得")       
        ftp.dir('./',ftp_file.append)
        return ftp_file
    except:
        logger.exception("FTP接続失敗")
        try:
            ftp.close()
        except:
            pass
        return()
#**************************************************************************************
#**************************************************************************************




#**************************************************************************************
#**********************ファイルの更新日時をAM/PM →→→ 24h表記へ変更***********************
#**************************************************************************************
def FTP_filetimechange(line):
    tokens = line.encode('Latin-1').decode('utf-8').split(maxsplit = 9)
    filename = tokens[-1]
    time_ampm = tokens[1] 
    # AM/PM表示を24時間表示に変更
    # 0時がAM12:00と表示されるため0:00に修正
    if "PM" in time_ampm:
        kousin_time = datetime.datetime.strptime(tokens[0]+' '+tokens[1], '%m-%d-%y %H:%M%p') + datetime.timedelta(hours=12)
    elif "AM" and "12" in time_ampm:
        kousin_time = datetime.datetime.strptime(tokens[0]+' '+tokens[1], '%m-%d-%y %H:%M%p') - datetime.timedelta(hours=12)
    else:
        kousin_time = datetime.datetime.strptime(tokens[0]+' '+tokens[1], '%m-%d-%y %H:%M%p')
    return(filename,kousin_time)
#**************************************************************************************
#**************************************************************************************




#**************************************************************************************
#**************limit_timeより更新時間が新しければファイルをダウンロード*******************
#**************************************************************************************
def FTP_getfiles(filename,kousin_time,ftp,limit_time,dst_dir,local_dir):
    file_kousin=[]
    if kousin_time > limit_time:
        dst_file_path = os.path.join(dst_dir,filename)
        file_localpath = os.path.join(local_dir,filename)
        file_kousin.append(kousin_time)
        with open(file_localpath, 'wb') as download_f: #ローカルパス
            ftp.retrbinary('RETR %s' % dst_file_path, download_f.write)
            logger.debug(" Downloaded files: [" +filename + "]["+ str(kousin_time) +"]")
            file_kousin =kousin_time 
    else:
        pass
    return(file_kousin)
#************************************************************************************** 
#**************************************************************************************
    
    


#**************************************************************************************
#***************************JSONファイルのlimit_timeを更新*******************************
#**************************************************************************************
def json_change_time(file_kousin,j_data,json_name):
    j_data["limit_time"] = file_kousin
    logger.debug(" 取得したファイルの中で最も遅い更新日時:" + j_data["limit_time"])
    with open(json_name, mode='wt', encoding='utf-8') as file:
        json.dump(j_data, file, ensure_ascii=False, indent=2)
        logger.debug(" jsonファイル'limit_time':" + j_data["limit_time"] + " に変更")
#**************************************************************************************
#**************************************************************************************




#**************************************************************************************
#***************************CSVファイル名に現在時刻を付加*******************************
# **********************STS  ALMはファイル名に日時がないため付与***********************
def filename_change(local_dir,filename):
    try:
        filepath = local_dir + "/"+ filename
        filepath_noncsv = os.path.splitext(os.path.basename(filepath))[0]
        file_name = filepath_noncsv + ".CSV"
        if   "ALM" in filename or "STS" in filename:
            str_now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")     
            new_filepath = local_dir + "/"+ filepath_noncsv +"_"+str_now+ ".CSV"
            new_filename = filepath_noncsv +"_"+str_now+ ".CSV"
            os.rename(filepath,new_filepath)
            logger.debug(" ファイル名変更:"+ new_filepath)
            print(new_filepath,new_filename)
            return(new_filepath,new_filename)
        else:
            return(filepath,file_name)
    except:
        pass
#**************************************************************************************
#**************************************************************************************




#**************************************************************************************
#***************************ファイルを更新時間で月ごとフォルダに格納*********************
#**************************************************************************************
def file_move(local_dir,file_dir,kousin_time,new_file_name):
    try:
        # print(kousin_time)
        dir_name = str(kousin_time)[0:4]+str(kousin_time)[5:7]
        dir_name =local_dir +"/"+ dir_name 
        os.makedirs(dir_name, exist_ok=True)
        #moveの2番目の引数をフルパスにして上書き可に
        shutil.move(file_dir,dir_name+"/"+new_file_name)
    except:
        pass
#**************************************************************************************
#**************************************************************************************




#**************************************************************************************
#******************************main処理************************************************
#**************************************************************************************
def main(config_path):
    logger.debug("----------------------------処理開始-----------------------------------")
    ip,user,password,dst_dir,local_dir,limit_time,j_data,json_name = JSON_load(config_path)
    logger.debug(" "+ dst_dir+" のデータ取得開始")
    ftp = FTP_connect(ip,user,password,)
    ftp_file_list = FTP_getfilelist(ftp,dst_dir,local_dir,limit_time)
    fileupdate_time =[]
    for line in ftp_file_list:
        filename,kousin_time =FTP_filetimechange(line)
        file_kousin_1 = FTP_getfiles(filename,kousin_time,ftp,limit_time,dst_dir,local_dir)
        try:
            file_dir,new_file_name = filename_change(local_dir,filename)
            file_move(local_dir,file_dir,kousin_time,new_file_name)
        except:
            pass    
        if file_kousin_1:

            file_kousin_1 = file_kousin_1.strftime('%Y-%m-%d %H:%M:%S')
            fileupdate_time.append(file_kousin_1)
        else:
            pass
       
    if fileupdate_time:
        fileupdate_time = max(fileupdate_time)
        json_change_time(fileupdate_time,j_data,json_name)
    else:
        logger.debug("ファイルダウンロード数 0 ")
        logger.exception("エラーorファイルダウンロード数 0 ")
    logger.debug("----------------------------終了-----------------------------------")    
    ftp.close()
    
#**************************************************************************************
#**************************************************************************************




if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('config', default=path_join('.', 'config', 'config.json'), help='config file path (./config/*.json)')
    # 引数の解析
    args = arg_parser.parse_args()
    config_path = args.config
    if config_path is not None:
        # main処理
        main(config_path)