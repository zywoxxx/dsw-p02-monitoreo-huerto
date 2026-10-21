# P05 - Catalogo de endpoints y contratos (completo)

La definicion formal es `docs/p04/openapi.yaml`, version 0.5.0 (OpenAPI 3.0.3). Este documento la resume para
leerla sin herramientas. Los ejemplos de respuesta estan copiados de `evidencia/txt/pruebas_api.txt`, es decir, son
respuestas reales de la API en la verificacion final; solo se recortaron los tokens.

Base en desarrollo: `http://localhost:8081`. Todos los cuerpos son `application/json` en UTF-8.

## 1. Resumen de las 13 operaciones

| # | Metodo y ruta | Para que | Quien | Exito | Errores | Desde |
|---|---|---|---|---|---|---|
| 1 | `GET /api/health` | Saber si la API llega a PostgreSQL | publico | 200 | 503 | P04 |
| 2 | `POST /api/auth/login` | Cambiar credenciales por un token | publico | 200 | 400, 401 | P04 |
| 3 | `GET /api/zonas` | Zonas del huerto | los 3 roles | 200 | 401 | **P05** |
| 4 | `GET /api/sensores` | Catalogo de sensores con rango y umbral | los 3 roles | 200 | 400, 401 | P04 |
| 5 | `GET /api/lecturas` | Historial paginado y filtrado | los 3 roles | 200 | 400, 401 | P04 |
| 6 | `GET /api/lecturas/{id}` | Una lectura | los 3 roles | 200 | 401, 404 | P04 |
| 7 | `POST /api/lecturas` | Registrar una lectura manual | OBSERVADOR | 201 | 400, 401, 403, 404, 409, 422, 503 | P04 |
| 8 | `GET /api/alertas` | Alertas paginadas con filtros | los 3 roles | 200 | 400, 401 | **P05** |
| 9 | `GET /api/alertas/{id}` | Una alerta | los 3 roles | 200 | 401, 404 | **P05** |
| 10 | `PATCH /api/alertas/{id}` | **Cambio de estado**: atender o reabrir | RESPONSABLE | 200 | 400, 401, 403, 404, 409, 503 | **P05** |
| 11 | `GET /api/anotaciones` | Anotaciones paginadas, opcionalmente por zona | los 3 roles | 200 | 400, 401 | **P05** |
| 12 | `GET /api/anotaciones/{id}` | Una anotacion | los 3 roles | 200 | 401, 404 | **P05** |
| 13 | `POST /api/anotaciones` | Registrar una anotacion firmada con el rol | los 3 roles | 201 | 400, 401, 404, 422, 503 | **P05** |

Las operaciones 1, 2 y 4 a 7 no cambiaron desde P04; su detalle esta en `docs/p04/endpoints.md`.

## 2. Reglas comunes

**Autenticacion.** Salvo las rutas 1 y 2, toda peticion lleva `Authorization: Bearer <token>`. Sin token, con la
firma alterada o caducado, la respuesta es 401 con la cabecera `WWW-Authenticate: Bearer`.

**Cuerpo de error.** Todos los errores tienen la misma forma `{codigo, mensaje, errores?, instante}`:

| Estado | `codigo` | Cuando |
|---|---|---|
| 400 | `VALIDACION` | JSON mal formado, campo obligatorio ausente, tipo incorrecto, texto demasiado corto o largo, parametro de consulta invalido |
| 401 | `NO_AUTENTICADO` | Falta el token, no es valido o caduco; credenciales incorrectas en el login |
| 403 | `ROL_SIN_PERMISO` | El rol del token no puede hacer la operacion |
| 404 | `NO_ENCONTRADO` | El recurso pedido o referido no existe |
| 405 | `METODO_NO_PERMITIDO` | La ruta existe pero no con ese metodo |
| 409 | `CONFLICTO` | El recurso existe pero su estado no admite la operacion (sensor inactivo; alerta ya en el estado pedido) |
| 422 | `REGLA_DE_NEGOCIO` | Datos bien formados que violan una regla del dominio (valor fuera del rango fisico; lectura de otra zona) |
| 500 | `ERROR_INTERNO` | Fallo no previsto; sin detalles tecnicos |
| 503 | `BASE_NO_DISPONIBLE` | PostgreSQL no responde |

**Paginacion.** `pagina` empieza en 0; `tamano` va de 1 a 100 (10 si no se indica). La respuesta es
`{ contenido, pagina, tamano, total }`, siempre de lo mas reciente a lo mas antiguo.

## 3. Contratos nuevos en P05

### 3.1 GET /api/zonas

Entrada: nada. Salida 200: lista de `Zona` ordenada por nombre.

```json
[ { "id": 1, "nombre": "Cama A", "cultivo": "Jitomate", "ubicacion": "Huerto escolar demo - patio norte (ficticio)" },
  { "id": 2, "nombre": "Invernadero 1", "cultivo": "Lechuga", "ubicacion": "Huerto escolar demo - invernadero (ficticio)" } ]
```

