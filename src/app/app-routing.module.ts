import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomeComponent } from './home/home.component';

const routes: Routes = [
  {
    path: '', pathMatch: 'full',
    component: HomeComponent
  },
  {
    path: 'cars',
    loadChildren: () =>
      import('./cars/cars.module').then(
        (m) => m.CarsModule
      )
  },
  { path: '**', redirectTo: '' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
