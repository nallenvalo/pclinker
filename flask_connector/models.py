from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()

class AppData(db.Model):
    __tablename__ = 'plate_log_data'
    id = db.Column(db.Integer, primary_key=True) # Corrected type definition
    name = db.Column(db.String(255), nullable = False)
    pulseOnLength = db.Column(db.Integer, nullable=False)
    HarvardAparatus = db.Column(db.Integer, nullable=False)
    Channel = db.Column(db.Integer, nullable=False)
    cycleLength = db.Column(db.Integer, nullable=False)
    plateName = db.Column(db.String(255), nullable=False)
    stimFreq = db.Column(db.Float, nullable=False)
    timeSampling = db.Column(db.Integer, nullable=False)
    stimulation_start = db.Column(db.DateTime, nullable=False)
    stimulation_end = db.Column(db.DateTime, nullable=False)
    pharmacological = db.Column(db.Boolean, nullable=False)
    Report_time1 = db.Column(db.DateTime, nullable=True)
    voltage1 = db.Column(db.Float, nullable=True)
    pulseDuration1 = db.Column(db.Float, nullable=True)
    frequency1 = db.Column(db.Float, nullable=True)
    current1 = db.Column(db.Float, nullable=True)
    charge1 = db.Column(db.Float, nullable=True)
    chargeDifference1 = db.Column(db.Float, nullable=True)
    maturationPercentage1 = db.Column(db.String(255), nullable=True)
    energy1 = db.Column(db.Float, nullable=True)
    rms1 = db.Column(db.Float, nullable=True)
    Report_time2 = db.Column(db.DateTime, nullable=True)
    voltage2 = db.Column(db.Float, nullable=True)
    pulseDuration2 = db.Column(db.Float, nullable=True)
    frequency2 = db.Column(db.Float, nullable=True)
    current2 = db.Column(db.Float, nullable=True)
    charge2 = db.Column(db.Float, nullable=True)
    chargeDifference2 = db.Column(db.Float, nullable=True)
    maturationPercentage2 = db.Column(db.String(255), nullable=True)
    energy2 = db.Column(db.Float, nullable=True)
    rms2 = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f'<SummaryStats {self.plateName}>'