### 3.2 GET /api/alertas

| Parametro de consulta | Tipo | Efecto |
|---|---|---|
| `nivel` | `BAJA` o `ALTA` | filtra por nivel; otro valor responde 400 |
| `atendida` | booleano | `false` solo pendientes, `true` solo atendidas; otro valor responde 400 |
| `zonaId` | entero | alertas de los sensores de esa zona |
| `pagina`, `tamano` | enteros | paginacion |

Salida 200: `PaginaAlertas`. Cada `Alerta` trae la lectura que la genero (valor y unidad), el sensor, la variable,
la zona y su estado. `atendidaEn` y `atendidaPor` solo aparecen cuando `atendida` es `true`.

```json
{ "contenido": [
    { "id": 49, "lecturaId": 110, "sensorCodigo": "SEN-A-TEMP-01", "variable": "Temperatura ambiente", "zonaId": 1, "zona": "Cama A",
      "valor": 10.00, "unidad": "C", "nivel": "BAJA", "mensaje": "Temperatura ambiente en Cama A: 10 C por debajo del minimo 15.00 C.",
      "atendida": false, "creadaEn": "2026-10-21T15:58:20.988347Z" },
    { "id": 48, "lecturaId": 109, "sensorCodigo": "SEN-A-TEMP-01", "variable": "Temperatura ambiente", "zonaId": 1, "zona": "Cama A",
      "valor": 38.00, "unidad": "C", "nivel": "ALTA", "mensaje": "Temperatura ambiente en Cama A: 38 C por encima del maximo 32.00 C.",
      "atendida": false, "creadaEn": "2026-10-21T15:58:19.952580Z" } ],
  "pagina": 0, "tamano": 5, "total": 49 }
```

### 3.3 GET /api/alertas/{id}

Salida 200: una `Alerta`. Si no existe, 404 `NO_ENCONTRADO` "La alerta 999999 no existe.".

### 3.4 PATCH /api/alertas/{id} (cambio de estado)

Solo el rol RESPONSABLE.

| Campo de entrada | Tipo | Obligatorio | Regla |
|---|---|---|---|
| `atendida` | booleano | si | `true` marca como atendida; `false` reabre |

No se aceptan `atendidaEn` ni `atendidaPor`: los pone el servidor con el instante actual y el rol del token.

Entrada y salida reales (la alerta la genero la lectura de 38 C del caso anterior):

```json
> PATCH /api/alertas/48   Authorization: Bearer <token de responsable>
  {"atendida": true}
< 200 OK
  {"id":48,"lecturaId":109,"sensorCodigo":"SEN-A-TEMP-01","variable":"Temperatura ambiente","zonaId":1,"zona":"Cama A",
   "valor":38.00,"unidad":"C","nivel":"ALTA","mensaje":"Temperatura ambiente en Cama A: 38 C por encima del maximo 32.00 C.",
   "atendida":true,"atendidaEn":"2026-10-21T15:58:32.434558Z","atendidaPor":"RESPONSABLE","creadaEn":"2026-10-21T15:58:19.95258Z"}

> PATCH /api/alertas/48   {"atendida": true}        (otra vez)
< 409 Conflict   {"codigo":"CONFLICTO","mensaje":"La alerta 48 ya estaba atendida.", ...}

> PATCH /api/alertas/48   {"atendida": false}       (reabrir)
< 200 OK   {"id":48, ..., "atendida":false, "creadaEn":"2026-10-21T15:58:19.95258Z"}    (sin atendidaEn ni atendidaPor)
```

| Entrada | Respuesta | Cambio en la base |
|---|---|---|
| `{"atendida": true}` sobre una pendiente, token de RESPONSABLE | 200 con `atendida: true`, `atendidaEn`, `atendidaPor: "RESPONSABLE"` | `atendida = true`, `atendida_en = now()`, `atendida_por = 'RESPONSABLE'` |
| `{"atendida": true}` otra vez | 409 `CONFLICTO`, "La alerta N ya estaba atendida." | ninguno |
| `{"atendida": false}` sobre una atendida | 200 con `atendida: false`, sin `atendidaEn` ni `atendidaPor` | las dos columnas vuelven a `NULL` |
| `{}` | 400 `VALIDACION`, campo `atendida` | ninguno |
| `{"atendida": "si"}` | 400 `VALIDACION` | ninguno |
| id inexistente | 404 `NO_ENCONTRADO` | ninguno |
| token de OBSERVADOR o COORDINACION | 403 `ROL_SIN_PERMISO` | ninguno |
| sin token | 401 `NO_AUTENTICADO` | ninguno |
| PostgreSQL detenido | 503 `BASE_NO_DISPONIBLE` | ninguno |

