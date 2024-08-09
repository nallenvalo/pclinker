import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from datetime import datetime
import time 
from datetime import date, datetime

output_dir = 'C:/Users/microscope/Desktop/SkeletalStimLogs/Images'

read_frequency = 10000
paths = ["C:/Users/microscope/Desktop/SkeletalStimLogs/SkelStimWebApp/voltage_table_8_2024_harvard1.csv"]
# paths = ["C:/Users/microscope/Desktop/SkeletalStimLogs/SkelStimWebApp/voltage_table_8_2024_harvard1_archive.csv"]
# paths = ["C:/Users/microscope/Desktop/SkeletalStimLogs/Lead 7_8/voltage_exp_8_2024_lead_7_8.csv"]
# paths = ["C:/Users/microscope/Desktop/SkeletalStimLogs/lead9/voltage_exp_7_2024.csv"]
paths = ["C:/Users/microscope/Desktop/SkeletalStimLogs/Lead 7_8/voltage_exp_8_2024_lead_7_8.csv", 
        "C:/Users/microscope/Desktop/SkeletalStimLogs/Lead 9_10/voltage_exp_8_2024_lead_9_10.csv"]

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def seconds_to_hhmmss_microseconds(total_seconds):
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60 
    seconds = total_seconds % 60
    microseconds = (total_seconds - int(total_seconds)) * 1_000_000
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}.{int(microseconds):06}"

# Set Seaborn style
sns.set(style="darkgrid")

# Create the plot
plt.figure(figsize=(30, 10))

for i, path in enumerate(paths):
    file_title = path.split('/')[-1]
    date_ = file_title.split('S')[0]
    file_title = file_title.split('.')[0]
    folder_path = os.path.join(output_dir, file_title)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    data_frame = pd.read_csv(path)
    data_frame.set_index('ID', inplace = True)
    columns_ = list(data_frame.columns[1:])
    sample_size = 1000000
    for col1, col2 in zip(columns_[::2], columns_[1::2]):
        time_ = data_frame[col1]
        value_ = data_frame[col2]
        x = pd.to_numeric(time_[6:], errors = 'coerce').dropna()
        y = pd.to_numeric(value_[6:], errors = 'coerce').dropna()
        plateid = value_.loc['plate_id']
        date_ = value_.loc['date']
        day_time = value_.loc['day_time']
        period = value_.loc['period']
        title_ = date_ + '_' + plateid + '_' + period
        start = 0 
        end = sample_size
        num_samples = len(data_frame[col1].dropna())
        plot_num = 1
        # data_frame[col] = data_frame[col] / 10

        while start < num_samples: 
            if end > num_samples: 
                end = num_samples
            data_ = y[start : end].values
            time_ = x[start : end].values
        
            sns.lineplot(x = time_, y = data_, linewidth = .1, alpha = .8, color = 'red')
            # Enhance plot aesthetics
            plt.xlabel('Time (s)', fontsize=10)
            x_ticks = np.arange(start/read_frequency, end/read_frequency, 10)
            plt.xticks(rotation=60, fontsize=8)
            # plt.axhline(y = 5, color = 'black', linewidth = .5, alpha = .5)
            # plt.axhline(y = -5, color = 'black', linewidth = .5, alpha = .5)
            plt.ylabel('Voltage (v)', fontsize=10)
            y_ticks = np.arange(-3, 3, 0.5)
            plt.yticks(y_ticks, fontsize=8)

            plt.title(title_, fontsize=10)
            plt.grid(True)
            plt.tight_layout()
            plt.show()

            plot_path = os.path.join(folder_path, f'plot_{plateid}_{date_}_{plot_num}.png')
            if os.path.exists(plot_path): os.remove(plot_path)
            plt.savefig(plot_path)
            plt.close()

            plot_num += 1 
            start += sample_size
            end += sample_size
print("Completed!")
