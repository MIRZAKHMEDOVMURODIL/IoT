#!/usr/bin/env python
# coding: utf-8
# In[1]:

#import pylab
import os,sys
import csv
import pandas as pd
import numpy as np
from tkinter import *
import tkinter.filedialog
import tkinter.messagebox
import tkinter.ttk as ttk
import datetime
from dateutil.relativedelta import relativedelta
import collections
import sqlite3
import re
import copy
import openpyxl as px
import pprint
import math
import time
import random
from tqdm import tqdm
import itertools
from scipy.stats import multivariate_normal
#import win32com.client  # ライブラリをインポート
from scipy.optimize import fmin
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import LinearRegression,Lasso,Ridge
from sklearn.neural_network import MLPClassifier
from sklearn.neural_network import MLPRegressor
import xgboost as xgb
import glob
from matplotlib import pyplot as plt
#import umap
from scipy.sparse.csgraph import connected_components
import matplotlib.pyplot as plt
import matplotlib.cm as c
from sklearn import linear_model

#import seaborn as sns
from sklearn import datasets

#import seaborn as sns
## 次元圧縮のアルゴリズム
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.manifold import TSNE
## データセットとデータの操作
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import FactorAnalysis
#from factor_analyzer import FactorAnalyzer
from pandas import plotting
from sklearn.decomposition import FactorAnalysis as FA
from sklearn.ensemble import AdaBoostRegressor
import gc

#__author__ = '' 
if __name__ == "__main__":
    root = Tk()
    root.title('ラッソ分析')
    root.geometry("600x400")
    typ = [('データファイル','*.xlsx;*.csv')]
    fTyp = [("All files","*.*")]
    
#キャンセルボタンの動作定義
    def stop():
        #プログラム終了
        sys.exit()
        

#ラーニングデータファイル読み込みボタンの動作定義#
    def hosei_data():
    	global filename_open
    	dir = 'C:'
    	filename_open = tkinter.filedialog.askopenfilename(filetypes = typ, initialdir = dir)
    	if filename_open != '':
    		lb[1].config(text = filename_open);
    	else:
    		lb[1].config(text = "ファイルはありません");
            
#線形回帰リッジ
    def Linear_Ridge(X_train, y_train, X_test):
    	reg_lr = Ridge(alpha =100)
    	reg_lr.fit(X_train,y_train)
    	#偏回帰係数
    	tfi = reg_lr.coef_
    	train_pred = reg_lr.predict(X_train)
    	
    	test_pred = reg_lr.predict(X_test)
    	return(test_pred,tfi)
    	
#線形回帰ラッソ
    def Linear_Lasso(X_train, y_train, X_test):
        lasso = Lasso(alpha= float(txt2.get()), max_iter=100000).fit(X_train, y_train)
        test_pred = lasso.predict(X_test)
        tfi = lasso.coef_
        #print(f"training dataに対しての精度: {lasso.score(X_train, y_train):.2}")
        #print(f"test set scoreに対しての精度: {lasso.score(X_test, y_test):.2f}")
        #print(f"使われている特徴量の数: {np.sum(lasso.coef_ != 0)}")
        return(test_pred,tfi)
        
#線形回帰リッジ
    def Linear_Ridge(X_train, y_train, X_test):
        ridge = Ridge(alpha= float(txt2.get())).fit(X_train, y_train)
        test_pred = ridge.predict(X_test)
        tfi = ridge.coef_
        #print(f"training dataに対しての精度: {lasso.score(X_train, y_train):.2}")
        #print(f"test set scoreに対しての精度: {lasso.score(X_test, y_test):.2f}")
        #print(f"使われている特徴量の数: {np.sum(lasso.coef_ != 0)}")
        return(test_pred,tfi)
        
#ランダムフォレスト定義
    def R_forest(X_train, y_train, X_test):
    	n_e = int(txt3.get())
    		
    	if str(txt4.get()) == "デフォルト":
    		m_d = None
    	else:
    		m_d = int(txt3.get())
    	reg_rf = RandomForestRegressor(n_estimators=n_e,max_depth = m_d,n_jobs=-1,random_state=1)
    	reg_rf.fit(X_train,y_train)
    	fti = reg_rf.feature_importances_
    	test_pred = reg_rf.predict(X_test)
    	return(test_pred,fti)
    	
