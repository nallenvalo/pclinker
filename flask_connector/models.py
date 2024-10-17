from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()

class AppData(db.Model):
    __tablename__ = 'plate_log_data'
    id = db.Column(db.Integer, primary_key=True, autoincrement = True) # Corrected type definition
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
    
class CheckLogs(db.Model): 
    __tablename__ = 'check_logs'
    id = db.Column(db.Integer, primary_key=True, autoincrement = True) # Corrected type definition
    ranCheck = db.Column(db.Integer, nullable=False)
    plateName = db.Column(db.String(255), nullable = False)
    Channel = db.Column(db.Integer, nullable=False)
    Stimulating = db.Column(db.Integer, nullable=False)
    harvardAparatus = db.Column(db.Integer, nullable=False)
    current = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f'<CheckLogs {self.ranCheck, self.plateName, self.Channel, self.Stimulating, self.harvardAparatus}>'

    
class CheckLogsArchives(db.Model): 
    __tablename__ = 'check_logs_archives'
    id = db.Column(db.Integer, primary_key=True, autoincrement = True) # Corrected type definition
    t_stamp = db.Column(db.DateTime, nullable=False)
    ranCheck = db.Column(db.Integer, nullable=False)
    plateName = db.Column(db.String(255), nullable = False)
    Channel = db.Column(db.Integer, nullable=False)
    Stimulating = db.Column(db.Integer, nullable=False)
    harvardAparatus = db.Column(db.Integer, nullable=False)
    current = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f'<CheckLogs {self.ranCheck, self.plateName, self.Channel, self.Stimulating, self.harvardAparatus}>'
    
class shortedHarvards(db.Model): 
    __tablename__ = 'shorted_harvards'
    id = db.Column(db.Integer, primary_key=True, autoincrement = True) # Corrected type definition
    Stimulator = db.Column(db.Integer, nullable=False)
    voltage = db.Column(db.Float, nullable=True)
    stimFreq = db.Column(db.Float, nullable=True)
    pulseOn = db.Column(db.Float, nullable=True)


# class ConfigTable(db.Model): 
    
#     __tablename__ = 'config_table'
#     id = db.Column(db.Integer, primary_key=True, autoincrement = True) # Corrected type definition
#     Stimulator = db.Column(db.String(255), nullable = False)
#     Stimulating = db.Column(db.Boolean, nullable=False)
#     T_AM = db.Column(db.String(255), nullable = False)
#     T_PM = db.Column(db.String(255), nullable = False)
#     voltage_expected = db.Column(db.Float, nullable=True)
#     voltage_real = db.Column(db.Float, nullable=True)
#     PulseOn = db.Column(db.Float, nullable=True)
#     PulseOn_real = db.Column(db.Float, nullable=True)
#     CycleLength = db.Column(db.Float, nullable=True)
#     CycleLength_real = db.Column(db.Float, nullable=True)
#     StimFrequency = db.Column(db.Float, nullable=True)
#     StimFrequency_real = db.Column(db.Float, nullable=True)
#     TimeSampling = db.Column(db.Float, nullable=True)
#     StimulationStart = db.Column(db.DateTime, nullable=False)
#     StimulationEnd = db.Column(db.DateTime, nullable=False)
#     C1 = db.Column(db.Boolean, nullable=False)
#     C2 = db.Column(db.Boolean, nullable=False)
#     C3 = db.Column(db.Boolean, nullable=False)
#     C4 = db.Column(db.Boolean, nullable=False)
#     C5 = db.Column(db.Boolean, nullable=False)
#     C6 = db.Column(db.Boolean, nullable=False)
#     C7 = db.Column(db.Boolean, nullable=False)

#     def __repr__(self):
#         return f'<ConfigTable {self.voltage_expected, self.voltage_real}>'






