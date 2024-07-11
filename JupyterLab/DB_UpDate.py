#!/usr/bin/env python
# coding: utf-8

# In[13]:


import csv
import logging
import sqlite3
import pprint
import pyodbc
import pandas as pd
from datetime import datetime
import numpy as np


sql= """ MERGE theme_master 
        USING ( SELECT ? AS themeCD, ? AS theme, ? AS managerID, ? AS manager, ? AS product_line,  ? AS jigyobu,  ? AS officeCD,  ? AS office,  ? AS divisionCD, ? AS division,  ? AS reg_date,  ? AS comp_date,  ? AS kouken_date_from,  ? AS kouken_date_to,  ? AS del_date,  ? AS kubun,  ? AS devCD,  ? AS memo,  ? AS action_status,  ? AS comp_result_date,  ? AS four_quadrant 
        ) AS CSV 
        ON (theme_master.themeCD = CSV.themeCD)

        WHEN MATCHED THEN
        
              UPDATE SET
              
                    theme_master.theme = CSV.theme,
                    theme_master.managerID = CSV.managerID,
                    theme_master.manager = CSV.manager,
                    theme_master.product_line = CSV.product_line,
                    theme_master.jigyobu = CSV.jigyobu,
                    theme_master.officeCD = CSV.officeCD,
                    theme_master.office = CSV.office,
                    theme_master.divisionCD = CSV.divisionCD,
                    theme_master.division = CSV.division,
                    theme_master.reg_date = CSV.reg_date,
                    theme_master.comp_date = CSV.comp_date,
                    theme_master.kouken_date_from = CSV.kouken_date_from,
                    theme_master.kouken_date_to = CSV.kouken_date_to,
                    theme_master.del_date = CSV.del_date,
                    theme_master.kubun = CSV.kubun,
                    theme_master.devCD = CSV.devCD,
                    theme_master.memo = CSV.memo,
                    theme_master.action_status = CSV.action_status ,
                    theme_master.comp_result_date = CSV.comp_result_date,
                    theme_master.four_quadrant = CSV.four_quadrant      
                    
        WHEN NOT MATCHED THEN
                                                         
                    INSERT (themeCD, theme, managerID, manager, product_line, jigyobu, officeCD, office, divisionCD, division,
                            reg_date, comp_date, kouken_date_from, kouken_date_to, del_date, kubun, devCD, memo, action_status,
                            comp_result_date, four_quadrant)
                            
                    VALUES (CSV.themeCD, CSV.theme, CSV.managerID, CSV.manager, CSV.product_line, CSV.jigyobu, CSV.officeCD,
                            CSV.office, CSV.divisionCD, CSV.division, CSV.reg_date, CSV.comp_date, CSV.kouken_date_from,
                            CSV.kouken_date_to, CSV.del_date, CSV.kubun, CSV.devCD, CSV.memo, CSV.action_status,
                            CSV.comp_result_date, CSV.four_quadrant);"""

def function_0(data):
    if data is not None:
        if '/' in data:
            a = datetime.strptime(data, '%Y/%m').strftime('%Y%m')
        else:
            a = datetime.strptime(data, '%Y%m').strftime('%Y%m')
    else:
        a = None        
    return a
    
def function_1(data):
    if data is not None:
        a = datetime.strptime(data, '%Y/%m/%d').strftime('%Y%m%d')
    else: 
        a = None
    return a
    
def function_2(data):
    if data is not None:
        a = datetime.strptime(data, '%Y/%m/%d').strftime('%Y%m%d')
    else: 
        a = None
    return a


try:
    driver   = 'SQL Server'
    server   = '10.9.185.19'
    database = 'treasure_test'
    username = 'sa'
    password = 'KyoceraAdmin'
    connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
    connection = pyodbc.connect(connection_string)
    cursor = connection.cursor()
  

    csv_file_path = r"C:\Users\00220401626\Desktop\ubexport_thememaster.csv"
    df = pd.read_csv(csv_file_path, encoding='cp932',dtype= object)
    df.replace([np.nan],[None], inplace=True)
    
    try:
        for index, data in df.iterrows():
            themeCD = data['テーマコード']
            theme = data['テーマ名']
            managerID = data['テーマリーダー']
            manager = data['テーマリーダー（ユーザー名）']
            product_line = data['プロダクトライン']
            jigyobu = data['依頼元 事業部']
            officeCD = data['テーマリーダー部署コード'][:3]
            office = data["テーマリーダー部署コード"]
            divisionCD = data['テーマリーダー部署コード'][3:]
            division = data['テーマリーダー部署名']
            reg_date = function_2(data['開始日'])
            comp_date = function_1(data['完了予定日'])                   
            kouken_date_from = function_0(data['税前貢献 開始年月'])
            kouken_date_to = function_0(data['税前貢献 終了年月']) 
            del_date = function_2(data['抹消日'])
            kubun = data['テーマ区分']
            devCD = data['開発コード']
            memo = data['備考']
            action_status = data['開発活動ステータス']         
            comp_result_date =function_1(data['完了/中止/中断日'])   
            four_quadrant = data['4象限区分']     
            
            cursor.execute(sql, ( themeCD, theme, managerID, manager, product_line, jigyobu, officeCD, office, divisionCD, division, reg_date, comp_date, kouken_date_from, kouken_date_to, del_date, kubun, devCD, memo, action_status, comp_result_date, four_quadrant))
            connection.commit()
              
    except Exception as b:
        logging.exception(f"An error occurred in {index+1}: {str(b)}") 
        
    finally:
        cursor.close()
        connection.close()
        print('All finished')
        
except Exception as e:
    logging.exception(f"An error occurred during connecting database or the importing data: {str(e)}")     

