// src/app/app.component.ts
import { Component, OnInit, EventEmitter, Output, Injectable } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';
import { PlateLogs } from './shared/Plate_logs';
import { SeedingFormComponent } from './seeding-form/seeding-form.component';
import { FilterDropdownComponent } from './filter-dropdown-component/filter-dropdown-component.component';
import { provideHttpClient} from '@angular/common/http';  // Import HttpClient and provideHttpClient
import { HttpClientModule } from '@angular/common/http';
import { PlateLogService } from './shared/plate-log.service';  // Import the service
import { FormsModule } from '@angular/forms'; // Import FormsModule
import {MatTableModule} from '@angular/material/table';
import {ConfigTableComponent} from './config-table/config-table.component';
import { CheckConnectionComponent } from './check-connection/check-connection.component';
import { stringify } from 'querystring';
import { filter } from 'rxjs';

//import { EventEmitter } from 'stream';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, CommonModule, SeedingFormComponent, FilterDropdownComponent, FormsModule, HttpClientModule, ConfigTableComponent, CheckConnectionComponent, MatTableModule],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  providers: []
})

export class AppComponent implements OnInit {
  @Output() checkLogsEvent = new EventEmitter<void>();
  title = 'homes';
  plate_logs: PlateLogs[] = [];
  showForm = false;
  showFilterDropdown = false;
  showConfigTable = false;
  CheckTable = false;
  selectedPlate: PlateLogs | null = null;
  selectedIndex: number | null = null;
  editMode = false;
  showMeta = false;
  showSettings = false;
  compress: boolean = false;
  applyChangesMode = false; // New flag for apply changes mode
  selectedHarvardAparatus: number | null = null; // Harvard Aparatus to apply changes to

  numDays : number = 35;
  newPulseOnLength: number | null = null;
  newCycleLength: number | null = null;
  newTimeSampling: number | null = null;
  newStimFreq: number | null = null;
  newStimulationStart: string | null = null;
  newStimulationEnd: string | null = null;
  newPharmacological: boolean | null = null;
  
  editCellLines : boolean = false;
  editPlatformCodes : boolean = false;
  editUsers : boolean = false;
  tempCell : string = ''
  cellLines : Array<string> = []
  tempPlt : string = ''
  platformCodes : Array<string> = []
  tempUsers : string = ''
  Users : Array<string> = []

  filters : {harvardAparatus : string []} = {
    harvardAparatus: ['all']
  };

  filter_key : {[key : string] : string} = {
    'all' : 'all',
    '1' : 'S88X 11',
    '2' : 'HA 2',
    '3' : 'HA 3',
  };

  filter_text = this.filters.harvardAparatus.map(fil => this.filter_key[fil])

  constructor(private plateLogService: PlateLogService) { }

  ngOnInit() {
    // will take out loadplates once we get the 
    // backend functionality
    // this.loadPlates();
    // this.refreshMaturation();
    // this.uploadPlates() 
    this.fetchPlates() 
    this.loadMetaData()
  }

  loadMetaData(){
    const platforms = localStorage.getItem('platformCodes')
    const cellLines = localStorage.getItem('cellLines')
    const Users = localStorage.getItem('Users')
    console.log('processing meta data')
    console.log('platforms : ', platforms)
    if (platforms){
      console.log('codes read')
      this.platformCodes = JSON.parse(platforms)
    }
    if (cellLines){
      this.cellLines = JSON.parse(cellLines)
    }
    if (Users){
      this.Users = JSON.parse(Users)
    }
  }

  saveChangesPlatform(){ 
    this.platformCodes = this.platformCodes.filter(code => code.trim() !== '')
    localStorage.setItem('platformCodes', JSON.stringify(this.platformCodes))
    console.log('plts saved')
    //this.editPlatformCodes = false
  }

  saveChangesCell(){ 
    this.cellLines = this.cellLines.filter(code => code.trim() !== '')
    localStorage.setItem('cellLines', JSON.stringify(this.cellLines))
    console.log('cellLines saved')
    //this.editCellLines = false
  }

  saveChangesUsers(){ 
    this.Users = this.Users.filter(code => code.trim() !== '')
    localStorage.setItem('Users', JSON.stringify(this.Users))
    console.log('cellLines saved')
    //this.editUsers = false
  }

  addPlatform(){
    this.platformCodes.push(this.tempPlt)
    this.tempPlt = ''
    this.saveChangesPlatform()
  }

  addCell(){
    this.cellLines.push(this.tempCell)
    this.tempCell = ''
    this.saveChangesCell()
  }

  addUsers(){
    this.Users.push(this.tempUsers)
    this.tempUsers = ''
    this.saveChangesUsers()
  }

  removePlatform(i : number){
    this.platformCodes.splice(i, 1)
    this.saveChangesPlatform()
  }

  removeCell(i : number){
    this.cellLines.splice(i, 1)
    this.saveChangesCell()
  }

  removeUsers(i : number){
    this.Users.splice(i, 1)
    this.saveChangesUsers()
  }

  togglePlatform() {
    this.editPlatformCodes = !this.editPlatformCodes
  }

