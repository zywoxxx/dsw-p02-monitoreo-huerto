# P04 - Catalogo de endpoints y contratos

La definicion formal es `docs/p04/openapi.yaml` (OpenAPI 3.0.3, version 0.4.0). Este documento lo resume para
leerlo sin herramientas. Los ejemplos de respuesta estan copiados de `evidencia/txt/pruebas_api.txt`, es decir, son
respuestas reales de la API; solo se recorto el token.

Base en desarrollo: `http://localhost:8081`. Todos los cuerpos son `application/json` en UTF-8.

## 1. Resumen

| # | Metodo y ruta | Para que | Quien | Exito | Errores | Estado |
|---|---|---|---|---|---|---|
| 1 | `GET /api/health` | Saber si la API llega a PostgreSQL | publico | 200 | 503 | IMPLEMENTADO |
| 2 | `POST /api/auth/login` | Cambiar credenciales por un token | publico | 200 | 400, 401 | IMPLEMENTADO |
| 3 | `GET /api/sensores` | Catalogo de sensores con rango y umbral | los 3 roles | 200 | 400, 401 | IMPLEMENTADO |
| 4 | `GET /api/lecturas` | Historial paginado y filtrado | los 3 roles | 200 | 400, 401 | IMPLEMENTADO |
| 5 | `GET /api/lecturas/{id}` | Una lectura | los 3 roles | 200 | 401, 404 | IMPLEMENTADO |
| 6 | `POST /api/lecturas` | Registrar una lectura manual | OBSERVADOR | 201 | 400, 401, 403, 404, 409, 422, 503 | IMPLEMENTADO |
| 7 | `GET /api/zonas` | Zonas del huerto | los 3 roles | 200 | 401 | SOLO CONTRATO |
| 8 | `GET /api/alertas` | Alertas generadas | los 3 roles | 200 | 400, 401 | SOLO CONTRATO |
| 9 | `GET /api/anotaciones` | Anotaciones recientes | los 3 roles | 200 | 401 | SOLO CONTRATO |
| 10 | `POST /api/anotaciones` | Registrar una anotacion | los 3 roles | 201 | 400, 401, 404 | SOLO CONTRATO |

"SOLO CONTRATO" quiere decir que la entrada y la salida ya estan acordadas en `openapi.yaml`, pero todavia no hay
codigo; hoy esas rutas responden 404. Se implementan en el siguiente incremento.

## 2. Reglas comunes

**Autenticacion.** Salvo las rutas 1 y 2, toda peticion lleva `Authorization: Bearer <token>`. Sin token, con la
firma alterada o caducado, la respuesta es 401 con la cabecera `WWW-Authenticate: Bearer`.

**Cuerpo de error.** Todos los errores tienen la misma forma:

```json
{
  "codigo": "VALIDACION",
  "mensaje": "La peticion tiene datos invalidos; no se guardo nada.",
  "errores": [ { "campo": "valor", "mensaje": "El valor admite como maximo 2 decimales; no se redondea." } ],
  "instante": "2026-09-29T12:27:52.5797281-06:00"
}
```

`errores` solo aparece cuando el problema es de campos concretos.

| Estado | `codigo` | Cuando |
|---|---|---|
| 400 | `VALIDACION` | JSON mal formado, campo obligatorio ausente, tipo incorrecto, mas de dos decimales, texto demasiado largo, parametro de consulta invalido |
| 401 | `NO_AUTENTICADO` | Falta el token, no es valido o caduco; credenciales incorrectas en el login |
| 403 | `ROL_SIN_PERMISO` | El rol del token no puede hacer la operacion |
| 404 | `NO_ENCONTRADO` | El recurso pedido o referido no existe |
| 405 | `METODO_NO_PERMITIDO` | La ruta existe pero no con ese metodo |
| 409 | `CONFLICTO` | El recurso existe pero su estado no admite la operacion (sensor inactivo) |
| 422 | `REGLA_DE_NEGOCIO` | Los datos estan bien formados pero violan una regla del dominio (rango fisico) |
| 500 | `ERROR_INTERNO` | Fallo no previsto; el cuerpo no incluye detalles tecnicos |
| 503 | `BASE_NO_DISPONIBLE` | PostgreSQL no responde |

