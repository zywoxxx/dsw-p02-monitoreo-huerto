import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { SesionService } from './sesion.service';

/** Sin sesion vigente no se entra a las rutas del flujo; la API de todos modos exige el token. */
export const sesionGuard: CanActivateFn = () => {
  const sesion = inject(SesionService);
  const router = inject(Router);
  return sesion.autenticado ? true : router.createUrlTree(['/acceso']);
};
