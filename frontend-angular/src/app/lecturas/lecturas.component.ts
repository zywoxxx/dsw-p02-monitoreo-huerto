import { Component, OnInit } from '@angular/core';
import { ApiService } from '../core/api.service';
import { ErrorApi, Lectura, PaginaLecturas, Sensor } from '../core/modelos';
import { SesionService } from '../core/sesion.service';

/**
 * Flujo principal en el cliente: elegir sensor, capturar valor, enviar y ver el historial.
 * La validacion con autoridad es la de la API; aqui solo se evita enviar el formulario vacio
 * y se muestran tal cual los errores que devuelve el servidor.
 */
@Component({
  selector: 'app-lecturas',
  templateUrl: './lecturas.component.html'
})
export class LecturasComponent implements OnInit {
  sensores: Sensor[] = [];
  pagina: PaginaLecturas = { contenido: [], pagina: 0, tamano: 10, total: 0 };

  sensorId: number | null = null;
  valor = '';
  observacion = '';

  filtroOrigen = '';
  cargando = false;
  enviando = false;
  exito = '';
  alerta = '';
  error: ErrorApi | null = null;

  constructor(private api: ApiService, public sesion: SesionService) {}

  ngOnInit(): void {
    this.api.sensores().subscribe({
      next: (s) => (this.sensores = s),
      error: (e) => (this.error = ApiService.comoError(e))
    });
    this.cargar(0);
  }

  get sensorElegido(): Sensor | undefined {
    return this.sensores.find((s) => s.id === Number(this.sensorId));
  }

  get totalPaginas(): number {
    return Math.max(1, Math.ceil(this.pagina.total / this.pagina.tamano));
  }

  cargar(numero: number): void {
    this.cargando = true;
    this.api.lecturas({ origen: this.filtroOrigen, pagina: numero, tamano: this.pagina.tamano }).subscribe({
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
    this.alerta = '';
    this.error = null;
    const texto = this.valor.trim().replace(',', '.');
    const esNumero = texto !== '' && !Number.isNaN(Number(texto));
    this.enviando = true;
    this.api.registrarLectura({
      sensorId: this.sensorId === null ? null : Number(this.sensorId),
      valor: texto === '' ? null : esNumero ? Number(texto) : texto,
      observacion: this.observacion.trim() || undefined
    }).subscribe({
      next: (l: Lectura) => {
        this.enviando = false;
        this.exito = `Lectura #${l.id} registrada: ${l.valor} ${l.unidad}, procedencia ${l.origen}.`;
        this.alerta = l.alerta ? `Alerta ${l.alerta.nivel}: ${l.alerta.mensaje}` : '';
        this.valor = '';            // solo se limpia cuando la API confirmo el alta (201)
        this.observacion = '';
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
