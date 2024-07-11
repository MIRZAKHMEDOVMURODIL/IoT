import os
os.add_dll_directory('C:\\Program Files\\IBM\\IBM DATA SERVER DRIVER\\bin')
import ibm_db
import sys
import logging
from logging.handlers import RotatingFileHandler
from os.path import join
import datetime

database = "AYB_APPL"
host = "10.143.16.244"
port ="50000"
protocol="TCPIP"
user="IOT_DATA"
password="asd23fgh"
log = "logs"

os.makedirs(log, exist_ok=True)

log_path = join(log,"debug.log")
log_formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')
log_handler = RotatingFileHandler(filename=log_path, maxBytes=1048576, backupCount=10, delay=True)
log_handler.setFormatter(log_formatter)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  
logger.addHandler(log_handler)

# 1.Take Variable from MotionBoard
try:
    CATEGORY = sys.argv[1]
    EQP = sys.argv[2]
    TS_DT = sys.argv[3]
    DATA_COLUMN = sys.argv[4]
    INPUT_DT = sys.argv[5]
    INPUT_PERSON = sys.argv[6]
    INPUT_COMMENT = sys.argv[7]
    DELETE_ROWS_DT = sys.argv[8]

except Exception as e:
    logging.error(f"An error occurred while taking variable from Motionboard to Python: {str(e)}")


# 2.Connect to Database
try:
    dsn = f"DATABASE={database};HOSTNAME={host};PORT={port};PROTOCOL={protocol};UID={user};PWD={password}"
    conn = ibm_db.connect(dsn, "", "")
except Exception as e:
    logging.info("Failed to Connect to Database: %s", e)


# 3.Update Database
try:
    ts_dt = datetime.datetime.strptime(TS_DT, '%Y/%m/%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
    input_dt = datetime.datetime.strptime(INPUT_DT, '%Y/%m/%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')  
    delete_rows_dt = datetime.datetime.strptime(DELETE_ROWS_DT,'%Y/%m/%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')

    if ts_dt > delete_rows_dt:
        sql = f"UPDATE IOT_DATA.THRESHOLD_ALERT SET INPUT_DT='{input_dt}', INPUT_PERSON='{INPUT_PERSON}', INPUT_COMMENT='{INPUT_COMMENT}' WHERE CATEGORY='{CATEGORY}' AND EQP='{EQP}' AND TS_DT<='{ts_dt}' AND  TS_DT>='{delete_rows_dt}' AND DATA_COLUMN='{DATA_COLUMN}'"
    else:
        sql = f"UPDATE IOT_DATA.THRESHOLD_ALERT SET INPUT_DT='{input_dt}', INPUT_PERSON='{INPUT_PERSON}', INPUT_COMMENT='{INPUT_COMMENT}' WHERE CATEGORY='{CATEGORY}' AND EQP='{EQP}' AND TS_DT='{ts_dt}' AND DATA_COLUMN='{DATA_COLUMN}'"

    stmt = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
except Exception as e:
    logging.exception("An error occurred while updating: %s", e)
