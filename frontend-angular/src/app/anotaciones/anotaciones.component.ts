import { Component, OnInit } from '@angular/core';
import { ApiService } from '../core/api.service';
import { Anotacion, ErrorApi, PaginaAnotaciones, Zona } from '../core/modelos';
import { SesionService } from '../core/sesion.service';

/**
 * Anotaciones libres sobre una zona (y opcionalmente sobre una lectura). Los tres roles anotan;
 * la API firma con el rol del token. Las reglas de largo y pertenencia las aplica la API; aqui
 * solo se muestra un contador y se presentan tal cual los errores del servidor.
 */
@Component({
  selector: 'app-anotaciones',
  templateUrl: './anotaciones.component.html'
})
export class AnotacionesComponent implements OnInit {
  readonly maximoTexto = 300;

  zonas: Zona[] = [];
  pagina: PaginaAnotaciones = { contenido: [], pagina: 0, tamano: 10, total: 0 };

  zonaId: number | null = null;
  lecturaId = '';
  texto = '';

  filtroZona: number | null = null;
  cargando = false;
  enviando = false;
  exito = '';
  error: ErrorApi | null = null;

  constructor(private api: ApiService, public sesion: SesionService) {}

  ngOnInit(): void {
    this.api.zonas().subscribe({
      next: (z) => (this.zonas = z),
      error: (e) => (this.error = ApiService.comoError(e))
    });
    this.cargar(0);
  }

  get totalPaginas(): number {
    return Math.max(1, Math.ceil(this.pagina.total / this.pagina.tamano));
  }

  cargar(numero: number): void {
    this.cargando = true;
    this.api.anotaciones({ zonaId: this.filtroZona, pagina: numero, tamano: this.pagina.tamano }).subscribe({
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

  registrar(): void {
    this.exito = '';
    this.error = null;
    const lectura = this.lecturaId.trim();
    const esNumero = lectura !== '' && !Number.isNaN(Number(lectura));
    this.enviando = true;
    this.api.registrarAnotacion({
      zonaId: this.zonaId === null ? null : Number(this.zonaId),
      lecturaId: lectura === '' ? undefined : esNumero ? Number(lectura) : lectura,
      texto: this.texto
    }).subscribe({
      next: (a: Anotacion) => {
        this.enviando = false;
        this.exito = `Anotacion #${a.id} registrada en ${a.zona}.`;
        this.texto = '';            // solo se limpia cuando la API confirmo el alta (201); la zona se conserva
        this.lecturaId = '';
        this.cargar(0);
      },
      error: (e) => {
        this.enviando = false;      // se conserva lo capturado para corregir
        this.error = ApiService.comoError(e);
      }
    });
  }

  errorDe(campo: string): string {
    return this.error?.errores?.find((x) => x.campo === campo)?.mensaje ?? '';
  }
}
