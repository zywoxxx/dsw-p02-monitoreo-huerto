import { Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ApiService } from '../core/api.service';
import { SesionService } from '../core/sesion.service';

@Component({
  selector: 'app-acceso',
  templateUrl: './acceso.component.html'
})
export class AccesoComponent {
  usuario = '';
  contrasena = '';
  enviando = false;
  error = '';
  expirada = this.ruta.snapshot.queryParamMap.get('expirada') === '1';

  constructor(private api: ApiService, private sesion: SesionService, private router: Router, private ruta: ActivatedRoute) {}

  entrar(): void {
    this.error = '';
    if (!this.usuario.trim() || !this.contrasena) {
      this.error = 'Escribe tu usuario y tu contrasena.';
      return;
    }
    this.enviando = true;
    this.api.login(this.usuario, this.contrasena).subscribe({
      next: (s) => {
        this.sesion.abrir(s);
        this.contrasena = '';
        this.router.navigate(['/lecturas']);
      },
      error: (e) => {
        this.enviando = false;
        this.contrasena = '';
        this.error = ApiService.comoError(e).mensaje;
      }
    });
  }
}
