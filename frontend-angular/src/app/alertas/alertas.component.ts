import { Component, OnInit } from '@angular/core';
import { ApiService } from '../core/api.service';
import { Alerta, ErrorApi, PaginaAlertas } from '../core/modelos';
import { SesionService } from '../core/sesion.service';

/**
 * Alertas generadas por lecturas fuera de umbral. Todos los roles las consultan; solo el responsable
 * las marca como atendidas o las reabre. El rol y el instante de atencion los pone la API, no el cliente.
 */
@Component({
  selector: 'app-alertas',
  templateUrl: './alertas.component.html'
})
export class AlertasComponent implements OnInit {
  pagina: PaginaAlertas = { contenido: [], pagina: 0, tamano: 10, total: 0 };

  filtroNivel = '';
  filtroAtendida = '';      // '' todas, 'false' pendientes, 'true' atendidas
  cargando = false;
  enviando = false;
  exito = '';
  error: ErrorApi | null = null;

  constructor(private api: ApiService, public sesion: SesionService) {}

  ngOnInit(): void {
    this.cargar(0);
  }

  get totalPaginas(): number {
    return Math.max(1, Math.ceil(this.pagina.total / this.pagina.tamano));
  }

  cargar(numero: number): void {
    this.cargando = true;
    this.api.alertas({
      nivel: this.filtroNivel,
      atendida: this.filtroAtendida === '' ? undefined : this.filtroAtendida === 'true',
      pagina: numero,
      tamano: this.pagina.tamano
    }).subscribe({
      next: (p) => {
        this.pagina = p;
        this.cargando = false;
      },
      error: (e) => {
        this.cargando = false;
        this.error = ApiService.comoError(e);
      }
    });
  }

  cambiar(alerta: Alerta, atendida: boolean): void {
    this.exito = '';
    this.error = null;
    this.enviando = true;
    this.api.cambiarAtencion(alerta.id, atendida).subscribe({
      next: (a: Alerta) => {
        this.enviando = false;
        this.exito = a.atendida ? `Alerta #${a.id} marcada como atendida.` : `Alerta #${a.id} reabierta.`;
        this.cargar(this.pagina.pagina);
      },
      error: (e) => {
        this.enviando = false;
        this.error = ApiService.comoError(e);
      }
    });
  }
}
