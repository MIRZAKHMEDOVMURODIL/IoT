import time
import pandas as pd
# import ibm_db
import logging
import os
import glob
import json
import datetime as dt 
import shutil
from os.path import join
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime, timedelta

# Load Configuration from JSON file
json_path = r'C:\Users\00220401626\Desktop\test\config.json'
with open(json_path) as json_file:
    config = json.load(json_file)
    
# Extract Configuration values
database = config['database']
host = config['host']
port = config['port']
protocol = config['protocol']
uid = config['uid']
pwd = config['pwd']
pc_csv = config['pc_csv']
local_csv = config['local_csv']
log = config['log']
insertion_time = config['insertion_time']
nas = config['nas']
time = str(insertion_time)
inserted_time = dt.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
inserted_day = inserted_time.strftime('%Y%m%d')

# Logging Settings
if not os.path.exists(log):
    os.makedirs(log, exist_ok=True)

dt_st = datetime.now()
log_path = join(log, f"debug_{dt_st.strftime('%Y%m%d')}.log")
log_formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
log_handler = RotatingFileHandler(filename=log_path, maxBytes=1048576, backupCount=10, delay=True)
log_handler.setFormatter(log_formatter)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(log_handler)

logging.info("1.Extract JSON Configuration Values")
print("1.Extract JSON Configuration Values")

# Copy CSV files from PC to Temp_CSV folder 
def copy_local():
    logging.info("2.Copy CSV Files to TEMP_CVS Folder")
    print("2.Copy CSV Files to TEMP_CVS Folder")
    
    if insertion_time:    
        csv_files = glob.glob(os.path.join(pc_csv,'*.csv'))
        selected_csv_paths = [file for file in csv_files if int(file[-12:-4]) >= int(inserted_day)]
    else:
        selected_csv_paths = glob.glob(os.path.join(pc_csv,'*.csv'))
        
    for source_path in selected_csv_paths:
        if os.path.exists(source_path):  
            file_name = os.path.basename(source_path)
            destination_path = os.path.join(local_csv, file_name)
            
            try:
                shutil.copy(source_path, destination_path)
                logging.info(f"'{file_name}' is copied '.")
                print(f"'{file_name}' is copied.")
            except Exception as e:
                logging.error(f"Error copying '{file_name}': {str(e)}")
                print(f"Error copying '{file_name}' : {str(e)}")
        else:
            logging.warning(f"Source file '{source_path}' does not exist.")
            print(f"Source file '{source_path}' does not exist.")

# Database Connection
def connect_db():
    logging.info("3.Database Connection")
    print("3.Database Connection")
    dsn = f"DATABASE={database};HOSTNAME={host};PORT={port};PROTOCOL={protocol};UID={uid};PWD={pwd}"
    conn = ibm_db.connect(dsn, "", "")
    if conn:
        logging.info("Connected to the database")
        print("Connected to the database")
    else:
        logging.info("Failed to connect to the database") 
        print("Not connected to the database")
    return conn

#Inserting the Latest Values into the Database
def latest_data(local_csv):
    logging.info("4.Latest_Values Insertion") 
    print("4.Latest_Values Insertion")
    try:
        csv_files = glob.glob(os.path.join(local_csv, '*.csv'))
        if csv_files:
            latest_csv_file = max(csv_files, key=os.path.getmtime)                                                                #max(int(csv_files[-12:-4]))
            df = pd.read_csv(f"{latest_csv_file}", encoding='cp932', dtype=object)
        
        if not df.empty:
            df['Timestamp'] = pd.to_datetime(df['Timestamp'])
            unique = df['Location'].unique()
            
            df_concat = []
            for location in unique:
                latest_location = df[df['Location'] == location].nlargest(1, 'Timestamp')
                df_concat.append(latest_location)
                
            latest_data = pd.concat(df_concat, ignore_index=True).sort_values(by='Location')
            merge_query = """
                MERGE INTO LIQUID_PARTICLE_LAST AS target
                USING (SELECT ? AS LOCATION, ? AS TS_DT, ? AS VALUE_1_0, ? AS VALUE_3_0, ? AS VALUE_5_0, ? AS VALUE_10_0, ? AS VALUE_15_0, ? AS VALUE_20_0, ? AS VALUE_25_0, ? AS VALUE_50_0 FROM SYSIBM.SYSDUMMY1) AS source
                ON target.LOCATION = source.LOCATION
                WHEN MATCHED THEN
                    UPDATE SET target.TS_DT = source.TS_DT, 
                               target.VALUE_1_0 = source.VALUE_1_0, 
                               target.VALUE_3_0 = source.VALUE_3_0, 
                               target.VALUE_5_0 = source.VALUE_5_0, 
                               target.VALUE_10_0 = source.VALUE_10_0, 
                               target.VALUE_15_0 = source.VALUE_15_0, 
                               target.VALUE_20_0 = source.VALUE_20_0, 
                               target.VALUE_25_0 = source.VALUE_25_0, 
                               target.VALUE_50_0 = source.VALUE_50_0
                WHEN NOT MATCHED THEN
                    INSERT (LOCATION, TS_DT, VALUE_1_0, VALUE_3_0, VALUE_5_0, VALUE_10_0, VALUE_15_0, VALUE_20_0, VALUE_25_0, VALUE_50_0)
                    VALUES (source.LOCATION, source.TS_DT, source.VALUE_1_0, source.VALUE_3_0, source.VALUE_5_0, source.VALUE_10_0, source.VALUE_15_0, source.VALUE_20_0, source.VALUE_25_0, source.VALUE_50_0);
                """
        
            stmt = ibm_db.prepare(conn, merge_query)
        
            for index, row in latest_data.iterrows():
                location = row['Location']
                timestamp = row['Timestamp']
                c1 = row['1.0μｍ']
                c3 = row['3.0μｍ']
                c5 = row['5.0μｍ']
                c10 = row['10.0μｍ']
                c15 = row['15.0μｍ']
                c20 = row['20.0μｍ']
                c25 = row['25.0μｍ']
                c50 = row['50.0μｍ']
        
                try:
                    if ibm_db.execute(stmt, (location, timestamp, c1, c3, c5, c10, c15, c20, c25, c50)):
                        logging.info(f"{location} : Inserted")
                        print(f"{location} : Inserted")
                    else:
                        error_message = f"Error {location}: {ibm_db.stmt_errormsg()}"
                        logging.error(error_message)
                except Exception as e:
                    error_message = f"Exception {location}: {str(e)}"
                    logging.error(error_message)

    except Exception as e:
        print(f"An error occurred: {e}")

