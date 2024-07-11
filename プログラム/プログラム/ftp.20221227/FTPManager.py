'''
REQUIREMENT PIP MODULE

REQUIREMENT ORIGINAL MODULE
- util.py
'''
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
from ftplib import FTP, all_errors
from dateutil import parser
from glob import glob
from enum import Enum
from logging import getLogger, StreamHandler, ERROR, DEBUG, Formatter
from logging.handlers import RotatingFileHandler

'''
utility functions
'''
CURRENT_DIR = os.path.abspath('./')

class ExEnum(Enum):
    @classmethod
    def keys(cls):
        return [k for k, v in cls.__members__.items()]

    @classmethod
    def values(cls):
        return [v.value for k, v in cls.__members__.items()]


def path_join(*args, os = None):
    os = os if os else platform.system()
    if os == 'windows':
        return ntpath.join(*args)
    else:
        return posixpath.join(*args)



def add_suffix(name, suffix_type, suffix = '', date_format="%Y%m%d%H%M%S"):
    if suffix_type == 'none':
        return name

    suffix_name = suffix
    tmp = os.path.splitext(name)
    if len(tmp) <= 0:
        return name

    basename = tmp[0]
    extension = tmp[1]

    if suffix_name is None:
    # if (suffix_type == 'script') or (suffix_type == 'date'):
        suffix_name = datetime.datetime.now().strftime(date_format)
    filename = '_'.join([basename, suffix_name])+extension

    return filename


