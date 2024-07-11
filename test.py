# from ftplib import FTP
# from datetime import datetime

# def parse_ftp_date(date_str, current_year):
#     """Parse the FTP date string to a datetime object."""
#     try:
#         # Try to parse the date assuming it's within the current year
#         return datetime.strptime(date_str, '%b %d %H:%M').replace(year=current_year)
#     except ValueError:
#         # If that fails, it's a file older than a year
#         return datetime.strptime(date_str, '%b %d %Y')

# def get_ftp_file_dates(ftp_host, ftp_user, ftp_pass, ftp_dir):
#     ftp = FTP(ftp_host)
#     ftp.login(ftp_user, ftp_pass)
#     ftp.cwd(ftp_dir)
    
#     # Retrieve directory listing
#     lines = []
#     ftp.dir(lines.append)
    
#     current_year = datetime.now().year
#     files = []
    
#     for line in lines:
#         parts = line.split()
        
      
#         # -rw-r--r-- 1 owner group 512 Jan 1 00:00 filename
#         # -rw-r--r-- 1 owner group 512 Jan 1 2023 filename
        
#         # Last modification date is in parts[5:8]
#         month = parts[5]
#         day = parts[6]
#         time_or_year = parts[7]
#         name = ' '.join(parts[8:])
        
#         date_str = f'{month} {day} {time_or_year}'
        
#         file_date = parse_ftp_date(date_str, current_year)
#         files.append((name, file_date))
    
#     ftp.quit()
#     return files

# # Example usage
# ftp_host = 'ftp.example.com'
# ftp_user = 'username'
# ftp_pass = 'password'
# ftp_dir = '/path/to/directory'

# files = get_ftp_file_dates(ftp_host, ftp_user, ftp_pass, ftp_dir)
# for name, date in files:
#     print(f'File: {name}, Date: {date}')




