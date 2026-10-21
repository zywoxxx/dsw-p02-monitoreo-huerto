// Tipos del contrato de la API (docs/p04/openapi.yaml). Si el contrato cambia, se cambia aqui.

export type Rol = 'RESPONSABLE' | 'OBSERVADOR' | 'COORDINACION';

export type Nivel = 'BAJA' | 'ALTA';

export interface Sesion {
  token: string;
  usuario: string;
  rol: Rol;
  expiraEn: string;
}

export interface Zona {
  id: number;
  nombre: string;
  cultivo?: string;
  ubicacion: string;
}

export interface Sensor {
  id: number;
  codigo: string;
  activo: boolean;
  zonaId: number;
  zona: string;
  variable: string;
  unidad: string;
  rangoFisicoMinimo: number;
  rangoFisicoMaximo: number;
  umbralMinimo?: number;
  umbralMaximo?: number;
}

export interface AlertaResumen {
  nivel: Nivel;
  mensaje: string;
}

export interface Lectura {
  id: number;
  sensorId: number;
  sensorCodigo: string;
  variable: string;
  zona: string;
  valor: number;
  unidad: string;
  origen: 'manual' | 'simulado';
  observacion?: string;
  registradoEn: string;
  alerta?: AlertaResumen;
}

export interface PaginaLecturas {
  contenido: Lectura[];
  pagina: number;
  tamano: number;
  total: number;
}

export interface NuevaLectura {
  sensorId: number | null;
  // numero cuando lo capturado es numerico; el texto tal cual cuando no, para que la API responda 400
  valor: number | string | null;
  observacion?: string;
}

export interface Alerta {
  id: number;
  lecturaId: number;
  sensorCodigo: string;
  variable: string;
  zonaId: number;
  zona: string;
  valor: number;
  unidad: string;
  nivel: Nivel;
  mensaje: string;
  atendida: boolean;
  // presentes solo cuando atendida es true; los pone el servidor, nunca el cliente
  atendidaEn?: string;
  atendidaPor?: Rol;
  creadaEn: string;
}

export interface PaginaAlertas {
  contenido: Alerta[];
  pagina: number;
  tamano: number;
  total: number;
}

export interface CambioAtencion {
  atendida: boolean;
}

export interface NuevaAnotacion {
  zonaId: number | null;
  // numero cuando lo capturado es numerico; el texto tal cual cuando no, para que la API responda 400
  lecturaId?: number | string;
  texto: string;
}

export interface Anotacion {
  id: number;
  zonaId: number;
  zona: string;
  lecturaId?: number;
  autorRol: Rol;
  texto: string;
  creadaEn: string;
}

export interface PaginaAnotaciones {
  contenido: Anotacion[];
  pagina: number;
  tamano: number;
  total: number;
}

export interface ErrorCampo {
  campo: string;
  mensaje: string;
}

export interface ErrorApi {
  codigo: string;
  mensaje: string;
  errores?: ErrorCampo[];
  instante?: string;
}
