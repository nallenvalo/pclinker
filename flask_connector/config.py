import os

# MYSQL_USER = os.getenv('MYSQL_USER', 'your_username')
# MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'your_password')
# MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
# MYSQL_PORT = os.getenv('MYSQL_PORT', '3306')
# DATABASE_NAME = os.getenv('DATABASE_NAME', 'default_db')

class Config:
    SECRET_KEY = 'Tarabio1'
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'nallen'
    MYSQL_PASSWORD = 'Tarabio1'
    New_MYSQL_PASSWORD = 'wtQGQ6EX.*zA6Zh'
    New_MYSQL_HOST = '10.10.100.41'

    # SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/app_data'
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{New_MYSQL_PASSWORD}@{New_MYSQL_HOST}/app_data'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False