import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AccesoComponent } from './acceso/acceso.component';
import { AlertasComponent } from './alertas/alertas.component';
import { AnotacionesComponent } from './anotaciones/anotaciones.component';
import { sesionGuard } from './core/sesion.guard';
import { LecturasComponent } from './lecturas/lecturas.component';

// Rutas del cliente: todas las vistas del flujo exigen sesion vigente; la API vuelve a exigir el token.
const routes: Routes = [
  { path: 'acceso', component: AccesoComponent },
  { path: 'lecturas', component: LecturasComponent, canActivate: [sesionGuard] },
  { path: 'alertas', component: AlertasComponent, canActivate: [sesionGuard] },
  { path: 'anotaciones', component: AnotacionesComponent, canActivate: [sesionGuard] },
  { path: '', pathMatch: 'full', redirectTo: 'lecturas' },
  { path: '**', redirectTo: 'lecturas' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}