#Inserting the All Values into the Database   
def all_data(local_csv):
    logging.info("5.All_Values Insertion") 
    print("5.All_Values Insertion")
    
    csv_files = glob.glob(os.path.join(local_csv, '*.csv'))
    if csv_files:  
        for csv in csv_files:
            df = pd.read_csv(fr"{csv}", encoding='cp932', dtype= object)
            df['Timestamp'] = df['Timestamp'].str.replace('/', '-', regex=False)
          
            config['insertion_time'] = str(df['Timestamp'].max())
            json_data = json.dumps(config, indent=2)
                        
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%Y-%m-%d %H:%M:%S') 
            
            if os.path.exists(json_path) and inserted_time:
                df = df[df['Timestamp'] > inserted_time]
                data = tuple(tuple(row) for row in df.values)
                values = ",".join(map(str, data))
            
                insert_query = f"INSERT INTO LIQUID_PARTICLE_TEST (Location, TS_DT, VALUE_1_0, VALUE_3_0, VALUE_5_0, VALUE_10_0, VALUE_15_0, VALUE_20_0, VALUE_25_0, VALUE_50_0) VALUES {values}"
                stmt = ibm_db.prepare(conn, insert_query)
            
                try:
                    if ibm_db.execute(stmt, values):
                        logging.info(f"{csv} : Inserted")
                        print(f"{csv} : Inserted")   
                        with open(json_path, 'w') as output_file:
                            output_file.write(json_data)
                except:
                    logging.info(f"{csv} : is already Updated")
                    print(f"{csv} : is already Updated")
              
            else:
                data = tuple(tuple(row) for row in df.values)
                values = ",".join(map(str, data))
            
                insert_query = f"INSERT INTO LIQUID_PARTICLE_TEST (Location, TS_DT, VALUE_1_0, VALUE_3_0, VALUE_5_0, VALUE_10_0, VALUE_15_0, VALUE_20_0, VALUE_25_0, VALUE_50_0) VALUES {values}"
                stmt = ibm_db.prepare(conn, insert_query)
            
                try:
                    if ibm_db.execute(stmt, values):
                        logging.info(f"{csv} : Inserted")
                        with open(json_path, 'w') as output_file:
                            output_file.write(json_data)
                except:
                    logging.info(f"{csv} : is already Updated")
                    print(f"{csv} : is already Updated")
    
    elif not selected_csv_files:
        logging.info("Database is already Updated")

# Backup CSV files to NAS and Delete from TEMP_CSV folder
def backup_and_delete_csv_files(local_csv, nas):
    logging.info("6.Backup_and_Delete_CSV_Files") 
    print("6.Backup_and_Delete_CSV_Files")
    
    csv_files = glob.glob(os.path.join(local_csv,'*.csv'))
    for source_path in csv_files:
        if os.path.exists(source_path):  
            file_name = os.path.basename(source_path)
            folder_name = file_name[:6]  
            
            destination_folder = os.path.join(nas, folder_name)
            
            destination_path = os.path.join(destination_folder, file_name)
            if not os.path.exists(destination_folder): 
                os.makedirs(destination_folder)
                print(f"Created folder '{folder_name}' in NAS")
                logging.info(f"Created folder '{folder_name}' in NAS")

            shutil.copy(source_path, destination_path)
            os.remove(source_path)
            print(f"File '{file_name}' copied to NAS and Deleted from TEMP_CSV")
            logging.info(f"File '{file_name}' copied to NAS and Deleted from TEMP_CSV")
        else:
            print(f"Source file '{source_path}' does not exist.")
            logging.info(f"Source file '{source_path}' does not exist.")
              
# Delete Log files if created day period passed 30 days                          
def delete_old_logs(log, days=30):
    period_time = datetime.now() - timedelta(days=days)

    for filename in os.listdir(log):
        if filename.endswith(".log"):
            filepath = os.path.join(log, filename)
            try:
                if os.path.isfile(filepath) and datetime.fromtimestamp(os.path.getctime(filepath)) < period_time:
                    os.remove(filepath)
                    logging.info(f"Deleted log file: {filepath}")
                    print(f"Deleted log file: {filepath}")
            except Exception as e:
                print(f"Error deleting file {filepath}: {e}")
                logging.info(f"Error deleting file {filepath}: {e}")
                    
# Running ALl Functions in Order
start_time = datetime.now()   

copy_local()
conn = connect_db()
latest_data(local_csv)
all_data(local_csv)
backup_and_delete_csv_files(local_csv, nas)
delete_old_logs(log)
  
end_time = datetime.now()
elapsed_time = end_time - start_time
total_seconds = elapsed_time.total_seconds()
minutes = int(total_seconds // 60)
seconds = int(total_seconds % 60)

print(f"Time spent: {minutes} minutes and {seconds} seconds")