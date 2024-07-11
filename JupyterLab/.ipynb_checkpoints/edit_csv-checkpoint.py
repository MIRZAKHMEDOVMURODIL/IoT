import os
import pandas as pd
import smtplib
import datetime
from email.mime.text import MIMEText
import logging
import logging.handlers
from dateutil.relativedelta import relativedelta
import codecs


def recreate_csv(logger, csv_file, file_index):
    logger.info('csv_file: ' + csv_file)
    # CSVファイル読込
    df = pd.read_csv(csv_file,encoding="cp932", dtype=object)

    # 決裁完了日をtimestampへ変換
    df["決裁完了日"] = pd.to_datetime(df["決裁完了日"], format="%Y/%m/%d %H:%M:%S")

    # 決裁状況=承認 で 決済完了日が2023/06/01以降のデータのみ抽出
    #df_aprv = df[df['決裁状況'] == "承認"]
    target_date = datetime.datetime(2023, 6, 1)
    df_aprv = df[(df['決裁状況'] == "承認") & (df['決裁完了日'] > target_date)]

    # テーマコード重複の場合、決裁完了日が遅いデータを残し、それ以外削除 & 必要な列を抽出
    df_aprv_sort = df_aprv.sort_values(by = '決裁完了日', ascending = False)
    df_aprv_sort_ver2 = df_aprv_sort.drop_duplicates(subset=["テーマコード"])
    if file_index=='03':
        # 03:企画書のみ"依頼元 事業部"ではなく"委託元 事業部"
        df_tmp = df_aprv_sort_ver2.reindex(columns=["テーマコード","テーマ名","前テーマコード","MP登録用仮テーマCD"\
        ,"委託元 事業部","開発活動ステータス","テーマリーダー","テーマリーダー社員No","テーマリーダー部署コード","テーマリーダー部署名"\
        ,"4象限区分","テーマ区分","プロダクトライン","開始日","完了予定日","完了/中止/中断 日","開発コード","税前貢献 開始年月","税前貢献 終了年月","決裁完了日"])
        # 列名変更
        df_aprv_sort_ver3 = df_tmp.rename(columns={"委託元 事業部":"依頼元 事業部"})
    else:
        df_aprv_sort_ver3 = df_aprv_sort_ver2.reindex(columns=["テーマコード","テーマ名","前テーマコード","MP登録用仮テーマCD"\
        ,"依頼元 事業部","開発活動ステータス","テーマリーダー","テーマリーダー社員No","テーマリーダー部署コード","テーマリーダー部署名"\
        ,"4象限区分","テーマ区分","プロダクトライン","開始日","完了予定日","完了/中止/中断 日","開発コード","税前貢献 開始年月","税前貢献 終了年月","決裁完了日"])

    # 開発活動ステータスが完了、中止、中断のテーマには決裁完了日+3か月で抹消日を追加する
    d_today = datetime.date.today()
    df_aprv_sort_ver3["抹消日"] = ''
    df_aprv_sort_ver3["抹消日"] = df_aprv_sort_ver3["決裁完了日"].apply(lambda x: x + relativedelta(months=3))
    df_aprv_sort_ver3["抹消日"] = df_aprv_sort_ver3["抹消日"].where((df_aprv_sort_ver3["開発活動ステータス"]=="中止")|(df_aprv_sort_ver3["開発活動ステータス"]=="中断")|(df_aprv_sort_ver3["開発活動ステータス"]=="完了"),"")
    df_aprv_sort_ver3["抹消日"] = df_aprv_sort_ver3["抹消日"].where(df_aprv_sort_ver3["抹消日"] < pd.to_datetime(d_today),"")
    df_aprv_sort_ver3["抹消日"] = df_aprv_sort_ver3["抹消日"].dt.strftime('%Y/%m/%d')
    df_aprv_sort_ver3["決裁完了日"] = df_aprv_sort_ver3["決裁完了日"].dt.strftime('%Y/%m/%d %H:%M:%S')

    # CSV出力
    out_csvpath = "C:/ub_work/02_theme_master/02_editcsv/after_edit" + str(file_index) + ".csv"
    df_aprv_sort_ver3.to_csv(out_csvpath, encoding='cp932', index=False)

    return out_csvpath


