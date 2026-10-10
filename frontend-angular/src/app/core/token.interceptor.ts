import { HttpErrorResponse, HttpEvent, HttpHandler, HttpInterceptor, HttpRequest } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { Observable, catchError, throwError } from 'rxjs';
import { SesionService } from './sesion.service';

/**
 * Agrega Authorization: Bearer a las llamadas a /api y, si la API responde 401 (token ausente,
 * invalido o caducado), cierra la sesion local y manda al acceso.
 */
@Injectable()
export class TokenInterceptor implements HttpInterceptor {
  constructor(private sesion: SesionService, private router: Router) {}

  intercept(req: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    const token = this.sesion.token;
    const esLogin = req.url.endsWith('/auth/login');
    const peticion = token && req.url.startsWith('/api') && !esLogin
      ? req.clone({ setHeaders: { Authorization: `Bearer ${token}` } })
      : req;
    return next.handle(peticion).pipe(
      catchError((e: HttpErrorResponse) => {
        if (e.status === 401 && !esLogin) {
          this.sesion.cerrar();
          this.router.navigate(['/acceso'], { queryParams: { expirada: 1 } });
        }
        return throwError(() => e);
      })
    );
  }
}
