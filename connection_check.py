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
from nidaqmx.stream_writers import DigitalSingleChannelWriter
from nidaqmx.stream_readers import AnalogMultiChannelReader
from nidaqmx.stream_readers import AnalogSingleChannelReader
from nidaqmx.constants import AcquisitionType, Edge, LoggingMode, LoggingOperation, READ_ALL_AVAILABLE
from nptdms import TdmsFile
import scipy.stats as stats
import seaborn as sns
from sqlalchemy import text

if len(sys.argv) > 1:
    # The first command line argument
    harvard = sys.argv[1]
    
    # Ensure harvard is either 0 or 1
    if harvard in ['1', '2', '3']:
        harvard = int(harvard)  # Convert to integer for further processing if needed
        print(f"The value of harvard is: {harvard}")
    else:
        raise Exception(f' first argument, {harvard}, must be either 1, 2, 3')
else:
    raise Exception("No command line arguments were provided.")

username = 'nallen'
password = 'wtQGQ6EX.*zA6Zh'
host = '10.10.100.41'

engine_app_data = create_engine(f'mysql+mysqlconnector://{username}:{password}@{host}/app_data', pool_size=400, max_overflow=800)
inspector = inspect(engine_app_data) 
if inspector.has_table('check_logs'):
    print('CHECK LOGS TABLE FOUND')
    check_log_data = pd.read_sql_table('check_logs', engine_app_data)
else : 
    raise Exception('NO CHECK LOGS')

print(check_log_data)

if harvard == 1 : 
    resistance = 10 # ohms
    v_stim = 5
    peak = .5
    npeak = .5
    StimShortedChannel = 'ai6'
    port = 'port0'
    device = 'Dev3'
    line = 'line0'
    n = 1
elif harvard == 2:
    resistance = 10 # ohms
    v_stim = 5
    peak = .5
    npeak = .5
    StimShortedChannel = 'ai0'
    port = 'port0'
    device = 'Dev1'
    line = 'line0'
    n = 1
elif harvard == 3:
    resistance = 10 # ohms
    v_stim = 5
    peak = .5
    npeak = .5
    StimShortedChannel = 'ai0'
    port = 'port0'
    device = 'Dev1'
    line = 'line8'
    n = int(2 ** 8)
elif harvard == 4: 
    resistance = 10 # ohms
    v_stim = 5
    peak = .5
    npeak = .5
    StimShortedChannel = 'ai0'
    port = 'port0'
    device = 'Dev3'
    line = 'line8'
    n = int(2 ** 8)

HA_Channel_To_Ai_dict = {
                        (1,1) : f'{device}/ai7',
                         (1,2) : f'{device}/ai6',
                         (1,3) : f'{device}/ai5',
                         (1,4) : f'{device}/ai4',
                        (1,5) : f'{device}/ai3',
                        (1,6) : f'{device}/ai2',
                        (1,7) : f'{device}/ai1',
                         (2,1) : f'{device}/ai7',
                         (2,2) : f'{device}/ai6',
                         (2,3) : f'{device}/ai5',
                         (2,4) : f'{device}/ai4',
                         (2,5) : f'{device}/ai5',
                         (2,6) : f'{device}/ai6',
                         (2,7) : f'{device}/ai7',

                         (3,1) : f'{device}/ai17',
                         (3,2) : f'{device}/ai18',
                         (3,3) : f'{device}/ai19',
                         (3,4) : f'{device}/ai20',
                         (3,5) : f'{device}/ai21',
                         (3,6) : f'{device}/ai22',
                         (3,7) : f'{device}/ai23'

                        }


plate_channels_dict = {}
# plate_channels_dict[f'{device}/ai0'] = f'Harvard {harvard} Shorted'
for i, row in check_log_data.iterrows():
    harvard_ = row['harvardAparatus']
    if harvard == harvard_:
        Channel = row['Channel']
        plateName = row['plateName']
        key = HA_Channel_To_Ai_dict[(harvard_, Channel)]
        print(f'(HA, Channel : AI) --> ({harvard_}, {Channel}) : {key}')
        print(f'AnalogIn, plate --> ({key} : {plateName})')
        plate_channels_dict[key] = plateName

print(plate_channels_dict)

if not plate_channels_dict: 
    print(f'No plates on harvard aparatus {harvard}')
    sys.exit(1)

# Channels for reading
channels = [input.split('/')[1] for input in plate_channels_dict.keys()]
# channels = ['ai0', 'ai2', 'ai4', 'ai6', 'ai8']
HA_channels = []
# channels = [channel for channel in channels if channel not in HA_channels]
channel_list = ", ".join([f"{device}/{channel}" for channel in channels])

# TDMS file that we will read the data into 
read_frequency = 10000
f_sampling = 1000
t_sampling = 2
f_stimulation = 1
dt_read = 1 / read_frequency
n_sampling = f_sampling * t_sampling
buffer_size_samples = read_frequency * 2 * t_sampling
pulse_on_length = 1
pulse_off_length = t_sampling - pulse_on_length
num = 4 if line == 'line2' else 1 if line == 'line0' else 0
pulse_data_path = "check_data.tdms"
resistance = 10

