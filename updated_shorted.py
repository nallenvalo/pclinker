import json
import pandas as pd
from sqlalchemy import create_engine, inspect
from datetime import timedelta
import mysql.connector
import numpy as np
import matplotlib.pyplot as plt
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

now = datetime.now()
yesterday = now - timedelta(days=1)
username = 'nallen'
password = 'wtQGQ6EX.*zA6Zh'
host = '10.10.100.41'

engine_app_data = create_engine(f'mysql+mysqlconnector://{username}:{password}@{host}/app_data', pool_size=400, max_overflow=800)
inspector = inspect(engine_app_data) 

engine_summary_stats = create_engine(f'mysql+mysqlconnector://{username}:{password}@{host}/summary_stats', pool_size=400, max_overflow=800)
inspector = inspect(engine_summary_stats) 
# will have to decide if we want to just maintain one summary_stats table for ever
summary_stats_table_list = []
for i in range(1,4):
    if inspector.has_table(f'summary_stats_table_harvard{i}'):
        table = pd.read_sql_table(f'summary_stats_table_harvard{i}', engine_summary_stats)
        summary_stats_table_list.append(table)
'''
if inspector.has_table('summary_stats_table'):
    print('has summary stats table')
    summary_stats_table = pd.read_sql_table('summary_stats_table', engine_summary_stats)'''
if not summary_stats_table_list:
    raise Exception('NO SUMMARY STATS')
summary_stats_table = pd.concat(table for table in summary_stats_table_list)



Stimulators_list = [1,2,3]
idx = 0
shorted_harvard_df = pd.DataFrame()

for harvard in Stimulators_list: 
    key = f'Harvard {harvard} Shorted'
    plate_rows = summary_stats_table.loc[summary_stats_table['plate_id'] == key]
    most_recent_values = plate_rows.sort_values(by='day_time', ascending=False).head(2)
    row1 = most_recent_values.iloc[0]

    voltage = float(row1['pos peaks mean(V)']) if row1['pos peaks mean(V)'] else np.nan
    stimFreq = row1['frequency(Hz)']
    pulseOn = row1['pulseDuration'] * 1000

    print(voltage, stimFreq, pulseOn)

    shorted_harvard_df.at[idx, 'id'] = idx 
    shorted_harvard_df.at[idx, 'Stimulator'] = harvard 
    shorted_harvard_df.at[idx, 'voltage'] =  round(voltage, 4) 
    shorted_harvard_df.at[idx, 'stimFreq'] = stimFreq
    shorted_harvard_df.at[idx, 'pulseOn'] = pulseOn

    idx += 1

print(shorted_harvard_df)
shorted_harvard_df.to_sql('shorted_harvards', con=engine_app_data, if_exists='replace', index=False)

