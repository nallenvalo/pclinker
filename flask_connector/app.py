from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import text
from config import Config
from models import db, AppData, CheckLogs, CheckLogsArchives, shortedHarvards
import pytz
from datetime import timedelta
from datetime import datetime
from flask_cors import CORS
import subprocess
from subprocess import call
import os 

New_MYSQL_HOST = '10.10.100.41'

# Define the time zone for Eastern Time (ET)
et = pytz.timezone('US/Eastern')

# Get the current time in ET
now_et = datetime.now(et)

# Check if daylight saving time is in effect
if now_et.dst() != timedelta(0):
    t = 4  # EDT (Eastern Daylight Time)
else:
    t = 5  # EST (Eastern Standard Time)

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

# Initialize SQLAlchemy
db.init_app(app)
migrate = Migrate(app, db)

def parse_and_convert_to_utc(date_str):
    local_time = datetime.fromisoformat(date_str)
    return local_time.replace(tzinfo=pytz.UTC)

def table_exists(table_name):
    result = db.session.execute(text(f"SHOW TABLES LIKE '{table_name}'"))
    return result.scalar() is not None


def check_logs():
    command_path = "C:/Users/microscope/WebApp/check_connection.cmd"
    if os.path.exists(command_path):
        try:
            result = subprocess.run(command_path, 
                                    shell=True, 
                                    check=True, 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE)
            print('Sucessful run')
            return {'output': result.stdout.decode(), 'error': result.stderr.decode()}
        except subprocess.CalledProcessError as e:
            print(e)
            return {'output': None, 'error': str(e)}
    else: 
        print('path does not exist')

def save_plate_data():
    command_path = "C:/Users/microscope/webApp/save_logs.cmd"
    if os.path.exists(command_path):
        try:
            result = subprocess.run(command_path, 
                                    shell=True, 
                                    check=True, 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE)
            print('Plate Data Saved')
            return {'output': result.stdout.decode(), 'error': result.stderr.decode()}
        except subprocess.CalledProcessError as e:
            print(e)
            return {'output': None, 'error': str(e)}
    else: 
        print('path does not exist')

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return "Hello, Flask with app_data database!"

@app.route('/api/plate_logs', methods=['POST'])
def add_plate_logs():
    # Clear the existing table data where name is 'plate_log_data'
    if table_exists('plate_log_data'):
        try:
            db.session.execute(text('TRUNCATE TABLE plate_log_data'))
            db.session.commit()
        except Exception as e:
            print(f"Error clearing existing data: {e}")
            db.session.rollback()
            return jsonify({'error': 'Failed to clear existing data'}), 500
    
    data = request.json
    print("Received data:", data)
    new_logs = []
    for i, plate in enumerate(data):
        try:
            new_log = AppData(
                id = i,
                name=plate['name'],
                pulseOnLength=plate['pulseOnLength'],
                HarvardAparatus=plate['HarvardAparatus'],
                Channel=plate['Channel'],
                cycleLength=plate['cycleLength'],
                plateName=plate['plateName'],
                stimFreq=plate['stimFreq'],
                timeSampling=plate['timeSampling'],
                stimulation_start=(datetime.fromisoformat(plate['stimulation_start']) - timedelta(hours = t)),
                stimulation_end=(datetime.fromisoformat(plate['stimulation_end']) - timedelta(hours = t)),
                pharmacological=plate['pharmacological'],
                Report_time1=(datetime.fromisoformat(plate['Report_time1']) - timedelta(hours = t)) if plate.get('Report_time1') else None,
                voltage1=plate.get('voltage1', 0),
                pulseDuration1=plate.get('pulseDuration1', 0),
                frequency1=plate.get('frequency1', 0),
                current1=plate.get('current1', 0),
                charge1=plate.get('charge1', 0),
                chargeDifference1=plate.get('chargeDifference1', 0),
                energy1=plate.get('energy1', 0),
                rms1=plate.get('rms1', 0),
                Report_time2=(datetime.fromisoformat(plate['Report_time2']) - timedelta(hours = t))if plate.get('Report_time2') else None,
                voltage2=plate.get('voltage2', 0),
                pulseDuration2=plate.get('pulseDuration2', 0),
                frequency2=plate.get('frequency2', 0),
                current2=plate.get('current2', 0),
                charge2=plate.get('charge2', 0),
                chargeDifference2=plate.get('chargeDifference2', 0),
                energy2=plate.get('energy2', 0),
                rms2=plate.get('rms2', 0)
            )
            new_logs.append(new_log)
        except KeyError as e:
            print(f"Missing key in data: {e}")  # Debugging statement for missing keys
            return jsonify({'error': f"Missing key in data: {e}"}), 400
    
    db.session.bulk_save_objects(new_logs)
    db.session.commit()
    save_plate_data()
    return jsonify({'message': 'Plate logs added'}), 201

