// src/app/shared/Plate_logs.ts
export class PlateLogs {
  // Constructor
  constructor(
    // User-Controlled
    public name : string,
    public pulseOnLength: number,
    public HarvardAparatus: number,
    public Channel: number,
    public cycleLength: number,
    public plateName: string,
    public stimFreq: number,
    public timeSampling: number,
    public stimulation_start: Date,
    public stimulation_end: Date,
    public pharmacological: boolean,
    // Data Report
    public Report_time1: Date,
    public voltage1: number,
    public pulseDuration1: number,
    public frequency1: number,
    public current1: number,
    public chargeDifference1: number,
    public rms1: number,
    public Report_time2: Date,
    public voltage2: number,
    public pulseDuration2: number,
    public frequency2: number,
    public current2: number,
    public chargeDifference2: number,
    public rms2: number
  ) {
    // Initialization
    this.name = name;
    this.pulseOnLength = pulseOnLength;
    this.HarvardAparatus = HarvardAparatus;
    this.Channel = Channel;
    this.cycleLength = cycleLength;
    this.plateName = plateName;
    this.stimFreq = stimFreq;
    this.timeSampling = timeSampling;
    this.stimulation_start = stimulation_start;
    this.stimulation_end = stimulation_end;
    this.pharmacological = pharmacological;
    this.Report_time1 = Report_time1;
    this.voltage1 = voltage1;
    this.pulseDuration1 = pulseDuration1;
    this.frequency1 = frequency1;
    this.current1 = current1;
    this.chargeDifference1 = chargeDifference1;
    this.rms1 = rms1;
    this.Report_time2 = Report_time2;
    this.voltage2 = voltage2;
    this.pulseDuration2 = pulseDuration2;
    this.frequency2 = frequency2;
    this.current2 = current2;
    this.chargeDifference2 = chargeDifference2;
    this.rms2 = rms2;
  }

  getMaturationPercentage(): number {
    const now = new Date();
    const totalDuration = this.stimulation_end.getTime() - this.stimulation_start.getTime();
    const elapsed = now.getTime() - this.stimulation_start.getTime();
    return parseFloat(Math.max(0, Math.min((elapsed / totalDuration) * 100, 100)).toFixed(4)); // Ensure it doesn't exceed 100%
  }
  toUTC() {
    this.stimulation_start = new Date(this.stimulation_start.toISOString());
    this.stimulation_end = new Date(this.stimulation_end.toISOString());
    if (this.Report_time1) this.Report_time1 = new Date(this.Report_time1.toISOString());
    if (this.Report_time2) this.Report_time2 = new Date(this.Report_time2.toISOString());
  }
}