from logging.handlers import RotatingFileHandler
from datetime import timedelta, datetime
from os.path import join
from ftplib import FTP
import logging
import time
import json
import sys
import os
import traceback


# 1.Get JSON Variable********************************************************************************************

if len(sys.argv) > 1:
    json_path = sys.argv[1]
else:
    print(" No JSON path provided in arguments.")
    sys.exit(1)

try:   
    with open(json_path) as json_file:
        config = json.load(json_file)

    port = config["port"]
    host = config['host']
    username = config['username']
    password = config['password']
    remote_folder = config['remote_folder']
    local_folder = config['local_folder']
    log = config['log_path']
    days = config['days']
    exts = config['exts']
    last_time = config['last_time']
    last_time = datetime.strptime(last_time, "%Y-%m-%d %H:%M:%S")

    if not os.path.exists(local_folder):
        os.makedirs(local_folder, exist_ok=True)
    
except Exception as e:
    print(" Error: Get JSON Variable {}".format(e))


# 2.Logging Configuration*****************************************************************************************

try:
    if not os.path.exists(log):
        os.makedirs(log, exist_ok=True)

    dt_st = datetime.now()
    log_path = join(log, "debug_{}.log".format(dt_st.strftime('%Y%m%d')))
    log_handler = RotatingFileHandler(filename=log_path, maxBytes=1048576, backupCount=10, delay=True)
    log_formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    log_handler.setFormatter(log_formatter)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(log_handler)
    logging.info(" Started {} --------------------------------------------------------------".format(remote_folder))
                                                         
except Exception as e:
    logging.error(" Logging Configuration. Error:{}".format(e))


# 3.Update_JSON****************************************************************************************************

def update_json_last_time(new_time):
   
    if new_time:
        try:
            config['last_time'] = new_time.strftime("%Y-%m-%d %H:%M:%S")
            json_data = json.dumps(config, indent=2)
            
            with open(json_path, 'w', encoding='utf-8') as output_file:
                output_file.write(json_data)

            logging.info(' Step_2. Update_JSON. Last modified time is {}'.format(new_time))

        except Exception as e:
            logging.error(" Error: Step_2. Update_JSON.{}".format(e))
    else:
        logging.info(" Step_2. Update_JSON. Already updated.")


# 4. Delete Old Logs************************************************************************************************

def delete_old_logs(log, days):
    logging.info(" Step_3. Delete Old Logs.")

    days = int(days)
    period_time = datetime.now() - timedelta(days=days)

    for filename in os.listdir(log):
        filepath = os.path.join(log, filename)
        if os.path.isfile(filepath) and datetime.fromtimestamp(os.path.getctime(filepath)) < period_time:
            try:
                os.remove(filepath)
                logging.info(" Deleted log file: {}".format(filepath))
            except Exception as e:
                logging.error(" Step_3. Delete Old Logs.  Error:  {} - {}".format(filepath, e))
    

# 5.Download Ftp Folder to Local ***********************************************************************************

def download_ftp_files(host, username, password, port, remote_folder, local_folder, last_time):
    logging.info(" Step_1. Download Remote Folder to Local.")
    try:
        ftp = FTP()
        ftp.connect(host, port) 
        ftp.login(username, password)
        ftp.cwd(remote_folder)
   
        files = []
        ftp.dir('./', files.append)

        if files:
            new_time = last_time   
            for file in files:
                for ext in exts:
                    if file.endswith(ext):
                        modified_time = file[0:17].strip()
                        modified_time = datetime.strptime(modified_time, '%m-%d-%y %I:%M%p').strftime('%Y-%m-%d %H:%M:%S')
                        modified_time = datetime.strptime(modified_time, "%Y-%m-%d %H:%M:%S")
                        modified_time += timedelta(hours=9)
                       
                        path = file[39:]                    

                        if modified_time > last_time:
                            local_file_path = os.path.join(local_folder, path)                    
                            remote_path = remote_folder + file[39:]
                            try:
                                with open(local_file_path, 'wb') as local_file:
                                    ftp.retrbinary('RETR ' + remote_path, local_file.write)
                                logging.info("SuccessFile:{}.".format(remote_path))
                            except Exception as e:
                                logging.error("FailedFile:{}.\n Error{}.".format(remote_path, e))
                             

                            modified_timestamp = modified_time.timestamp()
                            os.utime(local_file_path, (modified_timestamp, modified_timestamp))
                            
                            logging.info(" Downloaded file: {} || Modified time: {}".format(file,modified_time))
                            
                            if modified_time >= new_time:
                                new_time = modified_time

            update_json_last_time(new_time) 
        else:
            logging.info(' Step_1. Download Remote Folder to Local. There are no new files to update')

    except Exception as e:
        logging.error(" Step_1. Download Remote Folder to Local. Error: {}".format(e))
        logging.error(str(e))

    finally:
        ftp.quit()
        delete_old_logs(log, days)

# Main****************************************************************************************************************

start_time = time.time()

download_ftp_files(host, username, password, port, remote_folder, local_folder, last_time)

end_time = time.time()

total_time = end_time - start_time      
logging.info(" Total Spent Time: %s", total_time)
logging.info(" Finished -------------------------------------------------------------\n\n ")


