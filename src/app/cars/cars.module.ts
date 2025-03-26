import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CarsComponent } from './cars/cars.component';
import { CarsRoutingModule } from './cars-routing.module';
import {LayoutModule} from '@angular/cdk/layout';
import { MaterialModule } from '../shared/material.module';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { SharedModule } from '../shared/shared.module';
import {ScrollingModule} from '@angular/cdk/scrolling';
import { FormsModule } from '@angular/forms';
import { CarsDialogComponent } from './cars/cars-dialog/cars-dialog.component';

@NgModule({
  declarations: [
    CarsComponent,
    CarsDialogComponent
  ],
  imports: [
    CommonModule,
    CarsRoutingModule,
    SharedModule,
    LayoutModule,
    MaterialModule,
    ScrollingModule,
    FormsModule
  ]
})
export class CarsModule { }
