import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { SesionService } from './core/sesion.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html'
})
export class AppComponent {
  constructor(public sesion: SesionService, private router: Router) {}

  salir(): void {
    this.sesion.cerrar();
    this.router.navigate(['/acceso']);
  }
}