  toggleCell() {
    this.editCellLines = !this.editCellLines
  }

  toggleUsers() {
    this.editUsers = !this.editUsers
  }

  toggleSettings(){
    this.showSettings = !this.showSettings
    this.editCellLines = false;
    this.editPlatformCodes = false;
    this.editUsers = false;
  }

  toggleCompress() {
    this.compress = !this.compress
  }

  toggleShowMeta(){
    this.showSettings = false;
    this.showMeta = !this.showMeta
    this.applyChangesMode = false;
    this.showForm = false;
    this.editCellLines = false;
    this.editPlatformCodes = false;
    this.editUsers = false;
  }

  toggleForm() {
    this.showForm = !this.showForm;
    this.showMeta = false
    this.applyChangesMode = false;
  }

  toggleFilterDropdown() {
    this.showFilterDropdown = !this.showFilterDropdown;
    this.showMeta = false
  }

  onFilterChange(selectedFilters: string[]) {
    this.filters.harvardAparatus = selectedFilters;
    this.filter_text = this.filters.harvardAparatus.map(fil => this.filter_key[fil])
  }

  addNewPlate(event: {index: number | null, plate: PlateLogs}) {
    if (event.index !== null) {
      this.plate_logs[event.index] = event.plate;
    } else {
      this.plate_logs.push(event.plate);
    }
    this.savePlates();
    //this.showForm = false;
    this.selectedIndex = null;
    this.selectedPlate = null;
    this.refreshMaturation();
  }

  plateError(plate : PlateLogs) : boolean{
    //return true
    if (this.firstTwoStimsRan(plate)){
    if (!(plate.current1 > 50 && plate.current2 > 50)) return false
    //if ((plate.chargeDifference1 > .1 )) return false
    if ((plate.stimFreq != plate.frequency1 || plate.stimFreq != plate.frequency2 )) return false
  }
    return true

  }
  
  getCurrentDateYYMMDD(): string {
    const date = new Date();
    const year = date.getFullYear().toString().slice(-2);
    const month = ('0' + (date.getMonth() + 1)).slice(-2);
    const day = ('0' + date.getDate()).slice(-2);
    return `${year}${month}${day}`;
  }

  firstTwoStimsRan(plate : PlateLogs) : boolean {
    const today = new Date() //this.getCurrentDateYYMMDD();
    const first_two_stims_ran = new Date(plate.stimulation_start)
    first_two_stims_ran.setDate(first_two_stims_ran.getDate() + 1)
    return today > first_two_stims_ran 
  }

  cancelForm() {
    this.showForm = false;
    this.selectedPlate = null;
    this.selectedIndex = null;
  }

  toggleCheckTable() {
    if (!this.CheckTable){ 
      const confirmation = confirm('Note that this sends one 2 millisecond biphasic pulse through the tissues. Do you wish to continue?');
      if (confirmation){
        //this.savePlates();
        console.log('check table : ', this.CheckTable)
        this.CheckTable = !this.CheckTable
        this.checkLogsEvent.emit()
        console.log('check table : ', this.CheckTable)}
  }else{
    this.CheckTable = !this.CheckTable
  }
}

  editPlate(index: number) {
    this.selectedPlate = this.plate_logs[index];
    this.selectedIndex = index;
    this.showForm = true;
    this.editMode = true;
  }

  allAdded() {
    this.showForm = false;
  }

  toggleConfigTable(){
    this.showConfigTable = !this.showConfigTable
    console.log(this.showConfigTable)
  }
  
  
  toggleApplyChanges() {
    this.showForm = false;
    this.showMeta = false
    this.applyChangesMode = !this.applyChangesMode;
    if (this.applyChangesMode) {
      // Reset the selected Harvard Aparatus and the new values
      this.selectedHarvardAparatus = null;
      this.newPulseOnLength = 1;
      this.newCycleLength = 10;
      this.newTimeSampling = 3600;
      this.newStimFreq = 10;
      this.newStimulationStart = null;
      this.newStimulationEnd = null;
      this.newPharmacological = null;
    }
  }

  applyChanges() {
    if (this.selectedHarvardAparatus !== null) {
      console.log('Selected Harvard Apparatus:', this.selectedHarvardAparatus);
      console.log('New Values:', {
        newPulseOnLength: this.newPulseOnLength,
        newCycleLength: this.newCycleLength,
        newTimeSampling: this.newTimeSampling,
        newStimFreq: this.newStimFreq,
        newStimulationStart: this.newStimulationStart,
        newStimulationEnd: this.newStimulationEnd,
        newPharmacological: this.newPharmacological,
      });
  
      this.plate_logs.forEach(plate => {
        console.log(`Checking plate with Harvard Apparatus: ${plate.HarvardAparatus}`);
        if (Number(plate.HarvardAparatus) === Number(this.selectedHarvardAparatus)) {
          console.log('Updating plate:', plate);
          if (this.newPulseOnLength !== null) plate.pulseOnLength = this.newPulseOnLength;
          if (this.newCycleLength !== null) plate.cycleLength = this.newCycleLength;
          if (this.newTimeSampling !== null) plate.timeSampling = this.newTimeSampling;
          if (this.newStimFreq !== null) plate.stimFreq = this.newStimFreq;
          if (this.newStimulationStart !== null) {
            plate.stimulation_start = new Date(this.newStimulationStart)
            const endDate = new Date(this.newStimulationStart)
            endDate.setDate(endDate.getDate() + this.numDays)
            plate.stimulation_end = endDate
          };
          //if (this.newStimulationEnd !== null) plate.stimulation_end = new Date(this.newStimulationEnd);
          if (this.newPharmacological !== null) plate.pharmacological = this.newPharmacological;
  
          console.log('Updated plate:', plate);
        }
      });
  
      console.log('Updated Plate Logs:', this.plate_logs);
      this.savePlates(); // Save the updated plates
      this.applyChangesMode = false; // Exit apply changes mode
    }
  }

