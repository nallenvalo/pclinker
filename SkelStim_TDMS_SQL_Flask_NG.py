'''
Nicholas Allen, Brian Schriver 

Valo Health
Date started : 6 / 25 / 24
Date last modified  : 8 / 12 / 24

This code reads multiple input channels from multiple Digital Acquisition Boards and passes them all into the computer's hard drive. 
After passing into the hard drive, we read the data out and organize the full reads into dictionaries organized by channels. We
make dataframes based off the channels, one for the full current, one for the full voltage, one for summary stats, and one for cycle
stats. We identify columns for voltage and current by plate_id, date, date_time, period, and type. We identify rows in the stats
by date, date_time, and period. We then write these data frames back into SQL, either creating new one, or, more often, reading into the 
dataframe that is currently in SQL, appending the information, and doing checks for any additional rows and columns, and passing this information
back into SQL. We read in chunks so as to not yield a data overload. Furthermore, every year, we will create new tables in SQL for the 
items we are organizing.
'''
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

if len(sys.argv) > 1:
    # The first command line argument
    harvard = sys.argv[1]
    
    # Ensure harvard is either 0 or 1
    if harvard in ['1', '2']:
        harvard = int(harvard)  # Convert to integer for further processing if needed
        print(f"The value of harvard is: {harvard}")
    else:
        raise Exception(f' first argument, {harvard}, must be either 1 or 2')
else:
    raise Exception("No command line arguments were provided.")

with open("update_var.py") as f:
    code = f.read()
    exec(code)

with open('variables.json', 'r') as file:
    variables = json.load(file)

# Get start time
# will use this to parse that dictionary of plates and channels at the start
# If outside the range, we delete if in. if inside the range, we add and use the 
# HA, channel pair to map to an analog input, will have to decide on this once it is hooked up. 
# Can eventually add change times for frquenies, if datetime larger than > we change the main freq
# number to something else
datetime_start = datetime.now()

# Determine what period, if it is night or day
period = "AM" if datetime.now().hour < 12 else "PM"
#1) ====================VARIABLES==============================

resistance = 10 # ohms
peak = .5
# Dictionary for Channels f
# To be modified via the webapp 
# Have cases with the blank data frame for the largest number of plates
device = 'Dev3' if harvard == 1 else 'Dev1' if harvard == 2 else ''
# Add Logic once we add in another harvard aparatus 
line = 'line2' if harvard == 1 else 'line0' if harvard == 2 else ''
# This will be hard coded and predetermined 
HA_Channel_To_Ai_dict = {
                        (1,1) : f'{device}/ai1',
                         (1,2) : f'{device}/ai2',
                         (1,3) : f'{device}/ai3',
                         (1,4) : f'{device}/ai4',
                         (1,5) : f'{device}/ai5',
                         (1,6) : f'{device}/ai6',
                         (1,7) : f'{device}/ai7',
                         (2,1) : f'{device}/ai1',
                         (2,2) : f'{device}/ai2',
                         (2,3) : f'{device}/ai3',
                         (2,4) : f'{device}/ai4',
                         (2,5) : f'{device}/ai5',
                         (2,6) : f'{device}/ai6',
                         (2,7) : f'{device}/ai7',
                        }

#defaults 
f_sampling = 1000 # Hz
t_sampling = 60 * 60 * 1 # 1 HR
pulse_on_length = 1 # 
pulse_off_length = 9 # s
f_stimulation = 10 # Hz

plate_channels_dict = {}
plate_channels_dict[f'{device}/ai0'] = f'Harvard {harvard} Shorted'
for plate, vars_dict in variables.items(): 
    HarvardAparatus = vars_dict['HarvardAparatus']
    Channel = vars_dict['Channel']
    if harvard == HarvardAparatus:
        key = HA_Channel_To_Ai_dict[(HarvardAparatus, Channel)]
        print(f'(HA, Channel : AI) : ({HarvardAparatus}, {Channel}) : {key}')
        t_sampling = vars_dict['timeSampling']
        pulse_on_length = vars_dict["pulseOnLength"]
        pulse_off_length = vars_dict["cycleLength"] - vars_dict["pulseOnLength"]
        f_stimulation = int(vars_dict["stimFreq"])
        print(f'AnalogIn, plate : ({key} : {plate})')
        plate_channels_dict[key] = plate
