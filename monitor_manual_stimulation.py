import json
import warnings
from scipy.optimize import OptimizeWarning
import pandas as pd
from sqlalchemy import create_engine, inspect
from sklearn.linear_model import LinearRegression
import mysql.connector
import numpy as np
import sys
import matplotlib.pyplot as plt
from datetime import timedelta
import scipy
from scipy import integrate
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
from nidaqmx.stream_writers import DigitalSingleChannelWriter
from nidaqmx.stream_readers import AnalogMultiChannelReader
from nidaqmx.stream_readers import AnalogSingleChannelReader
from nidaqmx.constants import AcquisitionType, Edge, LoggingMode, LoggingOperation, READ_ALL_AVAILABLE
from nptdms import TdmsFile
import scipy.stats as stats
import seaborn as sns
from scipy.optimize import curve_fit
from scipy.optimize import least_squares

# Channels 
stim_channels_dict = {}
stim_channels_dict['Dev3/ai16'] = 'Lead_7_8'
stim_channels_dict['Dev3/ai17'] = 'Lead_9_10'

# Time Variables
datetime_start = datetime.now()
current_date = datetime.now().date()
start_of_day = datetime.combine(current_date, dt_time())

# Read Variables 
pulse_interval = 10
read_frequency = 4000
dt_read = 1 / read_frequency
samples_per_interval = pulse_interval * read_frequency
buffer_time = 7 # s
buffer_size_samples = int(read_frequency * buffer_time)
t_sampling = 12 * 60 * 60 # 12 hours / run * 60 minutes / hour * 60 seconds / minute

#SQL Credentials 
username = 'nallen'
password = 'wtQGQ6EX.*zA6Zh'
host = '10.10.100.41'

# Read Data Variables
pulse_data_path = "pulse_data_3.tdms"
channels = [input.split('/')[1] for input in stim_channels_dict.keys()]
channel_list = ", ".join([f"{'Dev3'}/{channel}" for channel in channels])

# Functions
def save_local(table_name, df, output_dir):
    print('\nWriting table to local storage...')
    if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    try: 
        sql_out_file = output_dir + f'{table_name}.csv'
        if os.path.exists(sql_out_file):
            os.remove(sql_out_file)
        df.to_csv(sql_out_file, index=True)
    except: 
        sql_out_file = output_dir + f'{table_name}_' + datetime.now().isoformat()[:10] + '.csv'
        if os.path.exists(sql_out_file):
            os.remove(sql_out_file)
        df.to_csv(sql_out_file, index=True)
    print(f'\nLOCAL COPY OF {sql_out_file} STORED AT {output_dir}\n')

def add_rows(engine, table_name, df : pd.DataFrame, chunk_size = 10000):
    print(f'adding rows to {table_name}')
    try:
        chunks = pd.read_sql_table(table_name, engine, chunksize=chunk_size)
        existing_df = pd.concat(chunk for chunk in chunks)
        print("\nDataFrame successfully loaded with shape:", existing_df.shape)
    except Exception as e:
        print("Error reading the table:", e)
    # existing_df = pd.read_sql_table(table_name, engine)

    # Find columns that are in one DataFrame but not the other
    existing_cols = set(existing_df.columns)
    new_cols = set(df.columns)
    
    cols_to_add_to_existing = new_cols - existing_cols
    cols_to_add_to_new = existing_cols - new_cols
    
    # Add missing columns with pd.NA values
    for col in cols_to_add_to_existing:
        existing_df[col] = pd.NA
    for col in cols_to_add_to_new:
        df[col] = pd.NA
    
    # Ensure both DataFrames have the same columns in the same order
    # df = df[existing_df.columns]
    
    # Concatenate DataFrames
    combined_df = pd.concat([existing_df, df], axis = 0).reset_index(drop = True)
    output_dir = 'C:\\Users\\microscope\\Desktop\\SkeletalStimLogs\\Manual_Stim_Logs\\'

    save_local(table_name, combined_df, output_dir)

    try:
        for i in range(0, combined_df.shape[0], chunk_size):
            chunk = combined_df.iloc[i:i + chunk_size]
            if i == 0:
                chunk.to_sql(table_name, engine, if_exists='replace', index=False)
            else:
                chunk.to_sql(table_name, engine, if_exists='append', index=False)
        print("\nDataFrame successfully uploaded in chunks.")
    except Exception as e:
        print("Error uploading the DataFrame:", e)
    