@app.route('/api/plate_logs', methods=['GET'])
def get_plate_logs():
    plate_logs = AppData.query.all()
    print(plate_logs)
    result = []
    for log in plate_logs:
        if log is not None:
            log_data = {
                'name': log.name if log.name else None,
                'pulseOnLength': log.pulseOnLength,
                'HarvardAparatus': log.HarvardAparatus,
                'Channel': log.Channel,
                'cycleLength': log.cycleLength,
                'plateName': log.plateName,
                'stimFreq': log.stimFreq,
                'timeSampling': log.timeSampling,
                'stimulation_start': log.stimulation_start.isoformat(),
                'stimulation_end': log.stimulation_end.isoformat(),
                'pharmacological': log.pharmacological,
                'Report_time1': log.Report_time1.isoformat() if log.Report_time1 else None,
                'voltage1': log.voltage1,
                'pulseDuration1': log.pulseDuration1,
                'frequency1': log.frequency1,
                'current1': log.current1,
                'charge1': log.charge1,
                'chargeDifference1': log.chargeDifference1,
                'energy1': log.energy1,
                'rms1': log.rms1,
                'Report_time2': log.Report_time2.isoformat() if log.Report_time2 else None,
                'voltage2': log.voltage2,
                'pulseDuration2': log.pulseDuration2,
                'frequency2': log.frequency2,
                'current2': log.current2,
                'charge2': log.charge2,
                'chargeDifference2': log.chargeDifference2,
                'energy2': log.energy2,
                'rms2': log.rms2
            }
            result.append(log_data)
    return jsonify(result), 200

    
@app.route('/api/check_logs', methods=['POST'])
def add_check_logs():
# Clear the existing table data where name is 'check_logs'
    if table_exists('check_logs'):
        try:
            db.session.execute(text('TRUNCATE TABLE check_logs'))
            db.session.commit()
        except Exception as e:
            print(f"Error clearing existing data: {e}")
            db.session.rollback()
            return jsonify({'error': 'Failed to clear existing data'}), 500
    
    data = request.json
    print("Received data:", data)
    new_logs = []
    new_logs_archives = []
    for i, plate in enumerate(data):
        try:
            new_log = CheckLogs(
                #id = i,
                ranCheck = plate['ranCheck'],
                plateName = plate['plateName'],
                Channel = plate['Channel'],
                Stimulating = plate['Stimulating'],
                harvardAparatus=plate['harvardAparatus'],
                current = plate['current'],
            )
            new_logs_archive = CheckLogsArchives(
                #id = i,
                ranCheck = plate['ranCheck'],
                t_stamp = datetime.now(),
                plateName = plate['plateName'],
                Channel = plate['Channel'],
                Stimulating = plate['Stimulating'],
                harvardAparatus=plate['harvardAparatus'],
                current = plate['current'],
            )
            new_logs.append(new_log)
            new_logs_archives.append(new_logs_archive)
        except KeyError as e:
            print(f"Missing key in data: {e}")  # Debugging statement for missing keys
            return jsonify({'error': f"Missing key in data: {e}"}), 400
    print('Sending :', new_logs)
    db.session.bulk_save_objects(new_logs)
    db.session.bulk_save_objects(new_logs_archives)
    db.session.commit()
    check_logs()
    return jsonify({'message': 'Check logs added and Checker has ran on PC 1'}), 201

@app.route('/api/check_logs', methods=['GET'])
def get_check_logs():
    plate_logs = CheckLogs.query.all()
    print(plate_logs)
    result = []
    for log in plate_logs:
        if log is not None:
            log_data = {
                'ranCheck' : log.ranCheck,
                'plateName': log.plateName if log.plateName else None,
                'Channel': log.Channel,
                'Stimulating' : log.Stimulating,
                'harvardAparatus': log.harvardAparatus,
                'current' : log.current
            }
            result.append(log_data)
    return jsonify(result), 200

