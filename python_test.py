from datetime import datetime

timestr_1 = '06-13-24  02:20AM test'	
timestr_2 = '06-13-24  02:20PM test'	

time_1 = timestr_1[0:17].strip()
time_2 = timestr_2[0:17].strip()

time_1 = datetime.strptime(time_1, '%m-%d-%y %I:%M%p').strftime('%Y-%m-%d %H:%M:%S')
print(time_1)

time_2 = datetime.strptime(time_2, '%m-%d-%y %I:%M%p').strftime('%Y-%m-%d %H:%M:%S')
print(time_2)


for file in files:
    for ext in exts:
        if file.endswith(ext):
            modified_time = file[0:17].strip()
            modified_time = datetime.strptime(modified_time, '%m-%d-%y %I:%M%p').strftime('%Y-%m-%d %H:%M:%S')

            if modified_time > last_time:
                local_file_path = os.path.join(local_folder, file)
                
                with open(local_file_path, 'wb') as local_file:
                    ftp.retrbinary('RETR ' + file, local_file.write)

                modified_timestamp = modified_time.timestamp()
                os.utime(local_file_path, (modified_timestamp, modified_timestamp))
                
                logging.info(" Downloaded file: {} || Modified time: {}".format(file,modified_time))
                
                if modified_time >= new_time:
                    new_time = modified_time

