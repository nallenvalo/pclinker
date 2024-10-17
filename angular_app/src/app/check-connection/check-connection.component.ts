import { Component, EventEmitter, Input, Output, OnChanges, SimpleChanges, OnInit, Injectable} from '@angular/core';
import {MatTableModule} from '@angular/material/table';import { PlateLogs } from '../shared/Plate_logs';
import { CommonModule } from '@angular/common';
import {checkLogs} from './checkLogs'
import { PlateLogService } from '../shared/plate-log.service';
import { range, timeout, TimeoutError } from 'rxjs';
import { NumberValueAccessor } from '@angular/forms';

export interface checkTable {
  Platename: string;
  Harvard: number;
  Channel: number;
  RanCheck: boolean;
  Stimulating: boolean;
  current : number;
}

const plateTable : checkTable[] = []

@Component({
  selector: 'app-check-connection',
  standalone: true,
  imports: [MatTableModule, CommonModule],
  templateUrl: './check-connection.component.html',
  styleUrl: './check-connection.component.css'
})

export class CheckConnectionComponent implements OnInit{
  @Input() existingPlates: PlateLogs[] = [];
  plates : checkLogs[] = [];
  displayedColumns: string[] = ['Platename', 'Harvard', 'Channel', 'RanCheck','Stimulating', 'current'];
  idx = 0;
  ranCheck: number = 0;
  plateName = '';
  Channel !: number;
  harvardAparatus !: number;
  Stimulating: boolean = false;
  current !: number;

  not_all_checked : boolean = true
  reportReady : boolean = false;
  progress : number = 0;
  checkAndStim = false;
  ExistsErr = false;

  ngOnInit() {
    console.log('Init Ran')
    this.checkLogsEvent()
  }

  constructor(private plateLogService: PlateLogService) { }

  checkLogsEvent(){
    console.log('CheckLogs Ran')
    console.log(this.existingPlates)
    for (const plate of this.existingPlates){
      const temp = new checkLogs(0, plate.plateName, plate.Channel, 0, plate.HarvardAparatus, NaN);
      this.plates[this.idx] = temp;
      this.idx += 1
    }
  console.log('Logs to be checked; ', this.plates)
  this.CheckUpload()

  const checkInterval = 2500
  const maxAttempts = 20
  let attempts = 0
  let increment = 10

  const checkCompletion = () => {
    this.reportReady = false
    attempts += 1;
    if (this.progress == 50){ increment = increment / 2}
    if (this.progress == 75){ increment = increment / 2}

    console.log('increment : ', increment)
    this.CheckRetrieve();
    this.not_all_checked = this.plates.some(plate => plate.ranCheck == 0);

    // let num : number = 0 
    // this.plates.forEach(plate => {
    //   if (plate.ranCheck === 1){
    //     num++;
    //   }
    // });
    // const total : number = this.plates.length
    // const percentage : number = num / total

    if (this.not_all_checked && attempts < maxAttempts){
      this.reportReady = false
      console.log('Not all checks have been completed. Timing out and checking again.')
      setTimeout(checkCompletion, checkInterval)
      this.UpdateTable()
      this.progress += increment
      console.log('report ready : ', this.reportReady)
    }else if (this.not_all_checked && attempts >= maxAttempts ){
      console.log('failed to run checks')
      this.evalTable()
      this.reportReady = true
      this.progress = 100
    }
    else{ 
    console.log('All checks have been completed.')
    this.UpdateTable()
    this.evalTable()
    this.reportReady = true
    this.progress = 100
  }
  };
  setTimeout(checkCompletion, checkInterval)
}

  CheckUpload(){
    this.plateLogService.sendConnectionCheck(this.plates).subscribe(response => {
      console.log('Upload successful:', response);
    }, error => {
      console.error('Upload failed:', error);
    });
  }

  CheckRetrieve(){
    this.plateLogService.recieveConnectionCheck().subscribe(
      (data: any[]) => {
        this.plates = data.map(plate => new checkLogs(
          plate.ranCheck,
          plate.plateName,
          plate.Channel,
          plate.Stimulating,
          plate.harvardAparatus,
          plate.current
        ));
        console.log('Data Recieved:', this.plates);
      },
      error => console.error('Fetch failed:', error)
    );
  }

  UpdateTable() { 
    plateTable.length = 0
    // Reset the plateTable array before populating it 
    for (const plate of this.plates) { 
      const temp: checkTable = { 
        Platename: plate.plateName, 
        Harvard: plate.harvardAparatus,
        Channel : plate.Channel,
        RanCheck: plate.ranCheck === 1, 
        Stimulating: plate.Stimulating === 1,
        current : plate.current
      }; 
      plateTable.push(temp); 
      // Add the new object to the plateTable array 
      } 
      console.log('plateTable:', plateTable); 
      // this.reportReady = true
  }
  evalTable(){
    this.checkAndStim = this.plates.every(plate => plate.ranCheck && plate.Stimulating)
    this.ExistsErr = this.plates.some(plate => !plate.ranCheck || !plate.Stimulating)
  }
  dataSource = plateTable;
}