**Paginacion.** `pagina` empieza en 0; `tamano` va de 1 a 100 (10 si no se indica). La respuesta es
`{ contenido, pagina, tamano, total }`.

## 3. Contratos

### 3.1 GET /api/health

Entrada: nada. Salida 200:

```json
{ "app": "huerto-api PR09 (P04 Spring Boot)", "status": "UP", "db": "UP", "postgres": "PostgreSQL 16.15", "lecturas": 7 }
```

Salida 503: `{ "app": "...", "status": "DOWN", "db": "DOWN", "error": "PostgreSQL no responde" }`.

### 3.2 POST /api/auth/login

| Campo de entrada | Tipo | Obligatorio | Regla |
|---|---|---|---|
| `usuario` | texto | si | 1 a 40 caracteres |
| `contrasena` | texto | si | 1 a 100 caracteres |

Salida 200:

```json
{ "token": "eyJhbGciOiJI...", "tipo": "Bearer", "usuario": "observador", "rol": "OBSERVADOR", "expiraEn": "2026-09-29T12:57:49.5102079-06:00" }
```

| Caso | Respuesta |
|---|---|
| Falta usuario o contrasena | 400 `VALIDACION` con el campo que falta |
| Usuario desconocido o contrasena incorrecta | 401 `NO_AUTENTICADO`, "Usuario o contrasena incorrectos." (el mismo mensaje en ambos casos) |

### 3.3 GET /api/sensores

| Parametro de consulta | Tipo | Obligatorio | Efecto |
|---|---|---|---|
| `zonaId` | entero | no | solo sensores de esa zona |
| `activo` | booleano | no | `true` solo activos, `false` solo inactivos |

Salida 200: lista de `Sensor`, ordenada por zona y codigo.

```json
[ { "id": 2, "codigo": "SEN-A-TEMP-01", "activo": true, "zonaId": 1, "zona": "Cama A",
    "variable": "Temperatura ambiente", "unidad": "C",
    "rangoFisicoMinimo": -10.00, "rangoFisicoMaximo": 60.00, "umbralMinimo": 15.00, "umbralMaximo": 32.00 } ]
```

`umbralMinimo` y `umbralMaximo` no aparecen si el sensor no tiene umbral. `zonaId=abc` responde 400.

### 3.4 GET /api/lecturas

| Parametro de consulta | Tipo | Efecto |
|---|---|---|
| `sensorId` | entero | lecturas de ese sensor |
| `zonaId` | entero | lecturas de los sensores de esa zona |
| `origen` | `manual` o `simulado` | filtra por procedencia; otro valor responde 400 |
| `pagina`, `tamano` | enteros | paginacion |

Salida 200: `PaginaLecturas`, de la mas reciente a la mas antigua.

```json
{ "contenido": [ { "id": 63, "sensorId": 2, "sensorCodigo": "SEN-A-TEMP-01", "variable": "Temperatura ambiente",
                   "zona": "Cama A", "valor": 38.00, "unidad": "C", "origen": "manual",
                   "observacion": "[prueba] P04 alerta alta", "registradoEn": "2026-09-29T18:27:51.164095Z",
                   "alerta": { "nivel": "ALTA", "mensaje": "Temperatura ambiente en Cama A: 38 C por encima del maximo 32.00 C." } } ],
  "pagina": 0, "tamano": 10, "total": 17 }
```

### 3.5 GET /api/lecturas/{id}

Entrada: `id` en la ruta. Salida 200: una `Lectura`. Si no existe, 404 `NO_ENCONTRADO`.

### 3.6 POST /api/lecturas

Solo el rol OBSERVADOR.

| Campo de entrada | Tipo | Obligatorio | Regla |
|---|---|---|---|
| `sensorId` | entero | si | debe existir y estar activo |
| `valor` | numero | si | maximo 2 decimales; dentro del rango fisico de la variable |
| `observacion` | texto | no | hasta 200 caracteres |

No se aceptan `origen` ni `registradoEn`: la API escribe `manual` y PostgreSQL pone el instante.

Entrada:

```json
{ "sensorId": 2, "valor": 25.5, "observacion": "[prueba] P04 lectura valida" }
```

