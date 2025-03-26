import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MaterialModule } from './material.module';
import { ToolbarComponent } from './components/toolbar/toolbar.component';
import { RouterModule } from '@angular/router';
import { LimitCharactersPipe } from './pipes/limit-characters.pipe';
import { TransformDatePipe } from './pipes/transform-date.pipe';
import { ParseHtmlPipe } from './pipes/parse-html.pipe';

@NgModule({
  declarations: [
    ToolbarComponent,
    LimitCharactersPipe,
    TransformDatePipe,
    ParseHtmlPipe
  ],
  exports: [
    ToolbarComponent,
    LimitCharactersPipe,
    TransformDatePipe,
    ParseHtmlPipe
  ],
  imports: [
    CommonModule,
    MaterialModule,
    RouterModule
  ]
})
export class SharedModule { }
