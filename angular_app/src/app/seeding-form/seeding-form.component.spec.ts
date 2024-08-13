import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SeedingFormComponent } from './seeding-form.component';

describe('SeedingFormComponent', () => {
  let component: SeedingFormComponent;
  let fixture: ComponentFixture<SeedingFormComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SeedingFormComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SeedingFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