@app.route('/api/shorted_harvard', methods=['GET'])
def harvard_data():
    print('Quering Shorted Harvard Aparatus Data table..')
    harvard_table = shortedHarvards.query.all()
    print(harvard_table)
    result = []
    for log in harvard_table:
        if log is not None:
            harvard_data = {
                'Stimulator' : log.Stimulator, 
                'voltage': log.voltage,
                'stimFreq' : log.stimFreq,
                'pulseOn' : log.pulseOn,
            }
            result.append(harvard_data)
    return jsonify(result), 200


# @app.route('/api/config_table_route', methods=['POST'])
# def add_config_table():
#     print('post request recieved')
#     # Clear the existing table data where name is 'check_logs'
#     if table_exists('config_table'):
#         try:
#             db.session.execute(text('TRUNCATE TABLE config_table'))
#             db.session.commit()
#         except Exception as e:
#             print(f"Error clearing existing data: {e}")
#             db.session.rollback()
#             return jsonify({'error': 'Failed to clear existing data'}), 500
    
#     data = request.json
#     print("Configuration data recieved:", data)
#     rows = []
#     for i, row  in enumerate(data):
#         try:
#             new_row = ConfigTable(
#                 #id = i,
#                 Stimulator = row['Stimulator'],
#                 Stimulating = row['Stimulating'],
#                 T_AM = row['T_AM'],
#                 T_PM = row['T_PM'],
#                 voltage_expected = row['voltage_expected'],
#                 voltage_real = row['voltage_real'],
#                 PulseOn = row['PulseOn'],
#                 PulseOn_real = row['PulseOn_real'],
#                 CycleLength = row['CycleLength'],
#                 CycleLength_real = row['CycleLength_real'],
#                 StimFrequency = row['StimFrequency'], 
#                 StimFrequency_real = row['StimFrequency_real'], 
#                 TimeSampling = row['TimeSampling'], 
#                 StimulationStart = datetime.now(),
#                 StimulationEnd =  datetime.now(),
#                 C1 =  row['C1'],
#                 C2 =  row['C2'],
#                 C3 =  row['C3'],
#                 C4 =  row['C4'],
#                 C5 =  row['C5'],
#                 C6 =  row['C6'],
#                 C7 =  row['C7']
#             )
#             rows.append(new_row)
#         except KeyError as e:
#             print(f"Missing key in data: {e}")  # Debugging statement for missing keys
#             return jsonify({'error': f"Missing key in data: {e}"}), 400
#     db.session.bulk_save_objects(rows)
#     db.session.commit()
#     return jsonify({'message': 'ConfigTable has been uploaded to SQL'}), 201

# @app.route('/api/config_table_route', methods=['GET'])
# def get_config_table():
#     print('Quering configuration table..')
#     config_table = ConfigTable.query.all()
#     print(config_table)
#     result = []
#     for log in config_table:
#         if log is not None:
#             log_data = {
#                 'Stimulator' : log.Stimulator, 
#                 'Stimulating': log.Stimulating,
#                 'T_AM' : log.T_AM,
#                 'T_PM' : log.T_PM,
#                 'voltage_expected' : log.voltage_expected if log.voltage_expected else None,
#                 'voltage_real' : log.voltage_real if log.voltage_real else None,
#                 'PulseOn' : log.PulseOn if log.PulseOn else None,
#                 'PulseOn_real' : log.PulseOn_real if log.PulseOn_real else None,
#                 'CycleLength' : log.CycleLength if log.CycleLength else None,
#                 'CycleLength' : log.CycleLength_real if log.CycleLength_real else None,
#                 'StimFrequency' : log.StimFrequency if log.StimFrequency else None,
#                 'StimFrequency_real' : log.StimFrequency_real if log.StimFrequency_real else None,
#                 'TimeSampling' : log.TimeSampling, 
#                 'StimulationStart' : log.StimulationStart, 
#                 'StimulationEnd' : log.StimulationEnd,
#                 'C1' : log.C1,
#                 'C2' : log.C2,
#                 'C3' : log.C3,
#                 'C4' : log.C4,
#                 'C5' : log.C5,
#                 'C6' : log.C6,
#                 'C7' : log.C7,
#             }
#             result.append(log_data)
#     return jsonify(result), 200
if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host = "10.10.100.15", debug=True)
    #app.run(debug=True)

