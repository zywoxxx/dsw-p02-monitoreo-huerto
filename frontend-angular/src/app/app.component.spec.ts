import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { AppComponent } from './app.component';
import { ApiService } from './core/api.service';
import { SesionService } from './core/sesion.service';

describe('Cliente Angular del PR09', () => {
  beforeEach(() => {
    sessionStorage.clear();
    TestBed.configureTestingModule({
      imports: [RouterTestingModule, HttpClientTestingModule],
      declarations: [AppComponent]
    });
  });

  it('crea el componente raiz sin sesion', () => {
    const fixture = TestBed.createComponent(AppComponent);
    expect(fixture.componentInstance.sesion.autenticado).toBeFalse();
  });

  it('solo el observador puede registrar lecturas', () => {
    const sesion = TestBed.inject(SesionService);
    const futuro = new Date(Date.now() + 60000).toISOString();
    sesion.abrir({ token: 't', usuario: 'coordinacion', rol: 'COORDINACION', expiraEn: futuro });
    expect(sesion.puedeRegistrarLecturas).toBeFalse();
    sesion.abrir({ token: 't', usuario: 'observador', rol: 'OBSERVADOR', expiraEn: futuro });
    expect(sesion.puedeRegistrarLecturas).toBeTrue();
  });

  it('una sesion caducada se descarta', () => {
    const sesion = TestBed.inject(SesionService);
    sesion.abrir({ token: 't', usuario: 'observador', rol: 'OBSERVADOR', expiraEn: new Date(Date.now() - 1000).toISOString() });
    expect(sesion.autenticado).toBeFalse();
  });

  it('POST /api/lecturas envia el cuerpo del contrato', () => {
    const api = TestBed.inject(ApiService);
    const http = TestBed.inject(HttpTestingController);
    api.registrarLectura({ sensorId: 2, valor: 25.5, observacion: 'prueba' }).subscribe();
    const peticion = http.expectOne('/api/lecturas');
    expect(peticion.request.method).toBe('POST');
    expect(peticion.request.body).toEqual({ sensorId: 2, valor: 25.5, observacion: 'prueba' });
    peticion.flush({ id: 1 });
    http.verify();
  });

  it('traduce el error de la API al esquema del contrato', () => {
    const e = ApiService.comoError({ nada: true });
    expect(e.codigo).toBe('DESCONOCIDO');
  });
});