print(plate_channels_dict)

if not plate_channels_dict: 
    print(f'No plates on harvard aparatus {harvard}')
    sys.exit(1)

n_sampling = f_sampling * t_sampling
dt_stimulation = 1/f_stimulation
    
# Channels for reading
channels = [input.split('/')[1] for input in plate_channels_dict.keys()]
# channels = ['ai0', 'ai2', 'ai4', 'ai6', 'ai8']
HA_channels = []
# channels = [channel for channel in channels if channel not in HA_channels]
channel_list = ", ".join([f"{device}/{channel}" for channel in channels])

pulse_interval = pulse_on_length + pulse_off_length
num_intervals = t_sampling / pulse_interval
read_frequency = f_sampling * 10
dt_read = 1 / read_frequency
samples_per_interval = pulse_interval * read_frequency
buffer_time = 2 # s
buffer_size_samples = int(read_frequency * buffer_time)

# TDMS file that we will read the data into 
pulse_data_path = "pulse_data.tdms"

'''
Generate pulses ensuring we are not off by one, previously had an error where we were pulsing 11 times however, 
we did not notice because we were not reading the first sample. Had inconsistent data. 
'''
# Generate Pulse Train
pulse_train = np.zeros(n_sampling, dtype=np.uint32)
pulse_intervals = np.arange(0, n_sampling, f_sampling // f_stimulation)
pulse_train[pulse_intervals] = 4 if line == 'line2' else 8 if line == 'line3' else 0
# On off pulse train for one cycle
pulse_on_off_single = np.concatenate((np.ones(pulse_on_length * f_sampling, dtype=np.uint32),
np.zeros(pulse_off_length * f_sampling, dtype=np.uint32)))
# Tile the pattern out for the rest of the pulse 
pulse_on_off = np.tile(pulse_on_off_single, n_sampling // len(pulse_on_off_single) + 1)[:n_sampling]
# Apply the pulse on/off pattern to the pulse train
pulse_train *= pulse_on_off

# plt.plot(pulse_train)f
# plt.show()

print("\nsampling time : ", t_sampling, " seconds ")
print(f"PULSE TRAIN GENERATED AT {time.ctime(time.time())}")

def seconds_to_hhmmss_microseconds(total_seconds):
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    microseconds = (total_seconds - int(total_seconds)) * 1_000_000
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}.{int(microseconds):06}"

#2 ============================= NIDAQ SETUP AND RUN ===================================
'''
We configure the write task and configure the read tasks. We've setup the read task to read into a 
TDMS hard drive file defined above. The read is set to create and replace. We will always replace the
prior file from the antecedent run so as not to use up too much memory. 

Next, we have to start the read task before the write task or we will miss data about the first sample with the ~.3 seconds
it takes to configure the tasks (pulse starts right away as soon as we active the write).
'''
with nidaqmx.Task() as writetask, nidaqmx.Task() as readtask:

    current_date = datetime.now().date()
    start_of_day = datetime.combine(current_date, dt_time())

    # SETUP: Digital Output writer
    # MUST MAKE SURE WE DO NOT STIMLUATE LEAD 12
    writetask.do_channels.add_do_chan(f'/Dev3/port0/{line}')
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
    # reader = AnalogSingleChannelReader(readtask.in_stream)

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

#3 ==================== FULL PULSE DATA LOAD FROM TDMS & TIME ARRAY =======================================
# ---------------- 3a loading --------------
print(f"\nDATA PROCESSING STARTED AT {time.ctime(time.time())}")
# Start the dat processing step
pulse_data_file = TdmsFile.read(pulse_data_path)
# Extract the data from the singular group and channel
pulse_channels = pulse_data_file.groups()[0].channels()
pulse_channels_data_dict = {}

for i, channel in enumerate(pulse_channels): 
    data = channel.data
    pulse_channels_data_dict[channel.name] = data

# All should be the same length in theory 
prev = 0
for key, val in pulse_channels_data_dict.items(): 
    if prev == 0: 
        prev = len(val)
        continue 
    next = len(val)
    if next == prev: 
        prev = next
    else : 
        raise ValueError("Len of all the data arrays are not equal") 
    
num_samples = len(list(pulse_channels_data_dict.values())[0])
print(f"DATA SUCESSFULLY READ INTO ARRAYS OF SIZE : {num_samples} AT {time.ctime(time.time())}\n")
# ----------------- 3b Time configurgation & check ---------------------------------------
# Calculate end for the time array
stop = t_start + num_samples * dt_read
# Create the time array
# Synthesized time data using start time, calculated stop time, and the read frequency
# Should all have the same time data
time_array = np.arange(start=t_start, stop=stop, step=dt_read)
'''
Checks to ensure that we have made our time array correctly. The min should be the start and the max should be the end.
Moreover, the start minus the end should equal the sampling time. Note that time_array values are not actual times at which data was recorded,
this was not possible to get with such a high frequency and while reading in chunks in the way we did. 
'''
print(f"Number of samples, {num_samples}, matches the number of values in the time array, {len(time_array)}")
# print("Time array : ", time_array)
print(f"""time array configured properly if min of the time array : {time.ctime(start_of_day.timestamp() + min(time_array))}, = the start time :  {time.ctime(start_of_day.timestamp() + t_start)},
and, max of the time array : {time.ctime(start_of_day.timestamp() + max(time_array))}, = t_start + sampling time : {time.ctime(start_of_day.timestamp() + t_sampling)},
and the last time minus the first time : {time_array[num_samples - 1] - time_array[0]}, = the sampling time : {t_sampling} \n""")

#4 =================== DATA PROCESSING & DATA FRAME CREATION ================================================

# ----------------------- 4a statistics data frame poppulation & creation ---------------------------------

# Returns the peaks of the data 
# Takes in an interval of data as well as boolean for pos v negative peaks 
# Takes all values over the threshold, and then takes the max
# Caught error w voltage spikes that we would not have seen
# Plot out the data for a given interval
def plot_voltage_vs_time(data, times):
    # Extract the time range for the current interval

    # Plot the data
    plt.figure(figsize=(20, 6))
    plt.axhline(y = 5, color = 'black', linestyle = '--')
    plt.axhline(y = -5, color = 'black', linestyle = '--')
    plt.plot(times, data, label='Voltage')
    plt.xlabel('Time (s)')
    plt.ylabel('Voltage (V)')
    plt.title('Voltage vs Time')
    plt.legend()
    plt.grid(True)
    plt.show()

def detect_peaks(interval, threshold, positive):
    peaks = []
    i = 0
    while i < len(interval):
        if (interval[i] > threshold and positive) or (interval[i] < -threshold and not positive):
            samples = []
            while i < len(interval) and ((interval[i] > threshold and positive) or (interval[i] < -threshold and not positive)):
                samples.append(i)
                i += 1
            if samples:
                if positive:
                    peak_index = max(samples, key=lambda x: interval[x])
                else:
                    peak_index = min(samples, key=lambda x: interval[x])
                peaks.append(peak_index)
        else:
            i += 1
    return peaks
#spi : samples per interval
#ns : num samples
#RF : read freq
# t : time arrray 
# In order to avoid global vars
def process_data_by_interval(pulse_data, SPI, NS, RF, t, name):
    # alternative peak method, not as accurate, only catches first instance of above the threshold
    # peaks, _ = scipy.signal.find_peaks(interval * 10, height=5, distance = 900)
    # neg_peaks, _ = scipy.signal.find_peaks(-interval * 10, height=5, distance = 900)
    # Detecting positive peaks
    df= pd.DataFrame(columns=[
    'day_time',
    'plate_id',
    'interval_num',
    'stimulation period',
    'pos pulses per cycle',
    'voltage pos median',
    'voltage pos mean',
    'voltage pos std',
    'voltage pos cv',
    'voltage pos min',
    'voltage pos max',
    'neg pulses per cycle',
    'voltage neg median',
    'voltage neg mean',
    'voltage neg std',
    'voltage neg cv',
    'voltage neg min',
    'voltage neg max',
    'energy applied',
    'interval snr',
    'interval rms'
    ])
    normal_stim_ = True
    indexes_ = []
    unexpected_peaks = []
    start_index = 0 # 0 seconds
    # global vars
    end_index = SPI // 2 # 5 seconds
    idx = 0 
    # Loop through each 10 second interval
    while start_index <= NS:
        if end_index > NS : 
            end_index = NS

        # Pull out data and time for the cycle we are looking at (5 : 15s, 15 : 25s...etc )
        # On intervals of 5 so as to never miss a pulse data point 
        interval = pulse_data[start_index:end_index]
        time_interval = time_array[start_index:end_index]

        # Process the cycle 
        # Do not want to process the final cycle where there is no real data, no pulse in the final 5 seconds. This will lead to processing errors
        if end_index != NS : 
            # print(f"Processing data for {name} interval : {start_index/RF} seconds to {end_index/RF} seconds:")
            # plot_voltage_vs_time(interval, time_interval)
            peaks = detect_peaks(interval, peak, True)
            neg_peaks = detect_peaks(interval, peak, False)

            if not peaks or not neg_peaks: 
                # Good place to send an alert
                normal_stim_ = False
                print(f"ALERT : No peaks for {name} {start_index/RF} seconds to {end_index/RF} seconds!")
                df.loc[idx, :] = np.nan
                df.at[idx, 'date'] = current_date
                df.at[idx, 'period'] = period
                df.at[idx, 'plate_id'] = plate_channels_dict[name]
                df.at[idx, 'interval_num'] = idx
                df.at[idx, 'voltage pos min'] = np.min(interval)
                df.at[idx, 'voltage pos max'] = np.max(interval)
                df.at[idx, 'voltage neg min'] = np.min(interval)
                df.at[idx, 'voltage neg max'] = np.max(interval)
                df.at[idx, 'interval rms'] = np.sqrt(np.mean(interval ** 2))
                df.at[idx, 'energy applied'] = np.sum(interval ** 2)
                df.at[idx, 'interval snr'] = 10 * np.log10(np.mean(interval ** 2) / np.var(interval))
            else :
                if idx != 0:
                    new_indexes = np.arange(start_index + peaks[0] - int(.25 * read_frequency), start_index + neg_peaks[-1] + int(.25 * read_frequency))
                else: 
                    new_indexes = np.arange(start_index + peaks[0], start_index + neg_peaks[-1] + int(.25 * read_frequency))
                indexes_ += list(new_indexes)
                
                if new_indexes.size > 0:
                    end_idx = new_indexes[-1] + int(((pulse_off_length - .5) * read_frequency))
                    if end_idx < len(pulse_data) :
                        post_pulse_interval = pulse_data[new_indexes[-1] : end_idx]
                        unexpected_peaks += detect_peaks(post_pulse_interval, peak * .5, True)
                        unexpected_peaks += detect_peaks(post_pulse_interval, peak * .5, False)
                    if unexpected_peaks: 
                        print('\nUNEXPECTED PEAKS DETECTED\n')
                        normal_stim_ = False
                    
                stim_start = time_interval[peaks[0]]
                stim_end = time_interval[neg_peaks[-1]]

                stimulation_period = stim_end - stim_start
                df.at[idx, 'stimulation period'] = stimulation_period
                df.at[idx, 'day_time'] = time.ctime(start_of_day.timestamp() + stim_start)
                df.at[idx, 'date'] = current_date
                df.at[idx, 'period'] = period
                df.at[idx, 'plate_id'] = plate_channels_dict[name]
                df.at[idx, 'interval_num'] = idx

                df.at[idx, 'pos pulses per cycle'] = len(peaks)
                df.at[idx, 'voltage pos median'] = np.median(interval[peaks])
                df.at[idx, 'voltage pos mean'] = np.mean(interval[peaks])
                df.at[idx, 'voltage pos std'] = np.std(interval[peaks])
                df.at[idx, 'voltage pos cv'] = stats.variation(interval[peaks])
                df.at[idx, 'voltage pos min'] = np.min(interval)
                df.at[idx, 'voltage pos max'] = np.max(interval)
                df.at[idx, 'avg pos current'] = (np.mean(interval[peaks] / resistance) * 1000)
                df.at[idx, 'pos charge'] = np.trapezoid(interval[peaks], x = t[peaks], dx = dt_read)

                df.at[idx, 'neg pulses per cycle'] = len(neg_peaks)
                df.at[idx, 'voltage neg median'] = np.median(interval[neg_peaks])
                df.at[idx, 'voltage neg mean'] = np.mean(interval[neg_peaks])
                df.at[idx, 'voltage neg std'] = np.std(interval[neg_peaks])
                df.at[idx, 'voltage neg cv'] = stats.variation(interval[neg_peaks])
                df.at[idx, 'voltage neg min'] = np.min(interval)
                df.at[idx, 'voltage neg max'] = np.max(interval)
                df.at[idx, 'avg neg current'] = (np.mean(interval[neg_peaks] / resistance) * 1000)
                df.at[idx, 'neg charge'] = np.trapezoid(interval[neg_peaks], x = t[neg_peaks], dx = dt_read)

                # Full interval signals common to electric stimulatuion statistics
                df.at[idx, 'interval rms'] = np.sqrt(np.mean(interval ** 2))
                df.at[idx, 'energy applied'] = np.sum(interval ** 2)
                df.at[idx, 'interval snr'] = 10 * np.log10(np.mean(interval ** 2) / np.var(interval))
        # Move to the next interval
        if idx == 0: 
            start_index += samples_per_interval // 2 # 0 seconds to 5 seconds
        else: 
            start_index += samples_per_interval # 5 seconds to 15, 15 to 25 etc
        end_index += samples_per_interval # always jump by 10, we handle the end case above
        idx += 1
    print(f"\nIntervals Processed, returning {name} intervals data frame\n")
    return df, normal_stim_, indexes_

def analyze_full_pulse_data(pulse_data, t, name, df_cycles : pd.DataFrame):

    'Report_time1', 'voltage1', 'pulseDuration1', 'frequency1', 'current1', 'charge1', 'chargeDifference1', 
    'maturationPercentage1', 'energy1', 'rms1', 'Report_time2', 'voltage2', 'pulseDuration2', 'frequency2', 
    'current2', 'charge2', 'chargeDifference2', 'maturationPercentage2', 'energy2', 'rms2'

    print(f"analyzing full pulse data for {name}")
    df = pd.DataFrame(columns=[
        'day_time', 'date', 'period', 'plate_id', 'mean', 'median', 'std', 'variance', 'min', 'max', 'range', 'rms',
        'snr', 'energy', 'pos peaks count', 'pos peaks mean', 'pos peaks median',
        'pos peaks std', 'pos peaks min', 'pos peaks max', 'neg peaks count', 
        'neg peaks mean', 'neg peaks median', 'neg peaks std', 'neg peaks min', 
        'neg peaks max'])

    idx = 0  # Full data only using the first index
    # General domain stats
    
    pos_peaks = detect_peaks(pulse_data, peak, True)
    neg_peaks = detect_peaks(pulse_data, peak, False)
    if not pos_peaks or not neg_peaks: 
        print(f"ALERT : No peaks for {name}")
        df.loc[idx, :] = np.nan
    else:
        df.at[idx, 'pos peaks count'] = len(pos_peaks)
        df.at[idx, 'pos peaks mean'] = np.mean(pulse_data[pos_peaks])
        df.at[idx, 'pos peaks median'] = np.median(pulse_data[pos_peaks])
        df.at[idx, 'pos peaks std'] = np.std(pulse_data[pos_peaks])
        df.at[idx, 'pos peaks min'] = np.min(pulse_data[pos_peaks])
        df.at[idx, 'pos peaks max'] = np.max(pulse_data[pos_peaks])
        df.at[idx, 'avg pos current'] = (np.mean(pulse_data[pos_peaks]) / resistance) * 1000
        df.at[idx, 'pos charge'] = np.trapezoid(pulse_data[pos_peaks], x = t[pos_peaks], dx = dt_read)
        df.at[idx, 'frequency'] = (len(pos_peaks) / t_sampling) * 10
        #df.at[idx, 'simp pos charge'] = simps(pulse_data[pos_peaks], t[pos_peaks])
    
        df.at[idx, 'neg peaks count'] = len(neg_peaks)
        df.at[idx, 'neg peaks mean'] = np.mean(pulse_data[neg_peaks])
        df.at[idx, 'neg peaks median'] = np.median(pulse_data[neg_peaks])
        df.at[idx, 'neg peaks std'] = np.std(pulse_data[neg_peaks])
        df.at[idx, 'neg peaks min'] = np.min(pulse_data[neg_peaks])
        df.at[idx, 'neg peaks max'] = np.max(pulse_data[neg_peaks])
        df.at[idx, 'avg neg current'] = (np.mean(pulse_data[neg_peaks]) / resistance) * 1000
        df.at[idx, 'neg charge'] = np.trapezoid(pulse_data[neg_peaks], x = t[neg_peaks], dx = dt_read)
        #df.at[idx, 'simp pos charge'] = simps(pulse_data[pos_peaks], t[pos_peaks])

    df.at[idx, 'full charge difference'] = np.trapezoid(y = pulse_data, x = t, dx = dt_read)
    #df.at[idx, 'simp full charge diff'] = simps(pulse_data, t)
    df.at[idx, 'pulseDuration'] = np.mean(df_cycles['stimulation period'].iloc[0])
    df.at[idx, 'day_time'] = datetime_start
    df.at[idx, 'date'] = current_date
    df.at[idx, 'period'] = period
    df.at[idx, 'plate_id'] = plate_channels_dict[key]
    df.at[idx, 'mean'] = np.mean(pulse_data)
    df.at[idx, 'median'] = np.median(pulse_data)
    df.at[idx, 'std'] = np.std(pulse_data)
    df.at[idx, 'variance'] = np.var(pulse_data)
    df.at[idx, 'min'] = np.min(pulse_data)
    df.at[idx, 'max'] = np.max(pulse_data)
    df.at[idx, 'range'] = np.ptp(pulse_data)
    df.at[idx, 'rms'] = np.sqrt(np.mean(pulse_data ** 2))
    df.at[idx, 'snr'] = 10 * np.log10(np.mean(pulse_data ** 2) / np.var(pulse_data))
    df.at[idx, 'energy'] = np.sum(pulse_data ** 2)
    print(f"Stats Dataframe created for {name}")
    return df
#----------------------------- 4b Pulse data frame creation, loading, and storage -----------------------------------------

# Ensure that the pulse array and time array are the same length (will only ever be off by one)
def ensure_length(pulse_data, time_array):
    min_length = min(len(time_array), len(pulse_data))
    time_array = time_array[:min_length]
    pulse_data = pulse_data[:min_length]
    return time_array, pulse_data

# channels = ['ai0', 'ai2', 'ai4', 'ai6', 'ai8']
# def process_data_by_interval(pulse_data, SPI, NS, RF, name):
data_frame_dict = {}
data_frame_dict['summary_stats'] = pd.DataFrame()
data_frame_dict['cycle_stats'] = pd.DataFrame()
data_frame_dict['voltage'] = pd.DataFrame()

for i, (key, value) in enumerate(pulse_channels_data_dict.items()):
    
    time_array, value = ensure_length(value, time_array)
    print("\nProcessing data from : ", key)

    data_frame_cyles, normal_stim, indexes = process_data_by_interval(value, samples_per_interval, num_samples, read_frequency, time_array, key)
    data_frame_pulse_summary = analyze_full_pulse_data(value, time_array, key, data_frame_cyles)
    if normal_stim: 
        value = value[indexes]
        time_ = time_array[indexes]
    else : 
        time_ = time_array

    plate_id = plate_channels_dict[key]

    print('\nprocessing voltage trace...')
    index_ = ['plate_id', 'day_time', 'date', 'period', 'resistance', 'type' ] + [i for i in range(len(value))]

    data_t = [plate_id, time.ctime(t_track), current_date, period, resistance, 'Times(S)'] + list(time_)
    data_v = [plate_id, time.ctime(t_track), current_date, period, resistance, 'Voltage(V)'] + list(value)
    data = {'ID' : index_, f'col_{i}_t' : data_t, f'col_{i}_v' : data_v}
    data_frame_voltage = pd.DataFrame(data)
    data_frame_voltage.set_index('ID', inplace = True)

    if i == 0: 
        merged_volt = data_frame_voltage
    else: 
        existing_df_volt = data_frame_dict['voltage'].set_index('ID')
        merged_volt = pd.concat([existing_df_volt, data_frame_voltage], axis = 1)
    
    print(f'Finished! saving dataframes for {key} \n')
    data_frame_dict['voltage'] = merged_volt.reset_index()
    data_frame_dict['cycle_stats'] = pd.concat([data_frame_dict['cycle_stats'], data_frame_cyles], ignore_index = True)
    data_frame_dict['summary_stats'] = pd.concat([data_frame_dict['summary_stats'], data_frame_pulse_summary], ignore_index = True)

#5 ====================WRITE DATA FRAMES TO SQL =========================================

# SQL Data Base Credentials # Database credentials
username = 'nallen'
password = 'wtQGQ6EX.*zA6Zh'
host = '10.10.100.41'

logging.basicConfig()
logging.getLogger('sqlalchemy.pool').setLevel(logging.INFO)

# Monitoring connection pool usage
@event.listens_for(Pool, "checkout")
def checkout_listener(dbapi_con, con_record, con_proxy):
    print(f"Connection checked out: {dbapi_con}")

@event.listens_for(Pool, "checkin")
def checkin_listener(dbapi_con, con_record):
    print(f"Connection returned to pool: {dbapi_con}")

# Function to add rows to existing table
def add_rows(engine, table_name, df : pd.DataFrame, chunk_size = 100000):
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
    
    # Write the combined DataFrame back to the SQL table
    print('\nWriting table to local storage...')
    output_dir = 'C:\\Users\\microscope\\Desktop\\SkeletalStimLogs\\SkelStimWebApp\\'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    sql_out_file = output_dir + f'{table_name}.csv'
    if os.path.exists(sql_out_file):
        os.remove(sql_out_file)
    combined_df.to_csv(sql_out_file, index=True)
    print(f'\nLOCAL COPY OF {table_name} STORED AT : {output_dir}\n')

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
    # combined_df.to_sql(table_name, engine, if_exists='replace', index=False)
    
def custom_sort(index):
    # Sort function that puts strings first, then numbers
    return sorted(index, key=lambda x: (isinstance(x, (int, float)), x))

def add_columns(engine, table_name, df : pd.DataFrame, chunk_size = 100000):
    # index into the proper column using that ID column
    # Make sure that there is only one of these columns
    #   existing_df = pd.read_sql_table(table_name, engine)
    try:
        chunks = pd.read_sql_table(table_name, engine, chunksize=chunk_size)
        existing_df = pd.concat(chunk for chunk in chunks)
        print("\nDataFrame successfully loaded with shape:", existing_df.shape)
    except Exception as e:
        print("Error reading the table:", e)

    existing_df.set_index('ID', inplace = True)
    df.set_index('ID', inplace = True)

    existing_df.index = existing_df.index.astype(str)
    df.index = df.index.astype(str)

    combined_indexes = existing_df.index.union(df.index)

    def custom_sort(index):
        try:
            return (1, int(index))
        except ValueError:
            return (0, index)

    # Sort combined indexes
    combined_indexes = sorted(combined_indexes, key=custom_sort)

    existing_df_reindexed = existing_df.reindex(combined_indexes)
    df_reindexed = df.reindex(combined_indexes)

    df_reindexed.columns = [i for i in range(len(df_reindexed.columns))]
    existing_df_reindexed.columns = [j + len(df_reindexed.columns) for j in range(len(existing_df_reindexed.columns))]
    
    # Concatenate the DataFrames
    combined_df = pd.concat([df_reindexed, existing_df_reindexed], axis=1, join = 'outer')
    # make sure that the ID column is modified when we pull it back out
    combined_df.reset_index(inplace = True)

    # Writing to computer to ensure
    print('\nWriting table to local storage...')
    output_dir = 'C:\\Users\\microscope\\Desktop\\SkeletalStimLogs\\SkelStimWebApp\\'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    sql_out_file = output_dir + f'{table_name}.csv'
    if os.path.exists(sql_out_file):
        os.remove(sql_out_file)
    combined_df.to_csv(sql_out_file, index=True)
    print(f'\nLOCAL COPY OF {table_name} STORED AT : {output_dir}\n')

    # Rename the columns sequentially
    new_columns = {col: f'col_{i+1}' for i, col in enumerate(combined_df.columns[1:])}
    combined_df.rename(columns=new_columns, inplace=True)

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
    # print(f'{table_name} written to SQL')

def create_new_table(engine, table_name, df : pd.DataFrame, chunk_size = 100000):
    print(f'\nCREATING {table_name}\n')
    pool = engine.pool
    print(pool.status())

    # Writing to computer to ensure
    print('\nWriting table to local storage...')
    output_dir = 'C:\\Users\\microscope\\Desktop\\SkeletalStimLogs\\SkelStimWebApp\\'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    sql_out_file = output_dir + f'{table_name}.csv'
    if os.path.exists(sql_out_file):
        os.remove(sql_out_file)
    df.to_csv(sql_out_file, index=True)
    print(f'\nLOCAL COPY OF {table_name} STORED AT : {output_dir}\n')

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

def process_databases(database_input_df_dict): 
    # Need to make sure we don't read in the HA for the current
    # If database doesnt equal current or not in HA_channels list
    for database_name, df in database_input_df_dict.items():
        print(f"writing into {database_name}")
        engine = create_engine(f'mysql+mysqlconnector://{username}:{password}@{host}/{database_name}', pool_size=400, max_overflow=800)
        inspector = inspect(engine) 
        # plates must be distinct or else we will override data
        if database_name == 'voltage': table = database_name + '_table_' + f'{datetime.now().month}_{datetime.now().year}' + f'_harvard{harvard}'
        else : table = database_name + '_table' + f'_harvard{harvard}'
        if inspector.has_table(table): 
            if database_name == 'voltage':
                # Update the variables before we write into voltage
                print("\nUpdating Variables...\n")
                with open("update_app_data.py") as f:
                    code = f.read()
                    exec(code)
                print(f'adding {database_name} columns to {table}')
                add_columns(engine, table, df)
            else: 
                print(f'adding {database_name} rows to {table}')
                add_rows(engine, table, df)
        else: 
            print(f"Table '{table}' does not exist in database '{database_name}'. Creating new table.")
            create_new_table(engine, table, df)

process_databases(data_frame_dict)
datetime_end = datetime.now()
total_time_elapsed = datetime_end - datetime_start
print(f'\ntotal time elapsed  : {total_time_elapsed}\n')


print("\nALL TASKS FINISHED, CODE EXITIING\n")