### 3.5 GET /api/anotaciones

| Parametro de consulta | Tipo | Efecto |
|---|---|---|
| `zonaId` | entero | anotaciones de esa zona; `abc` responde 400 |
| `pagina`, `tamano` | enteros | paginacion |

Salida 200: `PaginaAnotaciones`.

```json
{ "contenido": [
    { "id": 41, "zonaId": 1, "zona": "Cama A", "lecturaId": 101, "autorRol": "OBSERVADOR",
      "texto": "[prueba] P05 anotacion sobre una lectura", "creadaEn": "2026-10-21T15:52:23.732758Z" },
    { "id": 40, "zonaId": 1, "zona": "Cama A", "autorRol": "COORDINACION",
      "texto": "[prueba] P05 anotacion de coordinacion", "creadaEn": "2026-10-21T15:52:23.325422Z" } ],
  "pagina": 0, "tamano": 5, "total": 41 }
```

`lecturaId` solo aparece cuando la anotacion refiere a una lectura.

### 3.6 GET /api/anotaciones/{id}

Salida 200: una `Anotacion`. Si no existe, 404.

### 3.7 POST /api/anotaciones

Los tres roles.

| Campo de entrada | Tipo | Obligatorio | Regla |
|---|---|---|---|
| `zonaId` | entero | si | debe existir |
| `lecturaId` | entero | no | si viene, debe existir y pertenecer a un sensor de esa zona |
| `texto` | texto | si | se recorta; de 3 a 300 caracteres |

No se acepta `autorRol`: la anotacion se firma con el rol del token.

Entrada y salida reales:

```json
> POST /api/anotaciones   Authorization: Bearer <token de coordinacion>
  {"zonaId": 1, "texto": "[prueba] P05 anotacion de coordinacion"}
< 201 Created   Location: /api/anotaciones/42
  {"id":42,"zonaId":1,"zona":"Cama A","autorRol":"COORDINACION","texto":"[prueba] P05 anotacion de coordinacion","creadaEn":"2026-10-21T15:58:34.792856Z"}

> POST /api/anotaciones   {"zonaId": 2, "lecturaId": 108, "texto": "[prueba] P05 lectura de otra zona"}
< 422 Unprocessable Entity
  {"codigo":"REGLA_DE_NEGOCIO","mensaje":"La lectura 108 pertenece a Cama A, no a Invernadero 1.","instante":"2026-10-21T09:58:39.4764171-06:00"}
```

| Entrada | Respuesta | Cambio en la base |
|---|---|---|
| zona 1, texto valido, token de COORDINACION | 201, `Location: /api/anotaciones/N`, `autorRol: "COORDINACION"` | +1 anotacion |
| zona 1, `lecturaId` de una lectura de esa zona, token de OBSERVADOR | 201 con `lecturaId` y `autorRol: "OBSERVADOR"` | +1 anotacion |
| texto `"ok"` | 400 `VALIDACION`, "La anotacion debe tener al menos 3 caracteres." | ninguno |
| texto de 301 caracteres | 400 `VALIDACION`, "La anotacion no puede exceder 300 caracteres." | ninguno |
| texto `"   ab   "` (2 tras recortar) | 400 `VALIDACION` | ninguno |
| sin `zonaId` o sin `texto` | 400 `VALIDACION` con el campo | ninguno |
| `lecturaId` -3 | 400 `VALIDACION` | ninguno |
| `zonaId` 999 | 404 `NO_ENCONTRADO`, "La zona 999 no existe." | ninguno |
| `lecturaId` 999999 | 404 `NO_ENCONTRADO`, "La lectura 999999 no existe." | ninguno |
| zona 2 con una lectura de la zona 1 | 422 `REGLA_DE_NEGOCIO`, "La lectura N pertenece a Cama A, no a Invernadero 1." | ninguno |
| sin token | 401 | ninguno |

## 4. Permisos por rol

| Operacion | OBSERVADOR | RESPONSABLE | COORDINACION |
|---|---|---|---|
| Consultar zonas, sensores, lecturas, alertas, anotaciones | si | si | si |
| Registrar lectura | si | no (403) | no (403) |
| Atender o reabrir una alerta | no (403) | si | no (403) |
| Registrar anotacion | si | si | si |

Sale del acta (seccion de roles). La unica decision nueva es quien atiende alertas; esta justificada en
`arquitectura.md`, D12.

## 5. Contrato escrito y contrato generado

springdoc publica en `/v3/api-docs` lo que deduce del codigo y la interfaz en `/swagger-ui.html`. La ultima prueba de
`scripts/pruebas_api.py` compara rutas y metodos: todo lo implementado esta en `openapi.yaml` y, desde P05, no queda
ninguna operacion del contrato sin implementar. El documento generado queda en `evidencia/txt/openapi_generado.json`.
