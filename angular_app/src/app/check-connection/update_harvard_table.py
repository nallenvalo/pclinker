
import json
import pandas as pd
from sqlalchemy import create_engine, inspect
from datetime import timedelta
import numpy as np
import time
from datetime import datetime, date, time as dt_time

username = 'nallen'
password = 'wtQGQ6EX.*zA6Zh'
host = '10.10.100.41'

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
print(summary_stats_table)