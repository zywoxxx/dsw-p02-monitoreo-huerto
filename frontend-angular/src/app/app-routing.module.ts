import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AccesoComponent } from './acceso/acceso.component';
import { sesionGuard } from './core/sesion.guard';
import { LecturasComponent } from './lecturas/lecturas.component';

// Rutas del esqueleto. Alertas y anotaciones se agregan en el siguiente incremento (estan en el contrato).
const routes: Routes = [
  { path: 'acceso', component: AccesoComponent },
  { path: 'lecturas', component: LecturasComponent, canActivate: [sesionGuard] },
  { path: '', pathMatch: 'full', redirectTo: 'lecturas' },
  { path: '**', redirectTo: 'lecturas' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}
