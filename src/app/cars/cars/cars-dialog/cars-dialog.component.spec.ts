import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CarsDialogComponent } from './cars-dialog.component';

describe('CarsDialogComponent', () => {
  let component: CarsDialogComponent;
  let fixture: ComponentFixture<CarsDialogComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [CarsDialogComponent]
    });
    fixture = TestBed.createComponent(CarsDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