  getIndex(plate : PlateLogs) : number{ 
    return this.plate_logs.indexOf(plate)
  }
  
  deletePlate(index: number) {
    const confirmation = confirm('Are you sure you want to delete this plate log?');

    if (confirmation) {
      // Proceed with deletion if the user confirms
      this.plate_logs.splice(index, 1);
      this.savePlates();
      this.editMode = false;
    } else {
      // Do nothing if the user cancels
      console.log('Deletion cancelled');
    }
  }

  savePlates() {
      console.log('Data to be sent:', this.plate_logs);
      this.plateLogService.addPlateLogs(this.plate_logs).subscribe(
        response => console.log('Upload successful:', response),
        error => console.error('Upload failed:', error)
      );
    //}, error => console.error('Clear failed:', error));
    }

  loadPlates() {
    this.plateLogService.getPlateLogs().subscribe(
      (data: any[]) => {
        this.plate_logs = data.map(plate => new PlateLogs(
          plate.name,
          plate.pulseOnLength,
          plate.HarvardAparatus,
          plate.Channel,
          plate.cycleLength,
          plate.plateName,
          plate.stimFreq,
          plate.timeSampling,
          new Date(plate.stimulation_start),
          new Date(plate.stimulation_end),
          plate.pharmacological,
          new Date(plate.Report_time1),
          plate.voltage1,
          plate.pulseDuration1,
          plate.frequency1,
          plate.current1,
          plate.chargeDifference1,
          plate.rms1,
          new Date(plate.Report_time2),
          plate.voltage2,
          plate.pulseDuration2,
          plate.frequency2,
          plate.current2,
          plate.chargeDifference2,
          plate.rms2,
        ));
        this.refreshMaturation();
      },
      error => console.error('Fetch failed:', error)
    );
  }
  
  refreshMaturation() {
    this.plate_logs = this.plate_logs.map(plate => new PlateLogs(
      plate.name,
      plate.pulseOnLength,
      plate.HarvardAparatus,
      plate.Channel,
      plate.cycleLength,
      plate.plateName,
      plate.stimFreq,
      plate.timeSampling,
      plate.stimulation_start,
      plate.stimulation_end,
      plate.pharmacological,
      plate.Report_time1,
      plate.voltage1,
      plate.pulseDuration1,
      plate.frequency1,
      plate.current1,
      plate.chargeDifference1,
      plate.rms1,
      plate.Report_time2,
      plate.voltage2,
      plate.pulseDuration2,
      plate.frequency2,
      plate.current2,
      plate.chargeDifference2,
      plate.rms2,
    ));
  }
  getFilteredPlateLogs() {
    return this.plate_logs.filter(log => {
      if (this.filters.harvardAparatus.includes('all')) {
        return true;
      }
      return this.filters.harvardAparatus.includes(log.HarvardAparatus.toString());
    });
  }

  uploadPlates() {
    this.plateLogService.addPlateLogs(this.plate_logs).subscribe(response => {
      console.log('Upload successful:', response);
    }, error => {
      console.error('Upload failed:', error);
    });
  }

  fetchPlates() {
    this.plateLogService.getPlateLogs().subscribe(
      (data: any[]) => {
        this.plate_logs = data.map(plate => new PlateLogs(
          plate.name,
          plate.pulseOnLength,
          plate.HarvardAparatus,
          plate.Channel,
          plate.cycleLength,
          plate.plateName,
          plate.stimFreq,
          plate.timeSampling,
          new Date(plate.stimulation_start),
          new Date(plate.stimulation_end),
          plate.pharmacological,
          new Date(plate.Report_time1),
          plate.voltage1,
          plate.pulseDuration1,
          plate.frequency1,
          plate.current1,
          plate.chargeDifference1,
          plate.rms1,
          new Date(plate.Report_time2),
          plate.voltage2,
          plate.pulseDuration2,
          plate.frequency2,
          plate.current2,
          plate.chargeDifference2,
          plate.rms2,
        ));
        console.log('Data Recieved:', this.plate_logs);
        this.refreshMaturation();
      },
      error => console.error('Fetch failed:', error)
    );
  }

  getUniqueHarvardApparatus() {
    const harvardSet = new Set(this.plate_logs.map(log => log.HarvardAparatus.toString()));
    return Array.from(harvardSet);
  }  
}