def create_new_table(engine, table_name, df : pd.DataFrame, chunk_size = 10000):
    print(f'\nCREATING {table_name}\n')
    pool = engine.pool
    print(pool.status())

    # Writing to computer to ensure
    output_dir = 'C:\\Users\\microscope\\Desktop\\SkeletalStimLogs\\Manual_Stim_Logs\\'
    save_local(table_name, df, output_dir)

    try:
        for i in range(0, df.shape[0], chunk_size):
        # for i in range(0, df.shape[0], df):
            chunk = df.iloc[i:i + chunk_size]
            if i == 0:
                chunk.to_sql(table_name, engine, if_exists='replace', index=False)
            else:
                chunk.to_sql(table_name, engine, if_exists='append', index=False)
        print("\nDataFrame successfully uploaded in chunks.")
    except Exception as e:
        print("Error uploading the DataFrame:", e)

def process(data_dict): 
    for database_name, df in data_dict.items():
        engine = create_engine(f'mysql+mysqlconnector://{username}:{password}@{host}/{database_name}', pool_size=400, max_overflow=800, 
                               connect_args={
                                   'connect_timeout' : 60,
                               })
        table = database_name + '_manual_table'
        inspector = inspect(engine) 
        if inspector.has_table(table): 
            add_rows(engine, table, df)
        else: 
            create_new_table(engine, table, df)

def detect_peaks(interval, threshold, positive):
    peaks = []
    pulse_list = []
    all = []
    i = 0
    while i < len(interval):
        if (interval[i] > threshold and positive) or (interval[i] < -threshold and not positive):
            samples = []
            while i < len(interval) and ((interval[i] > threshold and positive) or (interval[i] < -threshold and not positive)):
                samples.append(i)
                i += 1
            if len(samples) > 5:
                if positive:
                    peak_index = max(samples, key=lambda x: interval[x])
                else:
                    peak_index = min(samples, key=lambda x: interval[x])
                peaks.append(peak_index)
                pulse_list.append(samples)
                all += samples
        else:
            i += 1
    return peaks, pulse_list, all

# The Run
with nidaqmx.Task() as readtask:
    readtask.ai_channels.add_ai_voltage_chan(channel_list)
    readtask.timing.cfg_samp_clk_timing(read_frequency, sample_mode=AcquisitionType.CONTINUOUS)
    readtask.in_stream.configure_logging(pulse_data_path, LoggingMode.LOG_AND_READ, operation=LoggingOperation.CREATE_OR_REPLACE)
    readtask.in_stream.input_buf_size = buffer_size_samples
    # multichannel reader 
    reader = AnalogMultiChannelReader(readtask.in_stream)
    readtask.start()
    print(f"READ TASK STARTED AT {time.ctime(time.time())}")
    print(f"\nMONITORING MANUAL STIMULATION UNTIL : {time.ctime(time.time() + t_sampling)}\nCurrently pulsing and collecting data... \n")

    try : 
        # seconds at this momment
        t_track = time.time() 
        # Seconds since the start of the day 
        t_start = t_track - start_of_day.timestamp()
        while (time.time() - start_of_day.timestamp()) - t_start < t_sampling: 
            data = np.zeros((len(channels), buffer_size_samples), dtype=np.float64)
            reader.read_many_sample(data, number_of_samples_per_channel=buffer_size_samples, timeout=10.0)
    except KeyboardInterrupt:
        print("Data acquisition stopped. Read tasks terminated.")
    finally:
        # Stop the read tasks after all data has been uploaded the hard drive
        readtask.stop()
        datetime_end = datetime.now()
        print(f"READ TASK COMPLETED AT {time.ctime(time.time())}")

print(f"\nDATA PROCESSING STARTED AT {time.ctime(time.time())}")
# Start the dat processing step
pulse_data_file = TdmsFile.read(pulse_data_path)
# Extract the data from the singular group and channel
pulse_channels = pulse_data_file.groups()[0].channels()
pulse_channels_data_dict = {}
time_dict = {}
for i, channel in enumerate(pulse_channels): 
    first = 0
    first_peak_seen = False
    last = 0 
    data = []
    for i, v in enumerate(channel.data):
        if abs(v) > .01:
            if not first_peak_seen : first = i
            first_peak_seen = True
            if abs(v) > .8: 
                v1 = v / 2 
                v2 = v / 2
                data.append(v1) 
                data.append(v2)
            else: 
                data.append(v)
            last = i

    t_samp = (last - first) / read_frequency

    num_samples = len(data)
    stop = t_start + num_samples * dt_read
    time_array = np.arange(start = t_start, stop = stop, step = dt_read)
    minlength = min([len(time_array), len(data)])
    x_y = (np.array(time_array[:minlength]), np.array(data[:minlength]))
    pulse_channels_data_dict[channel.name] = x_y
    time_dict[channel.name] = t_samp