pulse_train = np.zeros(n_sampling, dtype=np.uint32)
pulse_intervals = np.arange(0, n_sampling, f_sampling // f_stimulation)
pulse_train[pulse_intervals] = num
pulse_on_off_single = np.concatenate((np.ones(pulse_on_length * f_sampling, dtype=np.uint32),
np.zeros(pulse_off_length * f_sampling, dtype=np.uint32)))
pulse_on_off = np.tile(pulse_on_off_single, n_sampling // len(pulse_on_off_single) + 1)[:n_sampling]
pulse_train *= pulse_on_off
print("pulse_train : ", pulse_train)

#2 ============================= NIDAQ SETUP AND RUN ===================================
with nidaqmx.Task() as writetask, nidaqmx.Task() as readtask:

    current_date = datetime.now().date()
    start_of_day = datetime.combine(current_date, dt_time())

    writetask.do_channels.add_do_chan(f'/{device}/port0/{line}')
    writetask.timing.cfg_samp_clk_timing(f_sampling, sample_mode=AcquisitionType.FINITE, samps_per_chan=n_sampling)
    writer = DigitalSingleChannelWriter(writetask.out_stream, auto_start=False)
    writer.write_many_sample_port_uint32(pulse_train)

    # SETUP: Analog Input reader TDMS Reader
    readtask.ai_channels.add_ai_voltage_chan(channel_list)
    readtask.timing.cfg_samp_clk_timing(read_frequency, sample_mode=AcquisitionType.CONTINUOUS)
    readtask.in_stream.configure_logging(pulse_data_path, LoggingMode.LOG_AND_READ, operation=LoggingOperation.CREATE_OR_REPLACE)
    readtask.in_stream.input_buf_size = buffer_size_samples
    # multichannel reader 
    reader = AnalogMultiChannelReader(readtask.in_stream)

    # Start the read Task
    # The read task will take time t_sampling
    readtask.start()
    print(f"READ TASK STARTED AT {time.ctime(time.time())}")
    # Wait until we finish writing before we read.
    # The write task will take time t_sampling
    writetask.start()
    print(f'WRITE TASK STARTED AT {time.ctime(time.time())}')
    print(f"\nEXPECTED COMPLETION : {time.ctime(time.time() + t_sampling)}\nCurrently pulsing and collecting data... \n")
    
    # Loop until we have passed the sampling time
    try : 
        # need to subtract from start of the epoch
        t_track = time.time() # seconds at this momment
        # start_of_day.timestamp()) seconds at the start of the day
        t_start = t_track - start_of_day.timestamp() # Seconds since the start of the day 
        while (time.time() - start_of_day.timestamp()) - t_start < t_sampling: 
            data = np.zeros((len(channels), buffer_size_samples), dtype=np.float64)
            reader.read_many_sample(data, number_of_samples_per_channel=buffer_size_samples, timeout=10.0)
    # Handle the case where we exit code in the midst of hard drive upload
    except KeyboardInterrupt:
        print("Data acquisition stopped. Read and Write tasks terminated.")
    finally:
        # Stop the read tasks after all data has been uploaded the hard drive
        readtask.stop()
        print(f"WRITE TASK COMPLETE AT {time.ctime(time.time())}")
        print(f"READ TASK COMPLETED AT {time.ctime(time.time())}")

pulse_data_file = TdmsFile.read(pulse_data_path)
# Extract the data from the singular group and channel
pulse_channels = pulse_data_file.groups()[0].channels()
pulse_channels_data_dict = {}

for i, channel in enumerate(pulse_channels): 
    data = channel.data
    pulse_channels_data_dict[channel.name] = data

num_samples = len(list(pulse_channels_data_dict.values())[0])
stop = t_start + num_samples * dt_read
time_array = np.arange(start=t_start, stop=stop, step=dt_read)

# All should be the same length in theory 
table_connection = mysql.connector.connect(
    host = host, 
    user = username, 
    password = password,
    database =  'app_data'
    )
mycursor = table_connection.cursor()
prev = 0
for key, val in pulse_channels_data_dict.items(): 
    # sns.scatterplot(x = time_array, y = val)
    # plt.show()
    plate_id = plate_channels_dict[key]
    peaks = [k for k in val if k > .5]
    neg_peaks = [np.float64(-1)] * 20  #[k for k in val if k < -.1]# [np.float64(-1)] * 20 
    real_pulse = False
    current = (max(val) / resistance) * 1000
    if peaks :
        print(len(neg_peaks))
        print(len(peaks))
        print(peaks)
        real_pulse = len(peaks) > 10 and len(neg_peaks) > 10 and len(peaks) < 25 and len(peaks) < 25
        if real_pulse : current = (np.mean(peaks) / resistance) * 1000
        # If we have peaks but not a real pulse we do not want to report this data
        else: current = 0
    try:
    # Prepare the update query with key-value pairs from `row` dictionary
        if peaks and neg_peaks and real_pulse: 
            sql_update_query_stim = f"UPDATE check_logs SET Stimulating = 1 WHERE plateName = '{plate_id}'"
        else : 
            sql_update_query_stim = f"UPDATE check_logs SET Stimulating = 0 WHERE plateName = '{plate_id}'"
        sql_update_query_ran = f"UPDATE check_logs SET ranCheck = 1 WHERE plateName = '{plate_id}'"
        sql_update_query_current = f"UPDATE check_logs SET current = {current} WHERE plateName = '{plate_id}'"
        mycursor.execute(sql_update_query_stim)
        mycursor.execute(sql_update_query_ran)
        mycursor.execute(sql_update_query_current)
        table_connection.commit()
    except Exception as e:
        print(f"Query Failed: {e}")

    print(pd.read_sql_table('check_logs', engine_app_data))
