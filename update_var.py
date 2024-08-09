import json
import pandas as pd
from sqlalchemy import create_engine, inspect
import mysql.connector
import numpy as np
import sys
import matplotlib.pyplot as plt
from datetime import timedelta
import scipy
import numpy as geek 
import logging
from tabulate import tabulate
import os
from sqlalchemy.pool import Pool
from sqlalchemy import event
import time
import time
from datetime import datetime, date, time as dt_time
import nidaqmx
import matplotlib.pyplot as plt

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

all_plates = plate_log_data['plateName']
# print(all_plates)
active_plates = []
for plate in all_plates: 
    row = plate_log_data.loc[plate_log_data['plateName'] == plate]
    start_date = row['stimulation_start'].iloc[0]
    end_date = row['stimulation_end'].iloc[0]
    if start_date < now and end_date > now: 
        active_plates.append(plate)

plate_dict = {}
vars = ['pulseOnLength', 'HarvardAparatus', 'Channel', 'cycleLength', 'stimFreq', 'timeSampling'] 

for plate in active_plates: 
    plate_dict[plate] = {}
    row = plate_log_data.loc[plate_log_data['plateName'] == plate].iloc[0]
    # print(row)
    for var in vars: 
        plate_dict[plate][var] = row[var].item() if hasattr(row[var], 'item') else row[var]

with open('variables.json', 'w') as file:
    json.dump(plate_dict, file, indent=4)

print("STIMULATION PARAMETERS UPDATED")