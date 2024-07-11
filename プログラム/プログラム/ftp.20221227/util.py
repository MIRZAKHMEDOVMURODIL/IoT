import os
import sys
import datetime
import shutil
import importlib
import pathlib
import json
import re
import os
import platform
import posixpath
import ntpath
from glob import glob
from enum import Enum
from logging import Logger, getLogger

CURRENT_DIR = os.path.abspath('./')

class ParameterError(Exception):
    '''
    設定ファイルのパラメータ、引数の不足時のエラー
    '''

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


def beautify_path(path):
    return path.replace('/', os.sep)


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


if __name__ == "__main__":
    times = get_file_timestamps('./')
    latest_time = latest_timestamps('./')

# def log(name, parent_name='main'):
#     def decorator(f):
#         def wrapper(*args, **kwargs):
#             f(*args, logger= getLogger(parent_name).getChild(name), **kwargs)
#         return wrapper
#     return decorator