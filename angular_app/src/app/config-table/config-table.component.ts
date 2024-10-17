import { Component, EventEmitter, Input, Output, OnChanges, SimpleChanges, OnInit } from '@angular/core';
import {MatTableModule} from '@angular/material/table';
import { PlateLogs } from '../shared/Plate_logs';
import { CommonModule } from '@angular/common';
import { ConfigTable } from './ConfigTable';
import { PlateLogService } from '../shared/plate-log.service';
import { shortedHarvard } from './shortedHarvard';

// export interface ConfigTable {
//   Stimulator: string;
//   Stimulating: boolean
//   T_AM : String;
//   T_PM : String;
//   voltage_expected : number;
//   PulseOn: number;  
//   CycleLength: number;
//   StimFrequency: number;
//   TimeSampling: number;
//   StimulationStart: Date;
//   StimulationEnd: Date;
//   C1 : boolean;
//   C2 : boolean;
//   C3 : boolean;
//   C4 : boolean;
//   C5 : boolean;
//   C6 : boolean;
//   C7 : boolean;
// }

const ELEMENT_DATA: ConfigTable[] = [
  {Stimulator: 'S88X 11', Stimulating : false, T_AM : '8:10:00', T_PM : '20:10:00', 
    voltage_expected : 5, 
    voltage_real : NaN,
    PulseOn: NaN,
    PulseOn_real: NaN,
    CycleLength: NaN, 
    CycleLength_real : NaN,
    StimFrequency: NaN,
    StimFrequency_real : NaN,
    TimeSampling: NaN, 
    StimulationStart: new Date (), StimulationEnd: new Date(),
    C1 : false,
    C2 : false,
    C3 : false,
    C4 : false,
    C5 : false,
    C6 : false,
    C7 : false},
  {Stimulator: 'Harvard2', Stimulating : false, T_AM : '6:00:00', T_PM : '18:00:00',
    voltage_expected : 5, 
    voltage_real : NaN,
    PulseOn: NaN,
    PulseOn_real: NaN,
    CycleLength: NaN, 
    CycleLength_real : NaN,
    StimFrequency: NaN,
    StimFrequency_real : NaN,
    TimeSampling: NaN, 
    StimulationStart: new Date (), StimulationEnd: new Date(),
    C1 : false,
    C2 : false,
    C3 : false,
    C4 : false,
    C5 : false,
    C6 : false,
    C7 : false},
  {Stimulator: 'Harvard3', Stimulating : false, T_AM : '6:00:00', T_PM : '18:00:00', 
    voltage_expected : 5, 
    voltage_real : NaN,
    PulseOn: NaN,
    PulseOn_real: NaN,
    CycleLength: NaN, 
    CycleLength_real : NaN,
    StimFrequency: NaN,
    StimFrequency_real : NaN,
    TimeSampling: NaN, 
    StimulationStart: new Date (), StimulationEnd: new Date(),
    C1 : false,
    C2 : false,
    C3 : false,
    C4 : false,
    C5 : false,
    C6 : false,
    C7 : false}
];

@Component({
  selector: 'app-config-table',
  standalone: true,
  imports: [MatTableModule, CommonModule],
  templateUrl: './config-table.component.html',
  styleUrl: './config-table.component.css'
})

export class ConfigTableComponent implements OnChanges{ //, OnInit{
  @Input() existingPlates: PlateLogs[] = [];
  // 'StimulationStart', 'StimulationEnd', 
  shortedHarvardData : shortedHarvard[] = [];
  displayedColumns: string[] = ['Stimulator', 'Stimulating', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'T_AM', 'T_PM', 'voltage_expected', 'voltage_real', 'PulseOn', 'PulseOn_real', 'StimFrequency', 'StimFrequency_real', 'CycleLength', 'TimeSampling'];
  result: ConfigTable[] = [];
  box_bool : boolean = true;
  possibleNums : Array<number> = [1,2,3,4,5,6,7]
  possibleChannels : Array<number> = [1,2,3,4,5,6,7]
  possibleHarvards : Array<number> = [1,2,3]
  
