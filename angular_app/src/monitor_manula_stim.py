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
current_date = datetime.now().date()
start_of_day = datetime.combine(current_date, dt_time())

# Read Variables 
pulse_interval = 10
read_frequency = 4000
dt_read = 1 / read_frequency
samples_per_interval = pulse_interval * read_frequency
buffer_time = 7 # s
buffer_size_samples = int(read_frequency * buffer_time)
t_sampling = 12 * 60 * 60

# Read Data Variables
pulse_data_path = "pulse_data_3.tdms"
channels = [input.split('/')[1] for input in stim_channels_dict.keys()]
channel_list = ", ".join([f"{'Dev3'}/{channel}" for channel in channels])

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
        print(f"READ TASK COMPLETED AT {time.ctime(time.time())}")

print(f"\nDATA PROCESSING STARTED AT {time.ctime(time.time())}")
# Start the dat processing step
pulse_data_file = TdmsFile.read(pulse_data_path)
# Extract the data from the singular group and channel
pulse_channels = pulse_data_file.groups()[0].channels()
pulse_channels_data_dict = {}

for i, channel in enumerate(pulse_channels): 
    data = channel.data
    pulse_channels_data_dict[channel.name] = data

num_samples = len(list(pulse_channels_data_dict.values())[0])
print(f"DATA SUCESSFULLY READ INTO ARRAYS OF SIZE : {num_samples} AT {time.ctime(time.time())}\n")

stop = t_start + num_samples * dt_read
# Create the time array
# Synthesized time data using start time, calculated stop time, and the read frequency
# Should all have the same time data
time_array = np.arange(start=t_start, stop=stop, step=dt_read)

for key, y in pulse_channels_data_dict:
    sns.scatterplot(x = time_array, y = y, s = 5, color = 'red', label = f'{key}', alpha = .5)
plt.legend()
plt.show()








