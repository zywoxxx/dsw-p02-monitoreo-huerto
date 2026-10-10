import { Injectable } from '@angular/core';
import { Rol, Sesion } from './modelos';

const CLAVE = 'huerto.sesion';

/**
 * Guarda la sesion (token y rol) del lado del cliente. Se usa sessionStorage: se borra al cerrar la
 * pestana y no viaja sola en las peticiones, asi que el token solo sale en la cabecera Authorization.
 */
@Injectable({ providedIn: 'root' })
export class SesionService {
  private actual: Sesion | null = this.leer();

  get sesion(): Sesion | null {
    if (this.actual && new Date(this.actual.expiraEn).getTime() <= Date.now()) {
      this.cerrar();
    }
    return this.actual;
  }

  get autenticado(): boolean {
    return this.sesion !== null;
  }

  get token(): string | null {
    return this.sesion?.token ?? null;
  }

  get rol(): Rol | null {
    return this.sesion?.rol ?? null;
  }

  // Misma regla que Permisos.java: solo el observador registra lecturas. La API vuelve a comprobarlo.
  get puedeRegistrarLecturas(): boolean {
    return this.rol === 'OBSERVADOR';
  }

  abrir(sesion: Sesion): void {
    this.actual = sesion;
    sessionStorage.setItem(CLAVE, JSON.stringify(sesion));
  }

  cerrar(): void {
    this.actual = null;
    sessionStorage.removeItem(CLAVE);
  }

  private leer(): Sesion | null {
    try {
      const texto = sessionStorage.getItem(CLAVE);
      return texto ? (JSON.parse(texto) as Sesion) : null;
    } catch {
      return null;
    }
  }
}
