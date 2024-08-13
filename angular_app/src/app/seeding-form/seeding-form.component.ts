// src/app/seeding-form/seeding-form.component.ts
import { Component, EventEmitter, Input, Output, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { PlateLogs } from '../shared/Plate_logs';
// import {getUniqueHarvardApparatus()} from 'app.component.ts'

@Component({
  selector: 'app-seeding-form',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './seeding-form.component.html',
  styleUrls: ['./seeding-form.component.css']
})
export class SeedingFormComponent implements OnChanges {
  num : number = 6;
  platformCode = '';
  cellLine = ''; // Cell line
  name = ''; // User name
  pulseOnLength: number = 1;
  HarvardAparatus!: number;
  Channel!: number;
  cycleLength: number = 10;
  stimFreq: number = 10;
  timeSampling: number = 3600;
  stimulationStart!: string;
  stimulationEnd!: string;
  pharmacological: boolean = false;
  Report_time1 !: string;
  voltage1 !: number;
  pulseDuration1 !: number;
  frequency1 !: number;
  current1 !: number;
  chargeDifference1 !: number;
  energy1 !: number;
  rms1 !: number;
  Report_time2 !: string;
  voltage2 !: number;
  pulseDuration2 !: number;
  frequency2 !: number;
  current2 !: number;
  chargeDifference2!: number;
  energy2 !: number;
  rms2 !: number;

  errorMessage: string | null = null;
  showDynamicForms = false;
  newPlates: PlateLogs[] = [];
  currentPlateIndex = 0;

  @Input() plate: PlateLogs | null = null;
  @Input() selectedIndex: number | null = null;
  @Input() existingPlates: PlateLogs[] = []; // Add this input to get existing plates
  @Output() addSeeding = new EventEmitter<{index: number | null, plate: PlateLogs}>();
  @Output() allAdded = new EventEmitter<void>(); // Add this output event
  @Output() cancelForm = new EventEmitter<void>();

  ngOnChanges(changes: SimpleChanges) {
    if (changes['plate'] && this.plate) {
      this.platformCode = this.plate.plateName;
      this.cellLine = this.plate.plateName; // Cell line
      this.name = this.plate.name;
      this.pulseOnLength = this.plate.pulseOnLength;
      this.HarvardAparatus = this.plate.HarvardAparatus;
      this.Channel = this.plate.Channel;
      this.cycleLength = this.plate.cycleLength;
      this.stimFreq = this.plate.stimFreq;
      this.timeSampling = this.plate.timeSampling;
      this.stimulationStart = this.plate.stimulation_start.toISOString()
      this.stimulationEnd = this.plate.stimulation_end.toISOString()
      this.pharmacological = this.plate.pharmacological;
      this.Report_time1 = this.plate.Report_time1.toISOString()
      this.voltage1 = this.plate.voltage1
      this.pulseDuration1 = this.plate.pulseDuration1;
      this.frequency1 = this.plate.frequency1;
      this.current1 = this.plate.current1;
      this.chargeDifference1 = this.plate.chargeDifference1;
      this.rms1 = this.plate.rms1;
      this.Report_time2 = this.plate.Report_time2.toISOString()
      this.voltage2 = this.plate.voltage2;
      this.pulseDuration2 = this.plate.pulseDuration2;
      this.frequency2 = this.plate.frequency2;
      this.current2 = this.plate.current2;
      this.chargeDifference2 = this.plate.chargeDifference2;
      this.rms2 = this.plate.rms2;
    }
  }
  
  validateForm(newPlate: PlateLogs): boolean {
    const currentDate = new Date();

    // Check for blank fields
    if (!newPlate.name || !newPlate.plateName || !newPlate.HarvardAparatus || !newPlate.Channel ||
      !newPlate.pulseOnLength || !newPlate.cycleLength || !newPlate.stimFreq ||
      !newPlate.timeSampling || !newPlate.stimulation_start || !newPlate.stimulation_end) {
    this.errorMessage = "All fields must be filled out.";
    return false;
    }
    
    // Check Harvard Aparatus value
    if (![1, 2, 3].includes(newPlate.HarvardAparatus)) {
      this.errorMessage = "Harvard Aparatus must be in range (1-3)";
      return false;
    }

    // Check Channel value
    if (![1, 2, 3, 4, 5, 6, 7, 8, 9].includes(newPlate.Channel)) {
      this.errorMessage = "Channels must be in range (1-9)";
      return false;
    }

    // Check if end date comes after start date
    if (newPlate.stimulation_end <= newPlate.stimulation_start) {
      this.errorMessage = "End date must come after start date";
      return false;
    }

    // Check for unique plate name
    for (const plate of this.existingPlates) {
      if (this.selectedIndex !== null && plate === this.existingPlates[this.selectedIndex]) {
        continue; // Skip the plate being edited
      }
      if (plate.plateName === newPlate.plateName) {
        this.errorMessage = "Plate name must be unique.";
        return false;
      }
    }

    for (const plate of this.existingPlates) {
      if (this.selectedIndex !== null && plate === this.existingPlates[this.selectedIndex]) {
        continue; // Skip the plate being edited
      }
      if (plate.HarvardAparatus === newPlate.HarvardAparatus &&
          plate.stimulation_start <= currentDate &&
          plate.stimulation_end >= currentDate) {
        if (plate.pulseOnLength !== newPlate.pulseOnLength ||
            plate.cycleLength !== newPlate.cycleLength ||
            plate.timeSampling !== newPlate.timeSampling ||
            plate.stimFreq !== newPlate.stimFreq) {
          this.errorMessage = "Parameters must be congruent for all plates plugged into the same Harvard Aparatus";
          return false;
        }
      }
    }
    // Check for unique Harvard Aparatus and Channel combination
    for (const plate of this.existingPlates) {
      if (this.selectedIndex !== null && plate === this.existingPlates[this.selectedIndex]) {
        continue; // Skip the plate being edited
      }
      if (plate.HarvardAparatus === newPlate.HarvardAparatus && plate.Channel === newPlate.Channel) {
        this.errorMessage = "No two plates can be stimulated via the same Harvard Aparatus and Channel.";
        return false;
      }
    }
    this.errorMessage = null;
    return true;
  }
  // I want to prompt the form
  // I want to ask for how many plates they are inputting
  // I want to ask for the harvard aparatus that is being configured 
  // I want to set the the unique parameters for that harvard aparatus 
  // I want to set a unique channel and name for each plate 
  synthesizedPlateName(index: number): string {
    const currentDate = new Date().toISOString().split('T')[0];
    return `${currentDate}-${this.cellLine}-${this.platformCode}-P${index + 1}`;
  }

  onSubmit(i: number) {
    const newPlate = this.newPlates[i];
    //newPlate.plateName = this.synthesizedPlateName(i);
    if (this.validateForm(newPlate)) {
      this.addSeeding.emit({ index: this.selectedIndex, plate: newPlate });
      if (this.currentPlateIndex < this.num - 1) {
        this.currentPlateIndex++;
      } else {
        this.allAdded.emit(); // Automatically emit the event
        //this.resetForm();
      }
    }
  }

  onGetnum() {
    const currentDate = this.getCurrentDateYYMMDD();
    //const currentDate = new Date().toISOString().split('T')[0]; // Get current date in YYYY-MM-DD format
    this.newPlates = Array(this.num).fill(null).map((_, i) => new PlateLogs(
      this.name, // User name
      this.pulseOnLength,
      this.HarvardAparatus,
      1, // Default value, will be updated per plate
      this.cycleLength,
      `${currentDate}-${this.cellLine}-${this.platformCode}-P${i + 1}`, // Synthesize the plate name
      this.stimFreq,
      this.timeSampling,
      new Date(this.stimulationStart),
      new Date(this.stimulationEnd),
      this.pharmacological,
      new Date(this.Report_time1),
      this.voltage1,
      this.pulseDuration1,
      this.frequency1,
      this.current1,
      this.chargeDifference1,
      this.rms1,
      new Date(this.Report_time2),
      this.voltage2,
      this.pulseDuration2,
      this.frequency2,
      this.current2,
      this.chargeDifference2,
      this.rms2
    ));
    this.showDynamicForms = true;
    this.currentPlateIndex = 0;
  }
    // create new plate logs for all the new plates and set the parameters 
    // some kind of form validation 
    getCurrentDateYYMMDD(): string {
      const date = new Date();
      const year = date.getFullYear().toString().slice(-2);
      const month = ('0' + (date.getMonth() + 1)).slice(-2);
      const day = ('0' + date.getDate()).slice(-2);
      return `${year}${month}${day}`;
    }

  onCancel() {
    this.cancelForm.emit();
    this.resetForm();
  }

  resetForm() {
    this.platformCode = '';
    this.name = ''; // Reset user name
    this.HarvardAparatus = 0;
    this.Channel = 0;
    this.pulseOnLength = 1;
    this.cycleLength = 10;
    this.stimFreq = 10;
    this.timeSampling = 3600;
    this.stimulationStart = '';
    this.stimulationEnd = '';
    this.pharmacological = false;
    this.Report_time1 = '';
    this.voltage1 = NaN;
    this.pulseDuration1 = NaN;
    this.frequency1 = NaN;
    this.current1 = NaN;
    this.chargeDifference1 = NaN;
    this.rms1 = NaN;
    this.Report_time2 = '';
    this.voltage2 = NaN;
    this.pulseDuration2 = NaN;
    this.frequency2 = NaN;
    this.current2 = NaN;
    this.chargeDifference2 = NaN;
    this.rms2 = NaN;
    this.showDynamicForms = false;
    this.newPlates = [];
    this.currentPlateIndex = 0;
  }
  getUniqueHarvardApparatus() {
    const harvardSet = new Set(this.existingPlates.map(log => log.HarvardAparatus.toString()));
    return Array.from(harvardSet);
  }
  possibleNums : Array<number> = [1,2,3,4,5,6,7]
  possibleChannels : Array<number> = [1,2,3,4,5,6,7,8]
  possibleHarvards : Array<number> = [1,2,3]
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
}