Salida 201, con la cabecera `Location: /api/lecturas/62`:

```json
{ "id": 62, "sensorId": 2, "sensorCodigo": "SEN-A-TEMP-01", "variable": "Temperatura ambiente", "zona": "Cama A",
  "valor": 25.50, "unidad": "C", "origen": "manual", "observacion": "[prueba] P04 lectura valida",
  "registradoEn": "2026-09-29T18:27:50.587461Z" }
```

Si el valor sale del umbral operativo, la respuesta tambien es 201 y trae el objeto `alerta`. Los limites del umbral
cuentan como dentro: para SEN-A-TEMP-01, 15 y 32 no generan alerta.

| Entrada | Respuesta | Cambio en la base |
|---|---|---|
| `valor: 25.5` | 201 sin `alerta` | +1 lectura |
| `valor: 38` | 201 con `alerta.nivel = ALTA` | +1 lectura, +1 alerta |
| `valor: 10` | 201 con `alerta.nivel = BAJA` | +1 lectura, +1 alerta |
| `valor: 15` o `32` | 201 sin `alerta` | +1 lectura |
| `valor: "abc"` | 400 `VALIDACION` | ninguno |
| `valor: 24.555` | 400 `VALIDACION`, "maximo 2 decimales; no se redondea" | ninguno |
| sin `valor` o sin `sensorId` | 400 `VALIDACION` | ninguno |
| JSON mal formado | 400 `VALIDACION` | ninguno |
| `observacion` de 201 caracteres | 400 `VALIDACION` | ninguno |
| `valor: 150` | 422 `REGLA_DE_NEGOCIO`, "fuera del rango fisico de Temperatura ambiente [-10.00, 60.00]" | ninguno |
| `sensorId: 999` | 404 `NO_ENCONTRADO` | ninguno |
| sensor inactivo | 409 `CONFLICTO` | ninguno |
| sin token | 401 `NO_AUTENTICADO` | ninguno |
| token de COORDINACION o RESPONSABLE | 403 `ROL_SIN_PERMISO` | ninguno |

### 3.7 a 3.10 Recursos definidos solo en el contrato

| Ruta | Entrada | Salida |
|---|---|---|
| `GET /api/zonas` | nada | lista de `Zona` `{id, nombre, cultivo, ubicacion}` |
| `GET /api/alertas` | `nivel` (`BAJA`, `ALTA`), `pagina`, `tamano` | `PaginaAlertas`; cada `Alerta` trae `{id, lecturaId, sensorCodigo, zona, valor, unidad, nivel, mensaje, atendida, creadaEn}` |
| `GET /api/anotaciones` | `zonaId` opcional | lista de `Anotacion` `{id, zonaId, zona, lecturaId, autorRol, texto, creadaEn}` |
| `POST /api/anotaciones` | `{zonaId, lecturaId (opcional), texto}` con texto de 3 a 300 caracteres | 201 con la `Anotacion`; 400 si el texto no cumple; 404 si la zona o la lectura no existen. `autorRol` sale del token. |

## 4. Permisos por rol

| Operacion | OBSERVADOR | RESPONSABLE | COORDINACION |
|---|---|---|---|
| Consultar sensores, lecturas, zonas, alertas, anotaciones | si | si | si |
| Registrar lectura | si | no (403) | no (403) |
| Registrar anotacion | si | si | si |

La tabla sale del acta del proyecto (seccion de roles) y es la misma que se aplico en P03.

## 5. Contrato escrito y contrato generado

springdoc publica en `/v3/api-docs` el OpenAPI que deduce del codigo, y la interfaz en `/swagger-ui.html`. No es
el contrato de referencia porque solo conoce lo implementado y nombra los esquemas segun las clases Java
(`LecturaRequest` en lugar de `NuevaLectura`, `PaginaLectura` en lugar de `PaginaLecturas`). Sirve como
comprobacion: `scripts/pruebas_api.py` (caso 30) revisa que toda operacion que exista en el codigo este en
`openapi.yaml`, y que lo que falte en el codigo sea solo lo marcado como pendiente. El documento generado queda en
`evidencia/txt/openapi_generado.json`.
