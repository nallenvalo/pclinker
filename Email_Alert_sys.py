import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import shutil
import os
import json
import pandas as pd
import sys 
import datetime
from datetime import datetime
from sqlalchemy import create_engine, inspect

username = 'nallen'
password = 'wtQGQ6EX.*zA6Zh'
host = '10.10.100.41'

def SkelStimError(text_file, name):

    id_sender = 'skeletalstimulation@gmail.com'
    password_sender = 'ftey xyeq jlwv llqx' # NOTE THAT THIS IS FROM GOOGLE GMAIL APP PASSWORDS AT BOTTOM OF 2FA
    id_receipients = ['nallen@valohealth.com']

    msg = MIMEMultipart()
    msg['From'] = id_sender
    msg['To'] = ', '.join(id_receipients)
    msg['Subject'] = 'There has been an error in the Skeletal Stimulation Run'
    message = 'ALERT, THERE HAS BEEN AN ERROR ON A LEAD FILE RUN. \n' + name + '\n\n' + text_file
    msg.attach(MIMEText(message))

    mailserver = smtplib.SMTP('smtp.gmail.com',587)
    # identify ourselves to smtp gmail client
    mailserver.ehlo()
    # secure our email with tls encryption
    mailserver.starttls()
    # re-identify ourselves as an encrypted connection
    mailserver.ehlo()
    mailserver.login(id_sender, password_sender)

    mailserver.sendmail(id_sender, id_receipients, msg.as_string())

    mailserver.quit()

def MissingSKelStim(plate, date, num):

    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    id_sender = 'skeletalstimulation@gmail.com'
    password_sender = 'ftey xyeq jlwv llqx' # NOTE THAT THIS IS FROM GOOGLE GMAIL APP PASSWORDS AT BOTTOM OF 2FA
    id_receipients = ['nallen@valohealth.com']

    msg = MIMEMultipart()
    msg['From'] = id_sender
    msg['To'] = ', '.join(id_receipients)
    msg['Subject'] = 'Missing Skeletal Stimulation'
    message = f'Alert: missing skeletal stimulation log. \n plate : {plate} has recieved {num} stimulation periods in the 16 hours prior to {date}'
    msg.attach(MIMEText(message))

    mailserver = smtplib.SMTP('smtp.gmail.com',587)
    # identify ourselves to smtp gmail client
    mailserver.ehlo()
    # secure our email with tls encryption
    mailserver.starttls()
    # re-identify ourselves as an encrypted connection
    mailserver.ehlo()
    mailserver.login(id_sender, password_sender)

    mailserver.sendmail(id_sender, id_receipients, msg.as_string())

    mailserver.quit()

# def SkelStimRangeErr(plate, signal, val, date, HA):
def SkelStimRangeErr(errors_list, variables):
#  tup = [plate, 'snr', data, date, HA_]
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    id_sender = 'skeletalstimulation@gmail.com'
    password_sender = 'ftey xyeq jlwv llqx' # NOTE THAT THIS IS FROM GOOGLE GMAIL APP PASSWORDS AT BOTTOM OF 2FA
    id_receipients = ['nallen@valohealth.com']
    content = ''
    # tup = [plt, date, stat, data_, HA_]
    for item in errors_list:
        plate = item[0]
        signal = item[2]
        val = item[3]
        date = item[1]
        HA = variables[plate]['HarvardAparatus']
        expected = item[4]
        line = f'''Skeletal Stimulation {signal} is not expected for \n plate : {plate} of Harvard Aparatus {HA} 
        on excercise period {date}. The value was {val} which is outside the expected range of {expected}'''
        content += '\n' + line + '\n'

    msg = MIMEMultipart()
    msg['From'] = id_sender
    msg['To'] = ', '.join(id_receipients)
    msg['Subject'] = 'Skeletal Stimulation Outside of Expected Ranges'
    message = content
    msg.attach(MIMEText(message))

    mailserver = smtplib.SMTP('smtp.gmail.com',587)
    # identify ourselves to smtp gmail client
    mailserver.ehlo()
    # secure our email with tls encryption
    mailserver.starttls()
    # re-identify ourselves as an encrypted connection
    mailserver.ehlo()
    mailserver.login(id_sender, password_sender)

    mailserver.sendmail(id_sender, id_receipients, msg.as_string())

    mailserver.quit()