colors = ["blue", "green", "red", "black", "orange"]
data_frame_dict = {}
data_frame_dict['summary_stats'] = pd.DataFrame()
# data_frame_dict['voltage'] = pd.DataFrame()

for i, (key, (time_array, y)) in enumerate(pulse_channels_data_dict.items()):

    # voltage_data = pd.DataFrame()

    pos_peaks_idxs, pos_peaks_idx_lists, all_pos_idxs = detect_peaks(y, .1, True)
    neg_peaks_idxs, neg_peaks_idx_lists, all_neg_idxs = detect_peaks(y, .1, False)

    if pos_peaks_idx_lists and neg_peaks_idxs:
        num_pos_peaks = len(pos_peaks_idxs)
        num_neg_peaks = len(neg_peaks_idxs)
        avg_pos_voltage = np.mean(y[all_pos_idxs])
        avg_neg_voltage = np.mean(y[all_neg_idxs])
        pos_pulse_max = max(y[all_pos_idxs])
        neg_pulse_max = min(y[all_neg_idxs])
        pos_peaks_std = np.std(y[pos_peaks_idxs])
        neg_peaks_std = np.std(y[all_neg_idxs])
        pos_pulse_duration = (np.mean([len(pulse) for pulse in pos_peaks_idx_lists]) / read_frequency) * 1000 
        neg_pulse_duration = (np.mean([len(pulse) for pulse in neg_peaks_idx_lists]) / read_frequency) * 1000
        t_samp = time_dict[key]
        stim_freq =  (len(pos_peaks_idxs) / t_samp) * 10
    else : 
        num_pos_peaks = np.nan
        num_neg_peaks = np.nan
        avg_pos_voltage = np.nan
        avg_neg_voltage = np.nan
        pos_pulse_max = np.nan
        neg_pulse_max = np.nan
        pos_peaks_std = np.nan
        neg_peaks_std = np.nan
        pos_pulse_duration = np.nan
        neg_pulse_duration = np.nan
        stim_freq =  np.nan
            
    summary_data_dict = {
        'ID' : 0,
        'Stimulator' : stim_channels_dict[key], 
        'Day Time Start' : datetime_start,
        'Day Time End' : datetime_end,
        'Stim Time' : t_samp,
        'Stim Frequency' : stim_freq,
        'Num Pos Peaks' : num_pos_peaks,
        'Num Neg Peaks' : num_neg_peaks, 
        'Average Pos Voltage (V)' : avg_pos_voltage * 10, 
        'Average Neg Voltage (V)' : avg_neg_voltage * 10, 
        'Pos Pulse Max (V)' : pos_pulse_max * 10, 
        'Neg Pulse Max (V)' : neg_pulse_max * 10, 
        'Pos Peaks std (V)' : pos_peaks_std * 10, 
        'Neg Peaks std (V)' : neg_peaks_std * 10, 
        'Pos Pulse Duration (ms)' : pos_pulse_duration, 
        'Neg Pulse Duration (ms)' : neg_pulse_duration,
    }

    summary_df = pd.DataFrame(summary_data_dict, index = [0])
    
    # index_ = ['Stimulator', 'Day Time Start', 'Day Time End', 'Type' ] + [i for i in range(len(y)) ]
    # t = [f'{key}', f'{datetime_start}', f'{datetime_end}', 'Time (s)']
    # v = [f'{key}', f'{datetime_start}', f'{datetime_end}', 'Voltage (s)']
    # voltage_data = pd.DataFrame({
    #     'ID' : index_, f'col_{i}_t' : t, f'col_{i}_v' : v
    # }).set_index('ID')
    
    # if i == 0 : 
    #     merged_volt = voltage_data
    # else:
    #     existing_df_volt = data_frame_dict['voltage'].set_index('ID')
    #     merged_volt = pd.concat([existing_df_volt, voltage_data], axis = 1)
    
    # data_frame_dict['voltage'] = merged_volt.reset_index()
    data_frame_dict['summary_stats'] = pd.concat([data_frame_dict['summary_stats'], summary_df], ignore_index = True)

#     sns.scatterplot(x = time_array, y = y, s = 20, color = colors[i], label = f'{key}')
# plt.legend()
# plt.show()

process(data_frame_dict)