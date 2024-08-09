from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import text
from config import Config
from models import db, AppData
import pytz
from datetime import timedelta
from datetime import datetime
from flask_cors import CORS

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
                # id = i,
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

if __name__ == '__main__':
    app.run(debug=True)
