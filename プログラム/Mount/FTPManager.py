import json
import logging
from ftplib import FTP
import os
import time
import datetime as dt
from datetime import datetime
from datetime import timedelta
from logging.handlers import RotatingFileHandler
from os.path import join


# 1.Get JSON Variable********************************************************************************************

json_path = r'C:\Users\00220401626\Desktop\プログラム\Mount\config.json'

try:   
    with open(json_path) as json_file:
        config = json.load(json_file)

    host = config['host']
    username = config['username']
    password = config['password']
    remote_folder = config['remote_folder']
    local_folder = config['local_folder']
    log = config['log_path']
    days = config['days']
    exts = config['exts']
    last_time = config['last_time']
    last_time = dt.strptime(last_time, '%Y/%m/%d %H:%M:%S')
    logging.info("Get JSON Variable")
except Exception as e:
    logging.info(f"Error: {e}")

# 2.Logging Configuration*****************************************************************************************

try:
    if not os.path.exists(log):
        os.makedirs(log, exist_ok=True)

    dt_st = datetime.now()
    log_path = join(log, f"debug_{dt_st.strftime('%Y%m%d')}.log")
    log_formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    log_handler = RotatingFileHandler(filename=log_path, maxBytes=1048576, backupCount=10, delay=True)
    log_handler.setFormatter(log_formatter)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(log_handler)
    logging.info("Logging Configuration")

except Exception as e:
    logging.error(f"An error occurred while setting up logging:", e)


# 3. Delete Old Logs************************************************************************************************

def delete_old_logs(log, days):

    period_time = datetime.now() - timedelta(days=days)

    for filename in os.listdir(log):
        filepath = os.path.join(log, filename)
        if os.path.isfile(filepath) and datetime.fromtimestamp(os.path.getctime(filepath)) < period_time:
            try:
                os.remove(filepath)
                logging.info(f"Deleted log file: {filepath}")
            except Exception as e:
                logging.error(f"Error deleting file: {filepath} - {e}")


# 4.Update_JSON****************************************************************************************************

def update_json_last_time(new_time):
    try:
        config['last_time'] = new_time
        json_data = json.dumps(config, indent=2)

        with open(json_path, 'w') as output_file:
            output_file.write(json_data)

        logging.info(f'Last modified time is {new_time}')

    except Exception as e:
        logging.error(f"An error occurred while updating Last time to JSON file:", e)



# 5.Download Ftp Folder to Local ***********************************************************************************

def download_ftp_files(host, username, password, remote_folder, local_folder, last_time):
    try:
        ftp = FTP(host)
        ftp.login(username, password)
        ftp.cwd(remote_folder)

        files = ftp.mlsd()
        if files:
            new_time = ''
            for file, meta in files:
                if file.endswith(exts):
                    modified_time = datetime.strptime(meta['modify'], "%Y%m%d%H%M%S")
                    if modified_time > last_time:
                        local_file_path = os.path.join(local_folder, file)
                        with open(local_file_path, 'wb') as local_file:
                            ftp.retrbinary('RETR ' + file, local_file.write)
                        logging.info(f"Downloaded file: {file}")
                        new_time = modified_time
                else:
                    pass
            update_json_last_time(new_time) 
            logging.info(f'Last modified time is {new_time}')
        else:
            logging.info('There are no new files to update')

    except Exception as e:
        logging.exception(f"An error occurred: {e}")

    finally:
        ftp.quit()
        delete_old_logs(log, days)


# Main****************************************************************************************************************

start_time = time.time()

download_ftp_files(host, username, password, remote_folder, local_folder, last_time)

end_time = time.time()

total_time = end_time - start_time
logging.info("Finished. Total spent time: %s\n", total_time)


#Finsh*****************************************************************************************************************
# files = ftp.nlst()
# files = ftp.mlsd()
# file_time = time.strptime(file_time[4:], "%Y%m%d%H%M%S")