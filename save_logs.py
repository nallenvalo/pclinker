import json
import pandas as pd
from sqlalchemy import create_engine, inspect
from datetime import timedelta
import mysql.connector
import numpy as np
import matplotlib.pyplot as plt
import json
import scipy
import logging
from tabulate import tabulate
import os
from sqlalchemy.pool import Pool
from sqlalchemy import event
import time
import sys
import time
from datetime import datetime, date, time as dt_time
import nidaqmx
import matplotlib.pyplot as plt
from nidaqmx.stream_writers import DigitalSingleChannelWriter
from nidaqmx.stream_readers import AnalogMultiChannelReader
from nidaqmx.stream_readers import AnalogSingleChannelReader
from nidaqmx.constants import AcquisitionType, Edge, LoggingMode, LoggingOperation, READ_ALL_AVAILABLE
from nptdms import TdmsFile
import scipy.stats as stats

with open('variables.json', 'r') as file:
    variables = json.load(file)

now = datetime.now()
yesterday = now - timedelta(days=1)
username = 'nallen'
password = 'wtQGQ6EX.*zA6Zh'
host = '10.10.100.41'

engine_app_data = create_engine(f'mysql+mysqlconnector://{username}:{password}@{host}/app_data', pool_size=400, max_overflow=800)
inspector = inspect(engine_app_data) 
if inspector.has_table('plate_log_data'):
    print('PLATE LOG TABLE FOUND')
    plate_log_data = pd.read_sql_table('plate_log_data', engine_app_data)
else : 
    raise Exception('NO PLATE LOGS')

output_dir = 'C:\\Users\\microscope\\Desktop\\SkeletalStimLogs\\App_Data\\'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
sql_out_file = output_dir + f'plate_log_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
if os.path.exists(sql_out_file):
    os.remove(sql_out_file)
plate_log_data.to_csv(sql_out_file, index=True)
print('Plate Log Data Local Copy has been saved')