err_dir = "C:/Users/microscope/Desktop/SkeletalStimLogs/ErrorCallback"
call_dir = "C:/Users/microscope/Desktop/SkeletalStimLogs/Callback"
base_dir = "C:/Users/microscope/Desktop/SkeletalStimLogs"

# Check if the directory exists
if not os.path.exists(err_dir):
    print("The directory does not exist.")
else:
    # Get list of all files in the directory
    files = os.listdir(err_dir)
     # Check if the directory is empty
    if len(files) == 0:
        print("The directory is empty. No files found.")
    else:
        print("The directory is not empty. Files found.")
        for text_file in files:
            file_path = os.path.join(err_dir, text_file)
            with open(file_path, 'r') as file:
                text_file_content = file.read()
                SkelStimError(text_file_content, text_file)
            new_file_path = os.path.join(call_dir, text_file)
            shutil.move(file_path, new_file_path)

# Check if the directory exists
if datetime.now().hour % 12 == 0:
    if not os.path.exists(base_dir):
        pass
    else:
        # Get list of all files in the directory
        files = os.listdir(base_dir)
        files =[f for f in files if f.endswith('.txt')]
        # Check if the directory is empty
        if len(files) == 0:
            pass
        else:
            print("Terminated Python Script Files Found")
            content = 'Files left from a terminated Python script have been found \n \n'
            idx = 0
            for text_file in files:
                file_path = os.path.join(base_dir, text_file)
                with open(file_path, 'r') as file:
                    text_file_content = file.read()
                    file_num = f'\n\nFile Number {idx} : {text_file}\n'
                    content += file_num
                    content += text_file_content
                new_file_path = os.path.join(call_dir, text_file)
                shutil.move(file_path, new_file_path)
                idx += 1
            SkelStimError(content, '')

# engine_summary_stats = create_engine(f'mysql+mysqlconnector://{username}:{password}@{host}/summary_stats', pool_size=400, max_overflow=800)
# inspector = inspect(engine_summary_stats) 

# summary_stats_table_list = []
# for i in range(1,4):
#     if inspector.has_table(f'summary_stats_table_harvard{i}'):
#         table = pd.read_sql_table(f'summary_stats_table_harvard{i}', engine_summary_stats)
#         summary_stats_table_list.append(table)
        
# if not summary_stats_table_list:
#     raise Exception('NO SUMMARY STATS')

# summary_stats_table = pd.concat(table for table in summary_stats_table_list)
# summary_stats_table = summary_stats_table.sort_values(by='day_time', ascending=False)

# output_dir = 'C:\\Users\\microscope\\Desktop\\SkeletalStimLogs\\'
# if not os.path.exists(output_dir):
#     os.makedirs(output_dir)
# out_file = output_dir + f'entire_sum_stats.csv' #{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
# if os.path.exists(out_file):
#     os.remove(out_file)
# summary_stats_table.to_csv(out_file, index=True)

# with open('variables.json', 'r') as file:
#     variables = json.load(file)

# HA1_Running = False
# HA2_Running = False
# HA1_plates_set = set()
# HA2_plates_set = set()
# activate_plates_set = set()
# missing_stim_plates_set = set()

# # All plates in the vars dict are already active
# for plate, vars_dict in variables.items():
#     if vars_dict['HarvardAparatus'] == 1:
#         HA1_Running = True
#         HA1_plates_set.add(plate)
#     elif vars_dict['HarvardAparatus'] == 2:
#         HA2_Running = True
#         HA2_plates_set.add(plate)
#     activate_plates_set.add(plate)

# exit = False

# def check_missing_logs(Stimulator_plates_set : set, missing_stim_plates_set : set, summary_stats_table : pd.DataFrame):
#     activate_Stim_plates_df = pd.DataFrame()
#     activate_Stim_plates_df = summary_stats_table.loc[summary_stats_table['plate_id'].isin(Stimulator_plates_set)]
#     activate_Stim_plates_set = set(activate_Stim_plates_df.iloc[0])
#     missing_stim_plates_set.union(activate_Stim_plates_set.difference(activate_Stim_plates_set))
#     return missing_stim_plates_set, activate_Stim_plates_df

