import { Component, Output, Input, OnChanges, SimpleChanges, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-filter-dropdown',
  standalone: true,
  templateUrl : './filter-dropdown-component.component.html',
  styleUrls: ['./filter-dropdown-component.component.css']
})
export class FilterDropdownComponent implements OnChanges {
  @Output() filterChange = new EventEmitter<string[]>();
  @Input() currentFilters : string[] = []

  //It should set this to be a string with the current filters instead
  selectedFilters: string[] = this.currentFilters;

  ngOnChanges(changes : SimpleChanges) {
    this.selectedFilters = this.currentFilters;
  }

  onFilterChange(event: Event) {
    console.log(this.currentFilters)
    const inputElement = event.target as HTMLInputElement;
    const value = inputElement.value;
    const checked = inputElement.checked;

    if (value === 'all' && checked) {
      this.selectedFilters = ['all'];
    } else if (checked) {
      this.selectedFilters = this.selectedFilters.filter(f => f !== 'all');
      this.selectedFilters.push(value);
    } else {
      this.selectedFilters = this.selectedFilters.filter(f => f !== value);
    }

    if (this.selectedFilters.length === 0) {
      this.selectedFilters = ['all'];
    }

    this.filterChange.emit(this.selectedFilters);
  }
}