  //Update element data to incorporate all of the real data from the different HAs
  //  ngOnInit(){
  //   console.log('Sending Config Tables')
  //   this.sendConfig();
  //   setTimeout(this.CheckRetrieve, 3000)
  // }
  // Add the shorted voltage on the plate log component and display it here
  // Will instead load everything in from the SQL database
  ngOnChanges(changes : SimpleChanges){
    console.log(this.existingPlates)
    if (changes['existingPlates']){
      console.log('changes detected')
      this.harvardDataRetrieve()
      console.log('adding harvard data to table :', this.shortedHarvardData)
      // will preform operation, for i in possible harvards 
      // we will create a new row ConfigTable element 
      // We will push it onto the current config table array 
      // We will pull the table form SQL and subsequently update all of the parts 
      for(let row of ELEMENT_DATA){
        const num = row.Stimulator.slice(-1)
        if (this.getUniqueHarvardApparatus().includes(num)){
          const uniqueChannels = this.getUniqueChannels(parseInt(num))
          row.Stimulating = true
          if (!uniqueChannels.includes(1)){row.C1 = true} else {row.C1 = false}
          if (!uniqueChannels.includes(2)){row.C2 = true} else {row.C2 = false}
          if (!uniqueChannels.includes(3)){row.C3 = true} else {row.C3 = false}
          if (!uniqueChannels.includes(4)){row.C4 = true} else {row.C4 = false}
          if (!uniqueChannels.includes(5)){row.C5 = true} else {row.C5 = false}
          if (!uniqueChannels.includes(6)){row.C6 = true} else {row.C6 = false}
          if (!uniqueChannels.includes(7)){row.C7 = true} else {row.C7 = false}
        }else {
          row.Stimulating = false
          row.C1 = false
          row.C2 = false
          row.C3 = false
          row.C4 = false
          row.C5 = false
          row.C6 = false
          row.C7 = false
        }
        for (const i of this.possibleHarvards){
          if (parseInt(num) == i){
            for (const plate of this.existingPlates){
              if (plate.HarvardAparatus == i){
                row.CycleLength = plate.cycleLength
                row.PulseOn = plate.pulseOnLength
                row.StimFrequency = plate.stimFreq
                row.StimulationEnd = plate.stimulation_end
                row.StimulationStart = plate.stimulation_start
                row.TimeSampling = plate.timeSampling
            }
          }
          if (this.getUniqueHarvardApparatus().includes(num)){
          setTimeout(() => {
            row = this.update_table_real(num, row);
          }, 3000);
        }
        }
      }
    }
    }
  }

  constructor(private plateLogService: PlateLogService) { }

  update_table_real(num : string, row : ConfigTable){
    const real_data_row = this.shortedHarvardData.find(row => row.Stimulator === parseInt(num))
    console.log(real_data_row)
    if (real_data_row){
      row.voltage_real = real_data_row.voltage
      row.PulseOn_real = real_data_row.pulseOn
      row.StimFrequency_real = real_data_row.stimFreq
    }
    return row
  }

  getUniqueHarvardApparatus() {
    const harvardSet = new Set(this.existingPlates.map(log => log.HarvardAparatus.toString()));
    return Array.from(harvardSet);
  }

  getUniqueChannels(harvard : number) {
    const ChannelSet : Array<number> = []
    for (const plate of this.existingPlates) {
      if(plate.HarvardAparatus == harvard) {
        ChannelSet.push(plate.Channel)
      }
    }
    const result : Array<number> = []
    for (const channel of this.possibleChannels){
      if (!ChannelSet.includes(channel))
        result.push(channel)
    }
    return result 
  }

  sendConfig(){
    // this.plateLogService.SendConfigTable(ELEMENT_DATA)
    // console.log('sent config log data')
    this.plateLogService.SendConfigTable(ELEMENT_DATA).subscribe(
      response => console.log('Upload successful:', response),
      error => console.error('Upload failed:', error)
    );
  }

  harvardDataRetrieve(){ 
    console.log('Attempting to retrieve data')
    this.plateLogService.RetrieveHarvardData().subscribe(
      (data : any []) => { 
        console.log('shorted Harvard Data : data')
        this.shortedHarvardData = data.map(stim => new shortedHarvard(
          stim.Stimulator,
          stim.voltage,
          stim.stimFreq,
          stim.pulseOn
        ));
        console.log('Data Received:', this.shortedHarvardData);
    },
    error => console.error('upload failed', error)
  )
  }

  CheckRetrieve() {
    console.log('Attempted to retrieve data')
    this.plateLogService.RetrieveConfigTable().subscribe(
      (data: any[]) => {
        console.log(data)
        this.result = data.map(row => ({
          Stimulator: row.Stimulator,
          Stimulating: row.Stimulating,
          T_AM: row.T_AM,
          T_PM: row.T_PM,
          voltage_expected: row.voltage_expected,
          voltage_real: row.voltage_real,
          PulseOn: row.PulseOn,
          PulseOn_real: row.PulseOn_real,
          CycleLength: row.CycleLength,
          CycleLength_real: row.CycleLength_real,
          StimFrequency: row.StimFrequency,
          StimFrequency_real: row.StimFrequency_real,
          TimeSampling: row.TimeSampling,
          StimulationStart: row.StimulationStart,
          StimulationEnd: row.StimulationEnd,
          C1: row.C1,
          C2: row.C2,
          C3: row.C3,
          C4: row.C4,
          C5: row.C5,
          C6: row.C6,
          C7: row.C7
        }));
        console.log('Data Received:', this.result);
      },
      error => console.error('Fetch failed:', error)
    );
  }
  
  dataSource = ELEMENT_DATA;
}