// src/app/app.component.ts
import { Component, OnInit, Injectable } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';
import { PlateLogs } from './shared/Plate_logs';
import { SeedingFormComponent } from './seeding-form/seeding-form.component';
import { FilterDropdownComponent } from './filter-dropdown-component/filter-dropdown-component.component';
import { provideHttpClient} from '@angular/common/http';  // Import HttpClient and provideHttpClient
import { HttpClientModule } from '@angular/common/http';
import { PlateLogService } from './shared/plate-log.service';  // Import the service
import { FormsModule } from '@angular/forms'; // Import FormsModule

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, CommonModule, SeedingFormComponent, FilterDropdownComponent, FormsModule, HttpClientModule],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  providers: []
})

export class AppComponent implements OnInit {
  title = 'homes';
  plate_logs: PlateLogs[] = [];
  showForm = false;
  showFilterDropdown = false;
  selectedPlate: PlateLogs | null = null;
  selectedIndex: number | null = null;
  editMode = false;
  applyChangesMode = false; // New flag for apply changes mode
  selectedHarvardAparatus: number | null = null; // Harvard Aparatus to apply changes to

  newPulseOnLength: number | null = null;
  newCycleLength: number | null = null;
  newTimeSampling: number | null = null;
  newStimFreq: number | null = null;
  newStimulationStart: string | null = null;
  newStimulationEnd: string | null = null;
  newPharmacological: boolean | null = null;

  filters = {
    harvardAparatus: ['all']
  };

  constructor(private plateLogService: PlateLogService) { }

  ngOnInit() {
    // will take out loadplates once we get the 
    // backend functionality
    //this.loadPlates();
    // this.refreshMaturation();
    // this.uploadPlates() 
    this.fetchPlates() 
  }

  toggleForm() {
    this.showForm = !this.showForm;
  }

  toggleFilterDropdown() {
    this.showFilterDropdown = !this.showFilterDropdown;
  }

  onFilterChange(selectedFilters: string[]) {
    this.filters.harvardAparatus = selectedFilters;
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
  cancelForm() {
    this.showForm = false;
    this.selectedPlate = null;
    this.selectedIndex = null;
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
  
  toggleApplyChanges() {
    this.applyChangesMode = !this.applyChangesMode;
    if (this.applyChangesMode) {
      // Reset the selected Harvard Aparatus and the new values
      this.selectedHarvardAparatus = null;
      this.newPulseOnLength = null;
      this.newCycleLength = null;
      this.newTimeSampling = null;
      this.newStimFreq = null;
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
          if (this.newStimulationStart !== null) plate.stimulation_start = new Date(this.newStimulationStart);
          if (this.newStimulationEnd !== null) plate.stimulation_end = new Date(this.newStimulationEnd);
          if (this.newPharmacological !== null) plate.pharmacological = this.newPharmacological;
  
          console.log('Updated plate:', plate);
        }
      });
  
      console.log('Updated Plate Logs:', this.plate_logs);
      this.savePlates(); // Save the updated plates
      this.applyChangesMode = false; // Exit apply changes mode
    }
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