# missing_stim_plates_set, activate_HA1_summary_stats = check_missing_logs(HA1_plates_set, missing_stim_plates_set, summary_stats_table)
# missing_stim_plates_set, activate_HA2_summary_stats = check_missing_logs(HA2_plates_set, missing_stim_plates_set, summary_stats_table)

# if activate_HA1_summary_stats.empty and HA1_Running:
#     exit = True 
#     MissingSKelStim('entire HA1', '0', datetime.now())
# else:
#     print('HA1 properly configured')

# if activate_HA2_summary_stats.empty and HA2_Running:
#     exit = True 
#     MissingSKelStim('entire HA1', '0', datetime.now())
# else:  
#     print('HA2 properly configured')

# if exit : sys.exit(1)

# for plate in missing_stim_plates_set:
#     plate_rows = summary_stats_table.loc[missing_stim_plates_set['plate_id'] == plate]
#     day_time_list = plate_rows['day_time']
#     num = sum(1 for day in day_time_list if pd.to_datetime(day) > (datetime.now() - pd.Timedelta(hours=8)))
#     start =  pd.to_datetime(variables[plate]['stimulation_start']) 
#     if num < 1 and start > (datetime.now() - pd.Timedelta(hours=16)):
#         MissingSKelStim(plate, datetime.now(), num)
#     else :
#         print(f"Proper stimulation for {plate}")


# with open('all_errors.json', 'r') as file:
#     all_errors = json.load(file)
# errors = []
# valid = True

# def addErr(stat, data, expected_data, plate, date, errors, all_errors, valid):
#     if plate not in all_errors.keys(): all_errors[plate] = {}
#     tup = [plate, date, stat, data, expected_data]
#     date = date.isoformat()[:16]
#     key = date + '_' + stat
#     if key not in all_errors[plate].keys(): 
#         valid = False
#         all_errors[plate][key] = []
#         all_errors[plate][key].append(tup[2:])
#         errors.append(tup)
#     return errors, all_errors, valid

# for plate, param_dict in variables.items(): 
    
#     cycle_length = param_dict['cycleLength']
#     expected_stimFreq = param_dict['stimFreq']
#     t_sampling = param_dict['timeSampling']

#     peak = .7 #V
#     v_stim = 5 #V
#     min_current = 50 # mA 
#     expected_current = 85 # ma
    
#     plate_sum_stats_df = summary_stats_table.loc[summary_stats_table['plate_id'] == plate]
#     for idx, row in plate_sum_stats_df.iterrows(): 

#         full_charge_difference = row ['full charge difference (C)']
#         neg_max = row['neg peaks max(V)']
#         pos_max = row['pos peaks max(V)']
#         stimFreq = row['frequency(Hz)']
#         avg_pos_current = row['avg pos i (mA)']
#         avg_neg_current = row['avg neg i (mA)']
#         date = row['day_time']

#         if abs(full_charge_difference > .1) : 
#             errors, all_errors, valid = addErr('charge', full_charge_difference, '< .1', plate, date, errors, all_errors, valid)
        
#         if abs(neg_max) > peak * 2 or pos_max > peak * 2: 
#             data = (neg_max, pos_max)
#             expected = f'neg pulse max > {-peak * 2} and pos pulse max <  {peak * 2}'
#             errors, all_errors, valid = addErr('(neg pulse max, pos pulse max)', data, expected, plate, date, errors, all_errors, valid)
        
#         if stimFreq != expected_stimFreq:
#             errors, all_errors, valid = addErr('Stimulation Frequency', stimFreq, expected_stimFreq, plate, date, errors, all_errors, valid)

#         if avg_pos_current < min_current or avg_pos_current > expected_current * .5 or abs(avg_neg_current) < min_current or abs(avg_neg_current) > expected_current * 1.5: 
#             data = (avg_pos_current, avg_neg_current)
#             expected = f'abs val current phases > {min_current} and average pos current = {expected_current} +/- {.5 * expected_current} and avg neg current {-expected_current} +/- {.5 * -expected_current}'
#             errors, all_errors, valid = addErr('(pos current, neg current)', data, expected, plate, date, errors, all_errors, valid)

# if not valid : 
#     print('** New Error Detected **')
#     SkelStimRangeErr(errors, variables)
# else : 
#     print('Normal Stimulation!')
                
# with open('all_errors.json', 'w') as file:
#     json.dump(all_errors, file, indent=4)
