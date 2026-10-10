import { HttpClient, HttpErrorResponse, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ErrorApi, Lectura, NuevaLectura, PaginaLecturas, Sensor, Sesion } from './modelos';

/**
 * Unico punto del cliente que conoce las rutas de la API. La base es relativa (/api): en desarrollo
 * la resuelve proxy.conf.json hacia http://localhost:8081 y en produccion el servidor que publique el cliente.
 */
@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly base = '/api';

  constructor(private http: HttpClient) {}

  login(usuario: string, contrasena: string): Observable<Sesion> {
    return this.http.post<Sesion>(`${this.base}/auth/login`, { usuario, contrasena });
  }

  sensores(soloActivos = true): Observable<Sensor[]> {
    return this.http.get<Sensor[]>(`${this.base}/sensores`, { params: new HttpParams().set('activo', soloActivos) });
  }

  lecturas(filtros: { sensorId?: number; zonaId?: number; origen?: string; pagina?: number; tamano?: number }): Observable<PaginaLecturas> {
    let params = new HttpParams();
    Object.entries(filtros).forEach(([clave, valor]) => {
      if (valor !== undefined && valor !== null && valor !== '') {
        params = params.set(clave, String(valor));
      }
    });
    return this.http.get<PaginaLecturas>(`${this.base}/lecturas`, { params });
  }

  registrarLectura(nueva: NuevaLectura): Observable<Lectura> {
    return this.http.post<Lectura>(`${this.base}/lecturas`, nueva);
  }

  /** Convierte cualquier fallo HTTP en el esquema Error del contrato para mostrarlo igual en todas las vistas. */
  static comoError(e: unknown): ErrorApi {
    if (e instanceof HttpErrorResponse) {
      if (e.error && typeof e.error === 'object' && 'mensaje' in e.error) {
        return e.error as ErrorApi;
      }
      if (e.status === 0) {
        return { codigo: 'SIN_CONEXION', mensaje: 'No hay conexion con la API. Verifica que el backend este en marcha.' };
      }
      return { codigo: 'HTTP_' + e.status, mensaje: 'La API respondio ' + e.status + '.' };
    }
    return { codigo: 'DESCONOCIDO', mensaje: 'Ocurrio un error inesperado.' };
  }
}
