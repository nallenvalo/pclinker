import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ConfigTableComponent } from './config-table.component';

describe('ConfigTableComponent', () => {
  let component: ConfigTableComponent;
  let fixture: ComponentFixture<ConfigTableComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ConfigTableComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ConfigTableComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