def get_file_timestamps(dirname, exts = ['csv', 'txt', 'tsv']):
    return [
        # os.path.basename(file if len(file.split('.')) > 1 else file+'.dummy').split('.')[1]
        datetime.datetime.fromtimestamp(pathlib.Path(path_join(dirname, file)).stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S") 
        for file in os.listdir(dirname) 
        if (file if len(file.split('.')) > 1 else file+'.dummy').split('.')[1] in exts
    ]


def latest_timestamps(dirname, exts = ['csv', 'txt', 'tsv']):
    tmp = get_file_timestamps(dirname, exts)
    return max(tmp) if len(tmp) > 0 else None



'''
FTP エラー定義
'''
class ConfigError(Exception):
    '''
    設定ファイルの読み書きに失敗した際のエラー
    '''


class FTPError(Exception):
    '''
    FTP処理のエラー
    '''


class MethodError(Exception):
    '''
    FTPコマンド内のmethodの設定が間違っていた場合のエラー
    '''


class MethodType(ExEnum):
    '''
    methodの一覧（Enum文字列型）
    '''
    DOWNLOAD = 'download'
    UPLOAD = 'upload'


'''
FTP接続処理
'''
def connect_ftp(logger, ip, user, password, **kwargs):
    '''
    FTPインスタンスの生成
    FTPに接続する際の最初に行う処理。
    @param logger: ロガー
    @param ip str: 接続先のIPアドレス
    @param user str: ログインユーザ名
    @param password str: ログインパスワード
    '''
    logger.debug("trying to connect: {ip}, {user}, {password}".format(ip=ip, user=user, password=password))
    return FTP(ip, user, password, 21, 500)


def parse_latest_file_list(lines, logger, exts, limit_time, updated=True, timedelta=0, **kwargs):
    '''
    FTP のLISTコマンド(ftplib.dirに相当)で取得した結果から、指定の更新日時より後に更新されたファイルの一覧を取得する。
    ftplib.dir()の出力形式に準拠
    @param line 
    @ret {name: "ファイル名", date: "更新日時"} 
    '''
    try:
        limit_date = parser.parse(limit_time)
        # limit_date = datetime.datetime.strptime(limit_date, '%Y-%m-%d %H:%M:%S')
        files = []
        logger.debug('limit time:'+limit_time)
        for line in lines:
            # 文字コードの変換
            tokens = line.encode('Latin-1').decode('utf-8').split(maxsplit = 9)
            # logger.debug("file: {li}".format(li=tokens))
            # ディレクトリ以外を参照
            if tokens[0][0] is not "d":
                # token[5]: 月, token[6]: 日, token[7]: 年
                time_str = datetime.datetime.strptime(tokens[0]+' '+tokens[1], '%m-%d-%y %I:%M%p').strftime('%Y-%m-%d %H:%M:%S')
                # time_str = tokens[5] + " " + tokens[6] + " " + tokens[7]
                time = parser.parse(time_str)
                # 指定日時より後に更新されたファイルのみを追加
                filename = tokens[3]
                if os.path.basename(filename).split('.')[1] in exts:
                    if updated:
                        if time > (limit_date - datetime.timedelta(days=timedelta)):
                            logger.debug("append: {up}, {name}, {time}, {limit}, {flag}".format(up=updated, name=filename, time=time, limit=limit_date, flag=(time > limit_date)))
                            files.append({"name": filename, "time": time.strftime("%Y%m%d%H%M%S") })
                    else:
                        logger.debug("append: {up}, {name}, {time}, {limit}".format(up=updated, name=filename, time=time, limit=limit_time))
                        files.append({"name": filename, "time": time.strftime("%Y%m%d%H%M%S") })
        logger.debug('Num of updated files: {num}'.format(num=len(files)))
        return files
    except UnicodeDecodeError as e:
        raise UnicodeDecodeError('decode error at parsing dirname: %e' % e)
    except IndexError as e:
        raise IndexError('cannot get file list following datetime format')


def get_ftp_file_list(logger, dst_dir = './', limit_time='Jan 1 1000', exts=[], **kwargs):
    '''
    更新されたファイルのみを取得する
    @param logger:　ロガー
    @param dst_dir str: 接続先のディレクトリ
    @param exts [str]: 取得したいファイルの拡張子
    @param limit_time str: 更新日時の閾値（日付形式に準拠）
    '''
    try:
        with connect_ftp(logger=logger, **kwargs) as ftp:
            ftp.cwd(dst_dir)
            ftp_file_list = []
            # ファイル一覧の取得
            ftp.dir('./', ftp_file_list.append)
            # 更新日時が新しいファイルのみを検索
            files = parse_latest_file_list(ftp_file_list, logger=logger, limit_time=limit_time, exts=exts, **kwargs)
            if len(files) <= 0:
                logger.debug('There is no updated file')
            return files
    except all_errors as e:
        raise FTPError('failed to get file list')
        ftp.close()
        return []


def download_ftp_files(logger, dst_dir, local_dir, os_type, suffix_type, suffix, encoding='utf-8', allow_remove = False, **kwargs):
    '''
    FTP経由でファイルをダウンロードする処理
    update
    ファイルが指定されている場合は、指定ファイルのみをダウンロード
    ファイルが指定されていない場合は、該当ディレクトリのファイル全体を対象
    @param logger: ロガー
    @param dst_dir str: 指定先のディレクトリ
    @param local_dir: ローカルに保存するディレクトリ名
    @param os str: 接続先のOS、パスの生成時に必要
    '''
    try:
        # FTPサーバへ接続
        ftp = connect_ftp(logger=logger, **kwargs)
        logger.debug('download file with ftp')
        # 接続先のファイルの一覧
        dl_files = get_ftp_file_list(logger=logger, dst_dir=dst_dir, **kwargs)
        dl_files = [(os.path.basename(f.get('name')), f.get('time')) for f in dl_files]
        logger.debug('downloaded files: {f}'.format(f=dl_files))

        if len(dl_files) > 0:
            if allow_remove:
                shutil.rmtree(local_dir)
                os.mkdir(local_dir)


        for dl_file, time in dl_files:
            # 接続先のファイルのパス
            dst_file_path = path_join(dst_dir, dl_file)
            local_dir = local_dir if local_dir != '' else path_join(CURRENT_DIR, 'tmp') 
            # ローカルのファイルのパス
            suffix = time
            filename = add_suffix(dl_file, suffix_type=suffix_type, suffix=suffix)
            local_file_path = path_join(local_dir, filename)
            # ローカルに保存するファイルへのアクセス
            with open(local_file_path, 'wb') as download_f: #ローカルパス
                # ダウンロード処理
                ftp.retrbinary('RETR '+dst_file_path, download_f.write)
                logger.debug('success data download')
    except IOError as e:
        logger.error('IOError file cannot read or write' % e)
        raise FTPError('fail to save files')
    except all_errors as e:
        logger.error("failed to download file with ftp: % e" % e)
        ftp.close()
        raise FTPError('fail to download files')


def upload_ftp_file(logger, dst_dir, local_dir, local_file_name, updated, exts, os_type, **kwargs):
    '''
    FTPでのファイルのアップロード
    '''
    ftp = connect_ftp(logger=logger, **kwargs)
    local_file_path = path_join(local_dir, os.path.basename(local_file_name))
    ftp.cwd(dst_dir)
    logger.debug('local file upload')
    with open(local_file_path, 'rb') as f:
        ftp.storbinary("STOR "+os.path.basename(local_file_path), f)
        logger.debug('FTP upload success')


def upload_ftp_files(logger, dst_dir, local_dir, updated, exts, limit_time, **kwargs):
    '''
    FTPでの複数ファイルのアップロード
    '''
    logger.debug('ftp upload files')
    file_list = []
    for ext in exts:
        local_path = path_join(local_dir, '*.'+ext)
        tmp_file_list = glob(local_path)
        if updated:
            for f in tmp_file_list:
                if parser.parse(datetime.datetime.fromtimestamp(os.stat(f).st_ctime).strftime("%Y/%m/%d %H:%M:%S")) > parser.parse(limit_time):
                    file_list.append(f)
    logger.debug('file size: {n}'.format(n=len(file_list)))
    for f in file_list:
        logger.debug('upload file name: {n}'.format(n=f))
        upload_ftp_file(logger=logger, local_dir=local_dir, local_file_name=f, dst_dir=dst_dir, updated=updated, exts=exts, **kwargs)
    logger.debug('tmp file remove {fs}'.format(fs=len(glob(local_dir))))


def execute(method, logger, local_dir, **kwargs):
    '''
    FTP コマンドの実行
    @param method string: FTPで実行したい内容
        - download: ファイルのダウンロード
        - upload: ファイルのアップロード
    '''
    logger.debug('method type is {method}'.format(method=method))
    if method is None:
        raise MethodError('Method type is null')
    elif method == MethodType.DOWNLOAD.value:
        download_ftp_files(logger=logger, local_dir=local_dir, **kwargs)
    elif method == MethodType.UPLOAD.value:
        upload_ftp_files(logger=logger, local_dir=local_dir, **kwargs)
    else:
        raise MethodError('undefined method type: {m}'.format(m=method))
    return latest_timestamps(path_join(local_dir))

def main(config_path, execute_time = None):
    stream_handler = StreamHandler()
    stream_handler.setLevel(DEBUG)
    stream_handler_format = Formatter('%(asctime)s -%(name)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(stream_handler_format)

    # debug_file_handlerの生成
    debug_file_handler = RotatingFileHandler(path_join('.', 'log', 'debug.log'), maxBytes=5*1024*1024, backupCount=2)
    debug_file_handler.setLevel(DEBUG)
    debug_file_handler_format = Formatter('%(asctime)s -%(name)s - %(levelname)s - %(message)s')
    debug_file_handler.setFormatter(debug_file_handler_format)

    # error_file_handlerの生成
    error_file_handler = RotatingFileHandler(path_join('.', 'log', 'error.log'), maxBytes=5*1024*1024, backupCount=2)
    error_file_handler.setLevel(ERROR)
    error_file_handler_format = Formatter('%(asctime)s -%(name)s - %(levelname)s - %(message)s')
    error_file_handler.setFormatter(error_file_handler_format)

    # loggerオブジェクトとhandlerオブジェクトの紐づけ
    logger = getLogger('ftp')
    logger.setLevel(DEBUG)
    logger.addHandler(stream_handler)
    logger.addHandler(debug_file_handler)
    logger.addHandler(error_file_handler)
    logger.propagate = False

    logger.debug('Debug Start')
    logger.debug('FTP Process Start')
    logger.debug('File: {file}'.format(file=__file__))
    logger.debug('System: {sys}'.format(sys=sys.version))
    logger.debug('config: {config}'.format(config=config_path))
    logger.debug('shell exe time: {exet}'.format(exet=execute_time))

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

            # コマンドの確認
            ori_local = config.get('local_dir')
            local_dir = './tmp/' + config.get('local_dir')
            if not os.path.exists(local_dir):
                logger.error('path not exist')
                os.makedirs(local_dir, exist_ok=True)
            config['local_dir'] = local_dir

            # if config.get('suffix_type') == 'shell' and execute_time is not None:
            ori_suffix = config.get('suffix')
            ori_suffix = ori_suffix if ori_suffix is not None else ''
            if execute_time is not None:
                config['suffix'] = (ori_suffix +'_' if ori_suffix is not None else '') + execute_time
            # コールバック関数に設定パラメータに加えてロガー、引継ぎデータ、更新日時の閾値を追加
            config['logger'] = logger
            execute(**config)
            config['local_dir'] = ori_local
            del config['logger']
            exts = config.get('exts')
            timestamp = latest_timestamps(local_dir, exts)
            timestamp = timestamp if timestamp is not None else config['limit_time']
            logger.debug('latest updated time: {t}'.format(t=timestamp))
            config['limit_time'] = timestamp
            config['suffix'] = ori_suffix
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
                logger.debug('success save config file')
    except Exception as e :
        logger.error('undefined error {err}'.format(err=e))
    logger.debug('Process End')



if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('config', default=path_join('.', 'config', 'config.json'), help='config file path (./config/*.json)')
    arg_parser.add_argument('-t', '--time')

    # コマンドライン引数の解析
    args = arg_parser.parse_args()
    config_path = args.config
    execute_time = args.time
    if config_path is not None:
        main(config_path, execute_time)