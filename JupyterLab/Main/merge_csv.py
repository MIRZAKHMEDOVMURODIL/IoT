import pandas as pd
import smtplib
import datetime
from email.mime.text import MIMEText
import logging
import logging.handlers
from dateutil.relativedelta import relativedelta
import csv



logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
#file_handler = logging.FileHandler("C:\ub_work\02_theme_master\03_mergecsv/merge_csv.log")
file_handler = logging.handlers.RotatingFileHandler("C:/ub_work/02_theme_master/03_mergecsv/merge_csv.log", maxBytes=1*1024*1024, backupCount=5)
file_handler.setLevel(logging.DEBUG)
file_handler_format = logging.Formatter('%(asctime)s : %(levelname)s - %(message)s')
file_handler.setFormatter(file_handler_format)
file_handler.setFormatter(file_handler_format)
logger.addHandler(file_handler)

logger.info('Process Start.')

# UBからエクスポートしたテーママスタを辞書形式で読み込む
ub_themefile = 'C:/ub_work/02_theme_master/01_export/ubexport_thememaster.csv'
dict_ub_theme = pd.read_csv(ub_themefile, index_col=0, encoding='cp932').to_dict(orient='index')

#print(dict_ub_theme)

# 02_editcsvで作成したconcat.csvを読み込む
concat_file = 'C:/ub_work/02_theme_master/02_editcsv/concat.csv'
concat_list = pd.read_csv(concat_file, encoding='cp932').values.tolist()


for cl in concat_list:
    #print(cl)
    themecd = cl[0]

    if themecd in dict_ub_theme.keys():
        dict_val = dict_ub_theme[themecd]
        #print(dict_val)
        # テーマコードがすでに存在（更新）
        #if pd.isnull(dict_val['最終決裁完了日時']) or datetime.datetime.strptime(dict_val['最終決裁完了日時'],'%Y/%m/%d %H:%M:%S') < datetime.datetime.strptime(cl[19],'%Y/%m/%d %H:%M:%S'):
        if pd.isnull(dict_val['最終決裁完了日時']) or dict_val['最終決裁完了日時'] < cl[19]:
            # 決裁完了日が未入力 または 更新されている場合、他の項目の値を更新
            logger.debug('Update. themecd:' + themecd + ', 最終決裁完了日時: ' + str(dict_val['最終決裁完了日時']) + ', 決裁完了日: ' + str(cl[19]))
            
            dict_val['テーマ名'] = cl[1]
            dict_val['前テーマコード'] = cl[3]
            dict_val['MP登録用仮テーマCD'] = cl[4]
            dict_val['テーマリーダー'] = cl[5]
            dict_val['テーマリーダー社員No'] = cl[5]
            dict_val['テーマリーダー部署コード'] = cl[6]
            dict_val['テーマリーダー部署名'] = cl[7]
            dict_val['テーマ区分'] = cl[8]
            dict_val['プロダクトライン'] = cl[9]
            dict_val['依頼元 事業部'] = cl[10]
            dict_val['4象限区分'] = cl[11]
            dict_val['開発活動ステータス'] = cl[12]
            dict_val['開始日'] = cl[13]
            dict_val['完了予定日'] = cl[14]
            dict_val['完了/中止/中断日'] = cl[15]
            dict_val['抹消日'] = cl[16]
            dict_val['税前貢献 開始年月'] = cl[17]
            dict_val['税前貢献 終了年月'] = cl[18]
            dict_val['最終決裁完了日時'] = cl[19]

            # 更新
            dict_ub_theme[themecd]=dict_val

        else:
            # 決裁完了日が更新されていないので、何もしない
            logger.debug('Skip.   themecd:' + themecd + ', 最終決裁完了日時: ' + str(dict_val['最終決裁完了日時']) + ', 決裁完了日: ' + str(cl[19]))            

    else:
        # テーマコードが存在していない（新規）
        logger.debug('New.    themecd:' + themecd + ', 決裁完了日: ' + str(cl[19]))

        dict_val={}
        
        dict_val['開発コード'] = cl[2]

        dict_val['テーマ名'] = cl[1]
        dict_val['前テーマコード'] = cl[3]
        dict_val['MP登録用仮テーマCD'] = cl[4]
        dict_val['テーマリーダー'] = cl[5]
        dict_val['テーマリーダー社員No'] = cl[5]
        dict_val['テーマリーダー部署コード'] = cl[6]
        dict_val['テーマリーダー部署名'] = cl[7]
        dict_val['テーマ区分'] = cl[8]
        dict_val['プロダクトライン'] = cl[9]
        dict_val['依頼元 事業部'] = cl[10]
        dict_val['4象限区分'] = cl[11]
        dict_val['開発活動ステータス'] = cl[12]
        dict_val['開始日'] = cl[13]
        dict_val['完了予定日'] = cl[14]
        dict_val['完了/中止/中断日'] = cl[15]
        dict_val['抹消日'] = cl[16]
        dict_val['税前貢献 開始年月'] = cl[17]
        dict_val['税前貢献 終了年月'] = cl[18]
        dict_val['最終決裁完了日時'] = cl[19]

        # 新規
        dict_ub_theme[themecd]=dict_val        
        
df1=pd.DataFrame(dict_ub_theme.keys(),columns=['テーマコード'])
df2=pd.json_normalize(dict_ub_theme.values())
# indexをキーに結合
df=df1.join(df2)
print(df)
# CSV出力
csv_path = 'C:/ub_work/02_theme_master/03_mergecsv/theme_master.csv'
df.to_csv(csv_path, index=False, encoding='cp932')




logger.info('Process End.')