#XGboost
    def xgboost(X_train, y_train, X_test):
    	reg_XGB = xgb.XGBRegressor(objective ='reg:squarederror', random_state=1)
    	#reg_XGB = xgb.XGBRegressor(booster='gbtree',eta ='0.3',  n_estimators=700,n_jobs=-1,random_state=1)
    	X_train.columns = range(len(X_train.iloc[0,:]))
    	X_test.columns = range(len(X_train.iloc[0,:]))
    	
    	reg_XGB.fit(X_train,y_train)
    	fti = reg_XGB.feature_importances_
    	test_pred = reg_XGB.predict(X_test)
    	return(test_pred,fti)

#Adaboost
    def adaboost(X_train, y_train, X_test):
    	reg_ADA = AdaBoostRegressor()
    	reg_ADA.fit(X_train,y_train)
    	fti = reg_ADA.feature_importances_
    	test_pred = reg_ADA.predict(X_test)
    	return(test_pred,fti)
    	
#ランダムフォレスト分類定義
    def R_forest_b(X_train, y_train, X_test):
    	n_e = int(txt3.get())
    	
    	if str(txt4.get()) == "デフォルト":
    		m_d = None
    	else:
    		m_d = int(txt3.get())
    	reg_rf = RandomForestClassifier(n_estimators=n_e,max_depth = m_d,n_jobs=-1,random_state=1)
    	reg_rf.fit(X_train,y_train)
    	fti = reg_rf.feature_importances_
    	test_pred = reg_rf.predict(X_test)
    	return(test_pred,fti)
        
