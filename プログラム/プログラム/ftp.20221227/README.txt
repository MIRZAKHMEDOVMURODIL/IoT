仕様書

#システム概要

　装置からのデータ収集作業を自動化し、データ活用を推進することを目的とする。各装置はkeyence製のPLCで制御されている。稼働ログデータは各PLCにマウントされているSDカードに書き込まれている。収集ツールでは、各装置から直接データを吸い上げるのではなく、SDカードに書き出されたデータのみを抽出する

　SDカードからデータを転送する方法について、FTPを利用したファイル転送を用いる。FTPクライアントには、大東生産技術で開発したPythonプログラムを用いる。Pythonプログラムでは、SDカード内のファイル情報をもとに前回収集時からの差分データが存在する場合のみ、取得処理を行う。

　Pythonプログラムを実行する環境は、Interface社製のLinux端末を使用する。OSはDebian9.3であり、バックアップツール実装時にはSSH等のリモートアクセスにて実装する。

　各装置から転送されたファイルは仮想サーバ内に一時的に蓄えられる。蓄えられたファイルは、データ格納用のNASに送る。NASにファイルを送る方法について、NASに構築した共有フォルダを仮想サーバ側でマウントし、ファイルコピーにてバックアップファイルを作成する。ファイルの最終更新日時を確認し、差分ファイルのみがコピーされる。仮想サーバ内の一時ファイルは毎日23:50に削除される。


# 作業環境
## OS
Debian 9.3

## ログイン情報
ID: admin
PW: kyocera00
ディレクトリパス: /IoT/ftp

## ディレクトリ構成
|-config // 設定ファイル
  |-FTP_*_config.json: 設定ファイル(1ディレクトリに対して1ファイル作成)
|-tmp // FTPで転送されてきたファイルを一時保存する
  |-FV04901
  |-FV04902
  |-FV05701
|-log // ログファイル
  |-cron.log: FTPによるファイル転送処理(GetData.sh)をクーロンで実行した際のログ(最終更新内容のみ)
  |-mount.log: 共有フォルダをマウントした際のログ(最終更新内容のみ)
  |-remove.log: 一時ファイルを削除した際のログ(最終更新内容のみ)
  |-debug.log: FTPMagnager.pyを実行した際のDEBUGレベルまでのログ(70,000行まで追記)
  |-debug.log.*: 指定容量を超えてdebu.logが書き込まれた際の余剰書き出し先(デフォルトでは2ファイル分まで保存)
  |-error.log: FTPMagnager.pyを実行した際のERRORレベルまでのログ(70,000行まで追記)
|-mnt // 共有フォルダのマウント先
|-FTPMagnager.py: FTPを用いて、設定ファイルで記述した内容にもとづき、ファイル転送処理を実行
|-GetData.sh: configディレクトリ内の設定情報にもとづき、FTPMagnager.pyをまとめて実行するシェルスクリプト
|-MountSH.sh: 共有フォルダのマウントを実行するシェルスクリプト
|-RemoveFiles.sh: 一時フォルダ(./tmp)内のファイルを削除するシェルスクリプト

## タスク
毎日00:00 GetData.sh実行(FTPを用いて、装置からファイルを取得)
毎日00:10 sudo権限でMountSH.sh実行(FTPで取得したファイルを共有フォルダへコピー)
毎日23:50 sudo権限でRemoveFiles.sh実行

# 処理フロー
## FTPファイル取得フロー
1. 設定ファイルを引数にFTPMagnager.pyをPython3にて実行
2. 指定アドレスにFTPで接続
3. FTP接続先の指定ディレクトリ直下のファイル群に対して、拡張子および最終更新履歴をもとに条件検索
4. 条件を満たすファイル群のパス情報を取得
5, 1ファイルずつFTPにてダウンロード処理を実行
6. ダウンロードされたファイルはtmp直下の指定ディレクトリへ格納する。
7. 格納する際に、同一名のファイルの衝突を避けるために、元のファイル名と拡張子の間に最終更新日時を挿入する。元が同じファイルでも更新日時が異なる物は別ファイルとなる。
8. 条件を満たすファイルがすべてダウンロードされた場合終了

