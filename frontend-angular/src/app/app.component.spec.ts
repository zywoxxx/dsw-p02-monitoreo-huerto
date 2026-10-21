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

  it('solo el responsable puede atender alertas; los tres roles anotan', () => {
    const sesion = TestBed.inject(SesionService);
    const futuro = new Date(Date.now() + 60000).toISOString();
    expect(sesion.puedeAnotar).toBeFalse();
    sesion.abrir({ token: 't', usuario: 'observador', rol: 'OBSERVADOR', expiraEn: futuro });
    expect(sesion.puedeAtenderAlertas).toBeFalse();
    expect(sesion.puedeAnotar).toBeTrue();
    sesion.abrir({ token: 't', usuario: 'coordinacion', rol: 'COORDINACION', expiraEn: futuro });
    expect(sesion.puedeAtenderAlertas).toBeFalse();
    sesion.abrir({ token: 't', usuario: 'responsable', rol: 'RESPONSABLE', expiraEn: futuro });
    expect(sesion.puedeAtenderAlertas).toBeTrue();
    expect(sesion.puedeAnotar).toBeTrue();
  });

  it('PATCH /api/alertas/7 envia {atendida: true}', () => {
    const api = TestBed.inject(ApiService);
    const http = TestBed.inject(HttpTestingController);
    api.cambiarAtencion(7, true).subscribe();
    const peticion = http.expectOne('/api/alertas/7');
    expect(peticion.request.method).toBe('PATCH');
    expect(peticion.request.body).toEqual({ atendida: true });
    peticion.flush({ id: 7, atendida: true });
    http.verify();
  });

  it('POST /api/anotaciones envia el cuerpo del contrato', () => {
    const api = TestBed.inject(ApiService);
    const http = TestBed.inject(HttpTestingController);
    api.registrarAnotacion({ zonaId: 1, lecturaId: 12, texto: 'Se revisa el sensor.' }).subscribe();
    const peticion = http.expectOne('/api/anotaciones');
    expect(peticion.request.method).toBe('POST');
    expect(peticion.request.body).toEqual({ zonaId: 1, lecturaId: 12, texto: 'Se revisa el sensor.' });
    peticion.flush({ id: 5 });
    http.verify();
  });

  it('GET /api/alertas con atendida=false manda el parametro y omite los filtros vacios', () => {
    const api = TestBed.inject(ApiService);
    const http = TestBed.inject(HttpTestingController);
    api.alertas({ nivel: '', atendida: false, pagina: 0, tamano: 10 }).subscribe();
    const peticion = http.expectOne((r) => r.url === '/api/alertas');
    expect(peticion.request.method).toBe('GET');
    expect(peticion.request.params.get('atendida')).toBe('false');
    expect(peticion.request.params.has('nivel')).toBeFalse();
    expect(peticion.request.params.get('pagina')).toBe('0');
    peticion.flush({ contenido: [], pagina: 0, tamano: 10, total: 0 });
    http.verify();
  });

  it('traduce el error de la API al esquema del contrato', () => {
    const e = ApiService.comoError({ nada: true });
    expect(e.codigo).toBe('DESCONOCIDO');
  });
});
