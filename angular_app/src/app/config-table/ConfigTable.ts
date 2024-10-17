export interface ConfigTable {
  Stimulator: string;
  Stimulating: boolean
  T_AM : String;
  T_PM : String;
  voltage_expected : number;
  voltage_real : number;
  PulseOn: number;  
  PulseOn_real: number;  
  CycleLength: number;
  CycleLength_real: number;
  StimFrequency: number;
  StimFrequency_real: number;
  TimeSampling: number;
  StimulationStart: Date;
  StimulationEnd: Date;
  C1 : boolean;
  C2 : boolean;
  C3 : boolean;
  C4 : boolean;
  C5 : boolean;
  C6 : boolean;
  C7 : boolean;
}