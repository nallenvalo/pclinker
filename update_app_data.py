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

# print(summary_stats_table)
# Have to check the plates and have to check the start and endtime of the plates to a list of active plates
# Will Use harvard aparatus and channel number in the other file in order to get analog input
# print(plate_log_data.columns)
all_plates = plate_log_data['plateName']
# print(all_plates)
active_plates = []
for plate in all_plates: 
    row = plate_log_data.loc[plate_log_data['plateName'] == plate]
    start_date = row['stimulation_start'].iloc[0]
    end_date = row['stimulation_end'].iloc[0]
    if start_date < now: # and end_date > now: 
        active_plates.append(plate)
# print(active_plates)

# Need to get the data from the morning and write it into the SQL Table at the proper places 
'''
'id', 'name', 'pulseOnLength', 'HarvardAparatus', 'Channel', 'cycleLength', 'plateName', 'stimFreq', 'timeSampling', 
'stimulation_start', 'stimulation_end', 'pharmacological', 

'Report_time1', 'voltage1', 'pulseDuration1', 'frequency1', 
'current1', 'charge1', 'chargeDifference1', 'maturationPercentage1', 'energy1', 'rms1', 'Report_time2', 'voltage2', 
'pulseDuration2', 'frequency2', 'current2', 'charge2', 'chargeDifference2', 'maturationPercentage2', 'energy2', 'rms2'
'''

# Need to get the data from the prior night and write it into the SQL Table at the proper places 
'''
'day_time', 'date', 'period', 'plate_id', 'mean', 'median', 'std', 'variance', 'min', 'max', 'range', 'rms', 'snr', 'energy', 
'pos peaks count', 'pos peaks mean', 'pos peaks median', 'pos peaks std', 'pos peaks min', 'pos peaks max', 'neg peaks count', 
'neg peaks mean', 'neg peaks median', 'neg peaks std', 'neg peaks min', 'neg peaks max'
'''
# print(summary_stats_table.columns)
# print('summary stats daytime values : ', summary_stats_table['day_time'])
for plate in active_plates:
    # Find the two most recent values
    row_ = plate_log_data.loc[plate_log_data['plateName'] == plate]
    plate_rows = summary_stats_table.loc[summary_stats_table['plate_id'] == plate]
    most_recent_values = plate_rows.sort_values(by='day_time', ascending=False).head(2)

    if len(most_recent_values) == 2:
        row1 = most_recent_values.iloc[0]
        row2 = most_recent_values.iloc[1]
        '''print(f"Two most recent values for plate {plate}:")
        print("Row 1:")
        print(row1)
        # print("Row 2:")
        # print(row2)'''
        # may have to rethink what format to use
        Report_time1 = row1['day_time']
        voltage1 = row1['pos peaks mean']
        pulseDuration1 = row1['pulseDuration']
        frequency1 = row1['frequency']
        current1 = row1['avg pos current']
        chargeDifference1 = row1['full charge difference']# row1['pos charge'] - row1['neg charge']
        charge1 = row1['pos charge']
        energy1 = row1['energy']
        rms1 = row1['rms']
        Report_time2 = row2['day_time']
        voltage2 = row2['pos peaks mean']
        pulseDuration2 = row2['pulseDuration']
        frequency2 = row2['frequency']
        current2 = row2['avg pos current']
        chargeDifference2  = row2['full charge difference'] # row2['pos charge'] - row2['neg charge']
        charge1 = row2['pos charge']
        energy2 = row2['energy']
        rms2 = row1['rms']

        plate_log_data.loc[plate_log_data['plateName'] == plate, 'Report_time1'] = Report_time1
        plate_log_data.loc[plate_log_data['plateName'] == plate, 'voltage1'] = round(voltage1, 4)
        plate_log_data.loc[plate_log_data['plateName'] == plate, 'energy1'] = round(energy1, 3)
        plate_log_data.loc[plate_log_data['plateName'] == plate, 'rms1'] = round(rms1, 3)
        plate_log_data.loc[plate_log_data['plateName'] == plate, 'frequency1'] = round(frequency1, 3)
        plate_log_data.loc[plate_log_data['plateName'] == plate, 'current1'] = round(current1, 1)
        plate_log_data.loc[plate_log_data['plateName'] == plate, 'pulseDuration1'] = round(pulseDuration1, 3)
        plate_log_data.loc[plate_log_data['plateName'] == plate, 'chargeDifference1'] = round(chargeDifference1, 3)
        
        plate_log_data.loc[plate_log_data['plateName'] == plate, 'Report_time2'] = Report_time2
        plate_log_data.loc[plate_log_data['plateName'] == plate, 'voltage2'] = round(voltage2, 3)
        plate_log_data.loc[plate_log_data['plateName'] == plate, 'energy2'] = round(energy2, 3)
        plate_log_data.loc[plate_log_data['plateName'] == plate, 'rms2'] = round(rms2, 3)
        plate_log_data.loc[plate_log_data['plateName'] == plate, 'frequency2'] = round(frequency2, 3)
        plate_log_data.loc[plate_log_data['plateName'] == plate, 'current2'] = round(current2, 1)
        plate_log_data.loc[plate_log_data['plateName'] == plate, 'pulseDuration2'] = round(pulseDuration1, 3)
        plate_log_data.loc[plate_log_data['plateName'] == plate, 'chargeDifference2'] = round(chargeDifference2, 3)
    else:
        print(f"Not enough data for plate {plate} to find two most recent values.")

# Need to update the variables json data
# SQL drops the index column and will leads to errors when we try to read the model
# App data data frame is not an accurate representation
# plate_log_data['id'] = range(0, len(plate_log_data))
# plate_log_data.drop(columns=['id'])
# plate_log_data.reset_index(inplace=True)
plate_log_data.to_sql('plate_log_data', con=engine_app_data, if_exists='replace', index=False)
print("LOADED TO PLATE LOGS")
output_dir = 'C:\\Users\\microscope\\Desktop\\SkeletalStimLogs\\App_Data\\'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
sql_out_file = output_dir + f'plate_log_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
if os.path.exists(sql_out_file):
    os.remove(sql_out_file)
plate_log_data.to_csv(sql_out_file, index=True)

# print(variables)
plate_dict = {}
vars = ['pulseOnLength', 'HarvardAparatus', 'Channel', 'cycleLength', 'stimFreq', 'timeSampling', 'stimulation_start', 'stimulation_end'] 

for plate in active_plates: 
    plate_dict[plate] = {}
    row = plate_log_data.loc[plate_log_data['plateName'] == plate].iloc[0]
    # print(row)
    for var in vars: 
        if 'stimulation' in var:
             plate_dict[plate][var] = row[var].isoformat()
        else:
            plate_dict[plate][var] = row[var].item() if hasattr(row[var], 'item') else row[var]

with open('variables.json', 'w') as file:
    json.dump(plate_dict, file, indent=4)

print("JSON file has been updated.")

    
    