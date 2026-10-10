// Tipos del contrato de la API (docs/p04/openapi.yaml). Si el contrato cambia, se cambia aqui.

export type Rol = 'RESPONSABLE' | 'OBSERVADOR' | 'COORDINACION';

export interface Sesion {
  token: string;
  usuario: string;
  rol: Rol;
  expiraEn: string;
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
  nivel: 'BAJA' | 'ALTA';
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