#予測ボタンの動作定義#
    def hosei():
    	if '.csv' in filename_open:
    		df = pd.read_csv(filename_open,encoding="CP932")
    	else:
    		df = pd.read_excel(filename_open,sheet_name=0)
    	print(df)
    	df = df.dropna(how='any')
    	#空白データ抜いた後に番号飛び飛びになるから
    	df = df.reset_index(drop=True)
    	#print(df.describe().apply(lambda s: s.apply(lambda x: format(x, 'g'))))
    	print(df)
    	
    	df_c = df.columns.values.tolist()
    	
    	if str(txt_m.get()) == "入力してください":
    			txt_m.delete(0,tkinter.END)
    			txt_m.insert(tkinter.END,df_c[-1])
    			target = df_c[-1]
    	else:
    		target = str(txt_m.get())
    	try:
    		m_ind = df_c.index(target)
    	except:
    		msg_box1 = tkinter.messagebox.showinfo('確認', '該当の目的変数が存在しません。')
    		return()
    		
    	#目的変数の列番号
    	txt_m2.delete(0,tkinter.END)
    	txt_m2.insert(tkinter.END,m_ind)
    	
    	if var.get() == 0:
    		# 標準化
    		sc = StandardScaler()
    		sc.fit(df)
    		z = sc.transform(df)
    		#平均・標準偏差
    		mean, scale = sc.mean_, sc.scale_
    		df1 = pd.DataFrame(z, columns = df.columns.values.tolist(), index = df.index.values.tolist())
    	else:
    		df1 = df
    	
    	
    	haba = int(txt1.get())
    	if len(df1) <= haba:
    		msg_box1 = tkinter.messagebox.showinfo('確認', 'テストデータサイズで指定した行数が大きすぎます。')
    		return()
    	else:
    		pass
    	
    	
    	print("データ長さ",len(df1))
    	coeff_list = []
    	ans = []
    	for i in tqdm(range((len(df1)//haba) +1)):
    		
    		if i < len(df1)//haba:
    			df_test = df1.iloc[i*haba : (i+1)*haba, :]
    			df_train  = df1.drop(range(i*haba , (i+1)*haba))
    		elif len(df1) % haba > 0:
    			df_test = df1.iloc[len(df1) % haba *(-1) :, :]
    			df_train  = df1.iloc[:len(df1) % haba *(-1), :]
    			#print("最後",df_train.index.values.tolist())
    			#print("最後",df_test.index.values.tolist())
    		else:
    			print("あまり無し")
    			break
    		
    		
    		X_train, y_train  = df_train.drop(columns=target),  df_train.loc[:,target]
    		X_test, y_test    = df_test.drop(columns=target) ,  df_test.loc[:,target]
    		
    		if str(combo[1].get()) == "アンサンブル回帰(Randomforest)":
    			Random_F =  R_forest(X_train, y_train, X_test)
    			test_pred = pd.DataFrame(Random_F[0],index =df_test.index.values.tolist(),columns = [str(target)+"RandomForest"])
    			tokucho   = Random_F[1]
    		elif str(combo[1].get()) == "アンサンブル回帰(Adaboost)":
    			Ada_b =  adaboost(X_train, y_train, X_test)
    			test_pred = pd.DataFrame(Ada_b[0],index =df_test.index.values.tolist(),columns = [str(target)+"Adaboost"])
    			tokucho   = Ada_b[1]
    		elif str(combo[1].get()) == "アンサンブル回帰(XGboost)":
    			Xg_b =  xgboost(X_train, y_train, X_test)
    			test_pred = pd.DataFrame(Xg_b[0],index =df_test.index.values.tolist(),columns = [str(target)+"XGboost"])
    			tokucho   = Xg_b[1]
    		elif str(combo[1].get()) == "線形回帰(Lasso)":
    			linier_Lasso = Linear_Lasso(X_train, y_train, X_test)
    			test_pred = pd.DataFrame(linier_Lasso[0],index =df_test.index.values.tolist(),columns = [str(target)+"Lasso"])
    			tokucho   = linier_Lasso[1]
    		elif str(combo[1].get()) == "線形回帰(Ridge)":
    			linier_Ridge = Linear_Ridge(X_train, y_train, X_test)
    			test_pred = pd.DataFrame(linier_Ridge[0],index =df_test.index.values.tolist(),columns = [str(target)+"Ridge"])
    			tokucho   = linier_Ridge[1]
    		else:
    			#何分割かに分ける等の処理が必要
    			
    			Random_B =  R_forest_b(X_train, y_train, X_test)
    			test_pred = pd.DataFrame(Random_B[0],index =df_test.index.values.tolist(),columns = [str(target)+"RandomForest分類"])
    			tokucho   = Random_B[1]
    		
    		coeff_list.append(tokucho)
    		
    		if i == 0:
    			df_rec = test_pred
    		else:
    			df_rec = pd.concat([df_rec,test_pred])
    	
    	s_ind = copy.deepcopy(df_c)
    	s_ind.pop(m_ind)
    	
    	coeff_list = pd.DataFrame(coeff_list, columns = s_ind)
    	
    	if var.get() == 0:
    		df_rec = df_rec * scale[m_ind]  + mean[m_ind]
    	else:
    		pass
    	print(df_rec)
    	df_kekka = df.loc[df_rec.index.values.tolist(),:]
    	df_kekka = pd.concat([df_kekka,df_rec],axis=1)
    	print(df_kekka)
    	print(filename_open)
    	path, ext = os.path.split(filename_open)
    	#print(path)
    	
    	
    	if str(combo[1].get()) == "アンサンブル(Randomforest)":
    		filename_1 = str(path) + '/予測結果比較' + str(combo[1].get()) + '_木' + str(txt3.get()) + '_層' + str(txt4.get()) +'.csv'
    		filename_2 = str(path) + '/特徴量'       + str(combo[1].get()) + '_木' + str(txt3.get()) + '_層' + str(txt4.get()) +'.csv'
    	elif str(combo[1].get()) == "線形(Lasso)" or str(combo[1].get()) == "線形(Ridge)":
    		filename_1 = str(path) + '/予測結果比較' + str(combo[1].get()) + '_alpha' + str(txt2.get()) +'.csv'
    		filename_2 = str(path) + '/特徴量'       + str(combo[1].get()) + '_alpha' + str(txt2.get())  +'.csv'
    	else:
    		filename_1 = str(path) + '/予測結果比較' + str(combo[1].get()) +'.csv'
    		filename_2 = str(path) + '/特徴量'  + str(combo[1].get()) + '.csv'
    	
    	if os.path.isfile(filename_1):
    		return_YN = tkinter.messagebox.askyesno("Yes or No ?", str(filename_1) +"が存在します。上書しますか？")
    		if return_YN == False: #「No」をクリックされた時の処理
        		filename_1 =  tkinter.filedialog.asksaveasfilename(initialdir = "/",title = "Save as",filetypes =  [("csv file","*.csv")])
    		elif return_YN == True: #「Yes」をクリックされた時の処理
        		pass
    	else:
    		pass
    		
    	if ".csv" in filename_1:
    		pass
    	elif "." in filename_1:
    		filename_1 = filename_1.split(".")
    		filename_1 = filename_1[0] + ".csv"
    	else:
    		filename_1 = filename_1 + ".csv"
    	df_kekka.to_csv(filename_1,encoding="CP932")
    	
    	
    	if os.path.isfile(filename_2):
    		return_YN = tkinter.messagebox.askyesno("Yes or No ?", str(filename_2) +"が存在します。上書しますか？")
    		if return_YN == False: #「No」をクリックされた時の処理
        		filename_2 =  tkinter.filedialog.asksaveasfilename(initialdir = "/",title = "Save as",filetypes =  [("csv file","*.csv")])
    		elif return_YN == True: #「Yes」をクリックされた時の処理
        		pass
    	else:
    		pass
    		
    	if ".csv" in filename_2:
    		pass
    	elif "." in filename_2:
    		filename_2 = filename_2.split(".")
    		filename_2 = filename_2[0] + ".csv"
    	else:
    		filename_2 = filename_2+ ".csv"
    	coeff_list.to_csv(filename_2,encoding="CP932")
    	msg_box1 = tkinter.messagebox.showinfo('確認', '正常に終了しました。')
    	
#ボタンの配置定義
    lb = {}
    entry = {}
    combo = {}
    
    btn1 = Button(root,text = "読み込みデータ",command = hosei_data,width = 15)
    btn1.place(x = 10,y = 10)
    lb[1] = Label(root,text = '')
    lb[1].place(x = 130,y = 10)
    
    
    lb[2] = Label(root,text = '目的変数の列名(デフォルトは右端列)')
    lb[2].place(x = 10,y = 50)
    txt_m = tkinter.Entry(width=40)
    txt_m.insert(tkinter.END,"入力してください")
    txt_m.place(x=220, y=50)
    
    txt_m2 = tkinter.Entry(width=5)
    txt_m2.insert(tkinter.END,"")
    txt_m2.place(x=500, y=50)
    
    #出力するグラフの種類
    lb[3] = Label(root,text = 'データの標準化を')
    lb[3].place(x = 10,y = 75)
    var = tkinter.IntVar()
    var.set(0)
    rdo1 = Radiobutton(root, value=0, variable=var, text='する')
    rdo1.place(x=220, y=75)
    rdo2 = Radiobutton(root, value=1, variable=var, text='しない')
    rdo2.place(x=290, y=75)
    
    lb[4] = Label(root,text = 'テストデータサイズ[分割法]')
    lb[4].place(x = 10,y = 100)
    txt1 = tkinter.Entry(width=10)
    txt1.insert(tkinter.END,"1")
    txt1.place(x=220, y=100)
    
    lb[5] = Label(root,text = '分析手法選択')
    lb[5].place(x = 10,y = 125)
    combo[1] = ttk.Combobox(root, state='readonly',width = 30)
    combo[1].place(x = 220 ,y = 125)
    combo[1]["values"] = (["アンサンブル回帰(Randomforest)","アンサンブル回帰(Adaboost)","アンサンブル回帰(XGboost)","線形回帰(Lasso)","線形回帰(Ridge)","アンサンブル分類(Randomforest)"])
    combo[1].current(0)
    
    lb[6] = Label(root,text = 'RandomForest学習系')
    lb[6].place(x = 10,y = 200)
    
    lb[7] = Label(root,text = '木の本数')
    lb[7].place(x = 10,y = 230)
    txt3 = tkinter.Entry(width=10)
    txt3.insert(tkinter.END,1000)
    txt3.place(x=100, y=230)
    
    lb[8] = Label(root,text = '層数')
    lb[8].place(x = 10,y = 250)
    txt4 = tkinter.Entry(width=10)
    txt4.insert(tkinter.END,"デフォルト")
    txt4.place(x=100, y=250)
    
    
    lb[9] = Label(root,text = '線形回帰学習系')
    lb[9].place(x = 310,y = 200)
    
    lb[10] = Label(root,text = 'alpha')
    lb[10].place(x = 310,y = 230)
    txt2 = tkinter.Entry(width=10)
    txt2.insert(tkinter.END,"0.01")
    txt2.place(x=400, y=230)
    
    
    btn2 = Button(root,text = "予測",command = hosei,width = 10)
    btn2.place(x = 10,y = 360)
    
    btn3 = Button(root,text = "キャンセル",command = stop,width = 10)
    btn3.place(x = 90,y = 360)
    
    root.mainloop()


