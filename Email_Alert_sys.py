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
def SkelStimRangeErr(errors_list):
#  tup = [plate, 'snr', data, date, HA_]
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    id_sender = 'skeletalstimulation@gmail.com'
    password_sender = 'ftey xyeq jlwv llqx' # NOTE THAT THIS IS FROM GOOGLE GMAIL APP PASSWORDS AT BOTTOM OF 2FA
    id_receipients = ['nallen@valohealth.com']
    '''plate = plt
    signal = tup_[0]
    val = tup_[1]
    parts = data_stat.split('_')
    date = parts[0]
    HA = tup_[2]'''
    content = ''
    # tup = [plt, date, stat, data_, HA_]
    for item in errors_list:
        plate = item[0]
        signal = item[2]
        val = item[3]
        date = item[1]
        HA = item[4]
        line = f'Skeletal Stimulation {signal} is not expected for \n plate : {plate} of Harvard Aparatus {HA} on excercise period {date}. The value was {val} which is outside the expected range'
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


summary_stats_HA1 = "C:/Users/microscope/Desktop/SkeletalStimLogs/SkelStimWebApp/summary_stats_table_harvard1.csv"
summary_stats_HA2 = "C:/Users/microscope/Desktop/SkeletalStimLogs/SkelStimWebApp/summary_stats_table_harvard2.csv"

with open('variables.json', 'r') as file:
    variables = json.load(file)

HA1_Running = False
HA2_Running = False
HA1_plates = []
HA2_plates = []
# All plates in the vars dict are already active
for plate, vars_dict in variables.items():
    print( vars_dict['HarvardAparatus'])
    if vars_dict['HarvardAparatus'] == 1:
        HA1_Running = True
        HA1_plates.append(plate)
    elif vars_dict['HarvardAparatus'] == 2:
        HA2_Running = True
        HA2_plates.append(plate)

exit = False
if not os.path.exists(summary_stats_HA1) and HA1_Running:
    exit = True 
    MissingSKelStim('entire HA1', '0', datetime.now())
else:
    print('HA1 properly configured')
if not os.path.exists(summary_stats_HA2) and HA2_Running:
    exit = True
    MissingSKelStim('entire HA2', '0', datetime.now())
else:
    print('HA2 properly configured')
if exit : sys.exit(1)

if HA1_Running : summary_stats_HA1 = pd.read_csv(summary_stats_HA1)
if HA2_Running : summary_stats_HA2 = pd.read_csv(summary_stats_HA2)

for ha_list, sum_stats in zip([HA1_plates, HA2_plates], [summary_stats_HA1, summary_stats_HA2]):
    for plate in ha_list:
        plate_rows = sum_stats.loc[sum_stats['plate_id'] == plate]
        day_time_list = plate_rows['day_time']
        num = sum(1 for day in day_time_list if pd.to_datetime(day) > (datetime.now() - pd.Timedelta(hours=16)))
        start =  pd.to_datetime(variables[plate]['stimulation_start']) 
        if num < 2 and start > (datetime.now() - pd.Timedelta(hours=16)):
            MissingSKelStim(plate, datetime.now(), num)
        else :
            print(f"Proper stimulation for {plate}")

'''
mean, median	
std, variance
min, max
range	
rms, snr	
energy	
pos peaks count
pos peaks mean, pos peaks median
pos peaks std	
pos peaks min, pos peaks max	
neg peaks count
neg peaks mean, neg peaks median	
neg peaks std	
neg peaks min, neg peaks max
'''
with open('all_errors.json', 'r') as file:
    all_errors = json.load(file)
errors = []
valid = True

def addErr(stat, table, errs, plt, allErrors, bool_, data_):
    if plt not in allErrors.keys(): all_errors[plt] = {}
    date = table.loc[table.index == idx]['day_time'].iloc[0]
    tup = [plt, date, stat, data_, HA_]
    key = date + '_' + stat
    if key not in all_errors[plate].keys(): 
        bool_ = False
        allErrors[plate][key] = []
        allErrors[plate][key].append(tup[2:])
        errors.append(tup)
    return errs, allErrors, bool_

# def SkelStimRangeErr(plate, signal, date, HA):
for plate, param_dict in variables.items(): 
   
    if plate in HA1_plates:
        sum_stats = summary_stats_HA1
        HA_ = 1
    else : 
        sum_stats = summary_stats_HA2
        HA_ = 2

    snr = sum_stats['snr']
    for idx, data in enumerate(snr): 
        if data < .01 * param_dict['pulseOnLength'] or data > param_dict['pulseOnLength']/param_dict['cycleLength'] :
            '''if plate not in all_errors.keys(): all_errors[plate] = {}
            date = sum_stats.loc[sum_stats.index == idx]['day_time'].iloc[0]
            tup = [plate, date, 'snr', data, HA_]
            if date not in all_errors[plate].keys(): 
                valid = False
                all_errors[plate][date] = []
                all_errors[plate][date].append(tup[2:])
                errors.append(tup)'''
            errors, all_errors, valid = addErr('snr', sum_stats, errors, plate, all_errors, valid, data)

    mean = sum_stats['mean']
    for idx, data in enumerate(mean): 
        if abs(data) > .1:
            errors, all_errors, valid = addErr('mean', sum_stats, errors, plate, all_errors, valid, data)

    max, min = sum_stats['max'], sum_stats['min']
    for idx, (max, min) in enumerate(zip(max, min)): 
        if max > 5.1 or min < -5.1:
            data = (max, min) if max and min else []
            errors, all_errors, valid = addErr('minmax', sum_stats, errors, plate, all_errors, valid, data)

    range = sum_stats['range']
    for idx, data in enumerate(range):
        if data > 11 or data < 9:
            errors, all_errors, valid = addErr('range', sum_stats, errors, plate, all_errors, valid, data)

    pos_peaks, neg_peaks = sum_stats['pos peaks count'], sum_stats['neg peaks count']
    for idx, (pp, np) in enumerate(zip(pos_peaks, neg_peaks)): 
        if pp != np or pp != (param_dict['timeSampling'] / param_dict['cycleLength']) * param_dict['stimFreq'] or not pp or not np:
            data = (pp, np) if not pd.isna(pp) and not pd.isna(np) else []
            errors, all_errors, valid = addErr('peaks', sum_stats, errors, plate, all_errors, valid, data)

if not valid : 
    pass
    SkelStimRangeErr(errors)
else : 
    print('Normal Stimulation!')
                
with open('all_errors.json', 'w') as file:
    json.dump(all_errors, file, indent=4)
