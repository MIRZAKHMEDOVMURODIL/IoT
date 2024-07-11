システム概要 　-------------------------------------------------------------------------------------------------

EQP_Log 

1.Get_Data.sh と FTPManager.py: TPからローカルにログをダウンロード
　■　データ連携用PCがデータ連携用TPから各設備のログファイルをローカルに取得します。
　■　Get_Data.shからFTPManager.pyが起動され、FTPを通じてTPからTemp/Shareフォルダにデータが取得されます。
　■　cronにより、Get_Data.shが定期的に実行されます。

2.Mount.sh: ローカルからサーバーへログをコピー
　■　データ連携用PCがTemp/*フォルダに取得したログファイルをファイルサーバーにコピーします。
　■　cronにより、Mount.shが定期的に実行されます。　　　　　　　　　　　　　　　

3. Temp/Shareフォルダの、更新日が30日超えたファイルを削除
  ■　Delete.sh    : del -> /Temp/Share


GashoPC_Log 

1.ログファイルをローカルに取得
  ■ データ連携用PCが各装置画処PCからログファイルをローカルに取得します。
  ■ cronにより、InspMount.shを定期的に実行します。
  ■ InspMount.sh: (/PC = /Mount/Share) -> /Temp/Share

2.ログファイルのファイルサーバーへのコピー
  ■ データ連携用PCが、装置画処PCから取得したログファイルをファイルサーバーにコピーします。
  ■ cronにより、Mount.shを定期的に実行します。
  ■ Mount.sh: /Temp/Share -> (/Mount_Server = /Server)
         
3. Temp/Shareフォルダの、更新時間が30日超えたファイルを削除
  ■ Delete.sh: del -> /Temp/Share


ファイル構成　 --------------------------------------------------------------------------------------------------------

EQP_Log                        # TPからログを取得してローカルにダウンロードします。その後ローカルからサーバーへコピーします。  
  1.Code                       # プログラムが実行するために必要なファイルが保存されるフォルダ
   	1.Log　　　　　　　　　　　　# ログファイルが保存されるディレクトリ
	  2.config.json           　 # 設定情報が記載されたJSONファイル
    3.Get_Data.sh              # TPからローカルにデータを取得する
	  4.FTPManager.py          　# FTPを使用してデータをダウンロードする
	  5.Mount.sh               　# ローカルのデータをファイルサーバーにコピーする
	  6.Delete.sh                # 一時フォルダのデータを削除する
  2.Mount_Server/Share         # データが一時的に保存されるサーバーの共有フォルダ
  3.Temp/Share                 # ローカルPC上の一時フォルダ。データが一時的に保存されます


GashoPC_Log                    # 装置画処PCのログファイルをローカルに取得し、ローカルからファイルサーバーにコピーします。　
  1.Code                       # プログラムが実行するために必要なファイルが保存されるフォルダ
	  1.InspMount.sh             #　各装置からローカルにログファイルを取得する
	  2.Mount.sh                 #　ローカルのデータをファイルサーバーにコピーする
	  3.Delete.sh                #　一時フォルダのデータを削除する
  2.Mount_Server               #　データが保存されるサーバー
  3.Mount_PC                   #　各装置から取得したデータが一時的に保存されるPCの共有フォルダ
  4.Temp                       #　データ連携用PC上のデータが一時的に保存される一時フォルダ。


FileZilla Server(インストール・設定)　------------------------------------------------------------------------------------


	1. Download and Install FileZilla Server

	2. Add [user]    
		1. Virtual_Path : /TP
		2. Native_Path  : C:\Users\EQP_Log\TP

	3.Fttp接続に必要な情報
		1.host             : 　　　　　　　　　　　　
		2.port             :    　　　　　　 
		3.username         :				
		4.password         :			
		5.remote_folder    :				

	4.Firewall Setting
		1.詳細設定 -> 受信の規則 -> 新しい規則	-> プログラム -> このプログラムのパズ -> 参照　-> 接続を許可する　-> 次へ　-> 完了


CroneTab　--------------------------------------------------------------------------------------------------------------------

crontab -e

 0 0 * * *   /IoT/PC/EQP_Log/Code/Get_Data.sh            GetData.sh実行(FTPを用いて、装置からファイルを取得)
10 0 * * *   /IoT/PC/EQP_Log/Code/Mount.sh               MountSH.sh実行(FTPで取得したファイルを共有フォルダへコピー)
20 0 * * *   /IoT/PC/EQP_Log/Code/Delete.sh              Delete.sh実行 (更新日が30日超えたファイルを削除)

10 0 * * *  /IoT/PC/GashoPC_Log/Code/InspMount.sh        InspMount.sh実行(各装置からファイルを取得)
20 0 * * *  /IoT/PC/GashoPC_Log/Code/Mount.sh            Mount.sh実行(ロカルのファイルを共有フォルダへコピー)
30 0 * * *  /IoT/PC/GashoPC_Log/Code/Delete.sh           Delete.sh実行 (更新日が30日超えたファイルを削除)


接続情報　----------------------------------------------------------------------------------------------------------------------

1.EQP_Log

  1.Ftpから接続しファイルを取得するのに必要な情報

  　host             :	192.168.10.3																
  	username         :	admin
    password         :	kyocera00
    remote_folder_1  :	"/FV03004"        OK
    remote_folder_2  :	"/FV03014"        OK

  2.サーバー共有フォルダへコーピするのに必要な情報

  　FilePath　　　　　: \\10.21.32.90\Iotstrage\Data     \FV03004
                                                        \FV03014
    UserID           : Iotusr
    PassWord         : Cera1usr
    Domain           : SHGCERLDS05 　　　　　　　　　

2.GashoPC_Log

  1. 各装置画処PC

    vers     = 2.0      　　　
    user     = なし 
    password = なし 

    FV03004_PC1　   : //192.168.10.100/_apr　　　 #6/16確認　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　      　(//192.168.10.100/_apr/FV03004_PC1)
    FV03004_PC2　   : //192.168.10.101/_apr　　　 #6/16確認　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　      　(//192.168.10.101/_apr/FV03004_PC2)
    FV03014_PC1　   : //192.168.10.102/Log/検査データログ　　　 OK　　　　　　　　　　　　　　　　　　　　　　　　　　　　　      　(//192.168.10.102/_apr/FV03004_PC1)
    FV03014_PC2　   : //192.168.10.103/Log/検査データログ　　　 OK　　　　　　　　　　　　　　　　　　　　　　　　　　        　(//192.168.10.103/_apr/FV03004_PC2)

  2. サーバー共有フォルダへコーピするのに必要な情報

  　FilePath　　　　　: \\10.21.32.90\Iotstrage\Data     \FV03004_PC1　  
                                                        \FV03004_PC2　   　　　　　　　　　　　　　　　　      
                                                        \FV03014_PC1　   　　　　　　　　　　　　　      
                                                        \FV03014_PC2　         
    UserID           : Iotusr
    PassWord         : Cera1usr
　　 Domain           : SHGCERLDS05　　　　　　　　　OK
------------------------------------------------------------------------------------------------------------------------------


\\10.21.32.90\Iotstrage\Data      \FV03004
                                  \FV03014
                                  \FV03004_PC1　  
                                  \FV03004_PC2　   　　　　　　　　　　　　　　　　      
                                  \FV03014_PC1　   　　　　　　　　　　　　　      
                                  \FV03014_PC2　   



Windows 7 supports SMB versions 1.0, 2.0, and 2.1. 
By default, Windows 7 primarily uses SMB 2.0 and 2.1

echo %username%
echo %computername%

smbstatus
smbd -V
cd "\Program Files\Samba"
smbclient --version

/bin/mount -t cifs -o vers=2.0,ro,user=visionsystem,password='',iocharset=utf8,uid=1002,gid=1002
/bin/mount -t cifs -o vers=2.0,domain='SHGCERLDS05',user='DBCOLL01',password='CeraColl1u' //10.21.32.70/DbStrage /IoT/ftp/mnt/share



Sambaのバージョンを確認する方法

sc query mrxsmb10
sc query mrxsmb20
sc.exe qc lanmanworkstation

powershell
Get-SmbServerConfiguration



PC (file://Ha000154306/pc)

#test
sudo /bin/mount -t cifs -o vers=2.0,domain='AD',user='00220401626',password='Mm3001645$' //10.37.152.184/PC/FV03004_PC1 /IoT/PC/GashoPC_Log/Mount_PC/FV03004_PC1  
sudo /bin/mount -t cifs -o vers=2.0,domain='AD',user='00220401626',password='Mm3001645$' //10.37.152.184/pc /IoT/PC/GashoPC_Log/Mount_PC/FV03004_PC1   
sudo find /IoT/PC/GashoPC_Log/Mount_PC/FV03004_PC1 -type f -mtime -30 -exec cp -rp {} /IoT/PC/GashoPC_Log/Temp/FV03004_PC1 \;
sudo /bin/umount /IoT/PC/GashoPC_Log/Mount_PC/FV03004_PC1
	
Windows 7 でパスワードなしの共有フォルダを作成。

1.コントロールパネルを開きます。
2.ネットワークと共有センターを選択します。
3.共有の詳細設定をクリックします。
4.パスワード保護を無効にするために、すべてのネットワークの設定を変更します。
5.共有したいフォルダのプロパティで、共有タブを選択し、Everyoneに目的のアクセス権を与えます。
6.同じく共有したいフォルダのプロパティで、セキュリティタブを選択し、Everyoneに目的のアクセス権を与えます。


import traceback

traceback_str = traceback.format_exc() 
logging.error("FailedFile:{}.\n Error{}.\n{}".format(remote_path, e, traceback_str))