def concat_csv(logger, f_list, out_path):
    logger.info('merge_csv() target file count: ' + str(len(f_list)))
    data_list=[]
    for f in f_list:
        logger.debug(str(f))
        try:
            data_list.append(pd.read_csv(f, encoding="cp932", dtype=object))
        except UnicodeDecodeError:
            # Unicode変換エラーが出る場合こちら（encoding=cp932指定してもなぜか出力される）
            #logger.debug('UnicodeDecodeError')
            with codecs.open(f,'r','cp932','ignore') as file:
                data_list.append(pd.read_table(file, delimiter=',', dtype=object))

    df = pd.concat(data_list, axis=0, sort=True)
    order_cols = ['テーマコード','テーマ名','開発コード','前テーマコード','MP登録用仮テーマCD','テーマリーダー社員No','テーマリーダー部署コード','テーマリーダー部署名','テーマ区分','プロダクトライン','依頼元 事業部','4象限区分','開発活動ステータス','開始日','完了予定日','完了/中止/中断 日','抹消日','税前貢献 終了年月','税前貢献 開始年月','決裁完了日']
    df.to_csv(out_path, index=False, encoding="cp932", columns=order_cols)
    


if __name__=="__main__":
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    # logファイルはMAX1MB 5世代まで保存
    #file_handler = logging.FileHandler("C:/ub_work/02_theme_master/02_editcsv/edit_csv.log")
    file_handler = logging.handlers.RotatingFileHandler("C:/ub_work/02_theme_master/02_editcsv/edit_csv.log", maxBytes=1*1024*1024, backupCount=5)
    file_handler.setLevel(logging.DEBUG)
    file_handler_format = logging.Formatter('%(asctime)s : %(levelname)s - %(message)s')
    file_handler.setFormatter(file_handler_format)
    file_handler.setFormatter(file_handler_format)
    logger.addHandler(file_handler)
    
    logger.info('--------- Process Start. ---------')

    # 念のため前回作成したCSVを削除
    concat_csv_file = 'C:/ub_work/02_theme_master/02_editcsv/concat.csv'
    if os.path.isfile(concat_csv_file):
        os.remove(concat_csv_file)

    # UBからエクスポートした01-03のCSVをそれぞれ編集して新規CSVを作成
    file_list=[]
    file_list.append('C:/ub_work/02_theme_master/01_export/ubexport01.csv')     # 01.事前調査申請書
    file_list.append('C:/ub_work/02_theme_master/01_export/ubexport02.csv')     # 02.支援依頼書
    file_list.append('C:/ub_work/02_theme_master/01_export/ubexport03.csv')     # 03.企画書
    #file_list.append('D:/miura_temp_220630/ubexport03.csv')     # 03.企画書
    
    out_filelist=[]
    try:
        f_i = 1
        for f in file_list:
            if os.path.isfile(f):
                out_filelist.append(recreate_csv(logger, f, str(f_i).zfill(2)))
            else:
                logger.debug('csv file is not exist. skip. %s',f)
            f_i +=1

    except Exception as e:
        logger.exception(str(e))

    # 作成した新規CSVを1つのファイルに結合
    if out_filelist == []:
        logger.debug('out_filelist == []. concat csv was not created.')
    else:
        try:
            concat_csv(logger, out_filelist, concat_csv_file)
        except Exception as e:
            logger.exception(str(e))


    logger.info('--------- Process End. ---------')


##    #送受信先
##    to_email = "kei.miura.nf@kyocera.jp"
##    from_email = "kei.miura.nf@kyocera.jp"
##    message = '''
##    UnitBase出力ファイルの処理失敗<br/>
##    下記エラーが発生しました<br/><br/>
##    ''' + str(e)
##    msg = MIMEText(message, "html")
##    msg["Subject"] = "UnitBase出力ファイルの処理失敗"
##    msg["To"] = to_email
##    msg["From"] = from_email
##    # サーバを指定
##    server = smtplib.SMTP("mail.in.kyocera.co.jp",25)
##    # メールを送信
##    server.send_message(msg)
##    # 閉じる
##    server.quit()
