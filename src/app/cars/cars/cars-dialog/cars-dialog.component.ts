import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';

@Component({
  selector: 'app-cars-dialog',
  templateUrl: './cars-dialog.component.html',
  styleUrls: ['./cars-dialog.component.scss']
})
export class CarsDialogComponent {
  constructor(
    public dialogRef: MatDialogRef<CarsDialogComponent>,
    @Inject(MAT_DIALOG_DATA)
    public data: {
      type: string;
      info: any;
    }
  ){}

  public onNoClick(): void {
    this.dialogRef.close();
  }
}