## 共有フォルダへのバックアップ処理
1. mountコマンドにて共有フォルダをマウント
2. tmpディレクトリのファイルと共有フォルダのファイルを比較し、差分ファイルが存在すれば共有フォルダへファイルをコピーする
3. umountコマンドにて共有フォルダのマウントを解除する

## 一時ファイルの削除
1. rmコマンドにて再帰的にtmpディレクトリ内のファイルを削除


# FTPMagnager
## 依存関係
- python-dateutil: FTP接続先における最終更新日時をファイル情報からパースして解釈する際に使用

## 実行コマンド
python3 FTPMagnager.py [設定ファイルパス]

## 関数名
### execute(): FTPを用いたファイルの送受信処理の実行
### get_ftp_file_list(): FTP接続先のファイル一覧の取得
### download_ftp_files(): FTP経由でファイルのダウンロード処理

## 設定ファイル(json)
'''
{
    "allow_remove": <boolean> 一時ファイルを削除する,
    "command": <str> 原則"ftp",
    "dst_dir": <str> FTP接続先のディレクトリパス,
    "exts": <str[]> 取得するファイルの拡張子,
    "ip": <str> 接続先IPアドレス,
    "limit_time": <str> 更新日時の閾値,
    "local_dir": <str> 一時フォルダに格納するサブディレクトリ名,
    "method": <str> "download"/"upload",
    "os_type": <str> 実行するOS,
    "password": <str> FTP接続先のログインパスワード,
    "suffix": <str> サフィックスに追加する文字列,
    "suffix_type": <str> "none"/"date",
    "updated": <boolean> true,
    "user": <str> FTP接続時のログインID
}
'''


#装置情報
ID: Admin
PW: kyocera
アドレス: 10.23.45.126
ディレクトリパス: ['/FV04901/', '/FV04902/', '/FV05801/]
対象ファイル形式: CSV

# 共有フォルダ
## ログイン情報
パス: //10.21.32.70/DbStrage$
ドメイン: SHGCERLDS02
ユーザ名: DBCOLL01
パスワード: CeraColl1u

## ディレクトリ構成
data
|-FV04901
|-FV04902
|-FV05701

# 作業履歴
'''
cd ~/
mkdir ftp
cd ftp

# Proxy設定(環境変数)
export http_proxy="http://{proxy server}"
export http_proxy="http://{proxy server}"
export https_proxy="http://{proxy server}"

# Proxy設定(apt)
# Ubuntu 18.04では必要
sudo vim /etc/apt/apt.conf
Acquire::http::proxy "http://{proxy server}";
Acquire::https::proxy "http://{proxy server}";

# pipインストール
sudo apt update
sudo apt install python3-pip --fix-missing

# 依存モジュールインストール
pip3 install python-dateutil

# プログラム実行
mkdir log
mkdir tmp
mkdir config

# 印刷機からのファイル取得（動作確認）
python3 FTPManager.py config/FTP_printer_log1_config.json
python3 FTPManager.py config/FTP_printer_log2_config.json
python3 FTPManager.py config/FTP_printer_log3_config.json
python3 FTPManager.py config/FTP_printer_log4_config.json
python3 FTPManager.py config/FTP_printer_log5_config.json

# SPS積層機からのファイル取得（動作確認）
python3 FTPManager.py config/FTP_SPS_log1_config.json
python3 FTPManager.py config/FTP_SPS_log2_config.json
python3 FTPManager.py config/FTP_SPS_log3_config.json
python3 FTPManager.py config/FTP_SPS_log4_config.json
python3 FTPManager.py config/FTP_SPS_log5_config.json
python3 FTPManager.py config/FTP_SPS_log6_config.json
python3 FTPManager.py config/FTP_SPS_log7_config.json

# FTPによるファイル取得スクリプトの確認
chmod 777 GetData.sh
bash GetData.sh

# 共有フォルダのマウントとファイルコピー処理スクリプトの確認
chmod 777 MountSH.sh
sudo bash MountSH.sh

# 一時ファイル削除処理スクリプトの確認
chmod 777 RemoveFiles.sh
sudo bash RemoveFiles.sh

# cronの登録
crontab iot_cron
sudo crontab mount_cron

# Proxy設定解除(apt)
sudo rm /etc/apt/apt.conf
sudo touch /etc/apt/apt.conf
'''