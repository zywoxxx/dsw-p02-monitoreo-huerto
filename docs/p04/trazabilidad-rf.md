# P04 - Trazabilidad RF -> componente

Los requisitos son los de la ficha PR09 (C11) y el acta del proyecto; no se agrego ninguno. Por cada uno se indica
que pieza del cliente, de la API y de la base lo atiende, con que operacion del contrato y como se comprobo.

Estados: **VERIFICADO** (se ejecuto y hay evidencia), **NO_VERIFICADO** (existe pero no se probo),
**PENDIENTE** (definido en el contrato, sin codigo todavia).

## 1. Requisitos funcionales

| RF | Requisito | Operacion del contrato | Cliente Angular | API Spring Boot | PostgreSQL | Prueba | Estado |
|---|---|---|---|---|---|---|---|
| RF01 | Zonas | `GET /api/zonas`; la zona tambien viaja dentro de `Sensor` y `Lectura` | columna Zona en `LecturasComponent` | `SensorRepository`, `LecturaRepository` (join con `zona`) | `zona` | contrato 07 y 09 | Zona dentro de sensores y lecturas: VERIFICADO. Recurso `/api/zonas`: PENDIENTE |
| RF02 | Variables con unidad y rango fisico | `GET /api/sensores` | `LecturasComponent` (ficha del sensor elegido) | `SensorController`, `SensorRepository` | `variable` | contrato 07; navegador 03 | VERIFICADO |
| RF03 | Registrar lecturas con instante, valor y procedencia | `POST /api/lecturas` | `LecturasComponent.registrar()`, `ApiService.registrarLectura()` | `LecturaController`, `LecturaService`, `ReglasLectura`, `LecturaRepository.insertarLectura` | `lectura` | contrato 12, 17 a 26; navegador 04, 06, 07; `ReglasLecturaTest`, `LecturaControllerTest` | VERIFICADO |
| RF04 | Umbrales por sensor | `GET /api/sensores` (campos `umbralMinimo`, `umbralMaximo`) | ficha del sensor | `SensorRepository` (LEFT JOIN `umbral`), `ReglasLectura.nivelAlerta` | `umbral` | contrato 07 y 16; `ReglasLecturaTest` | VERIFICADO |
| RF05 | Historial | `GET /api/lecturas`, `GET /api/lecturas/{id}` | tabla, filtro y paginador de `LecturasComponent` | `LecturaController`, `LecturaService.listar`, `LecturaRepository.buscar/contar` | `lectura` e indice por instante | contrato 09, 10, 11, 13, 28; navegador 08 | VERIFICADO |
| RF06a | Alerta automatica | `POST /api/lecturas` (objeto `alerta` en la respuesta); `GET /api/alertas` | aviso y etiqueta en el historial | `LecturaService` (transaccion), `LecturaRepository.insertarAlerta` | `alerta` | contrato 14, 15, 16; navegador 05 | Generacion y consulta dentro de la lectura: VERIFICADO. Listado `/api/alertas`: PENDIENTE |
| RF06b | Anotaciones por rol | `GET` y `POST /api/anotaciones` | - | - | `anotacion` (ya existe) | - | PENDIENTE (solo contrato) |
| RF07 | Modelo relacionado | todas | - | repositorios | 7 tablas con FK, UNIQUE y CHECK | `sql/03_consultas_verificacion.sql` antes y despues | VERIFICADO |
| RF08 | API Web 3.0 | `openapi.yaml` completo | `ApiService`, `TokenInterceptor` | toda la carpeta `api-spring/` | - | `verify-module.sh M04` | VERIFICADO para 6 de 10 operaciones; 4 PENDIENTE |
| RF09 | Fuente IoT simulada (Web 4.0) | filtro `origen=simulado` en `GET /api/lecturas` | filtro de procedencia | `LecturaRepository.buscar` | `lectura.origen` | contrato 10; navegador 08 | Consulta: VERIFICADO. El simulador no es parte de P04 |

## 2. Requisitos no funcionales y criterios de aceptacion

| Id | Requisito | Componentes | Prueba | Estado |
|---|---|---|---|---|
| RNF01 | Ruta de salud | `HealthController` | contrato 01; `txt/10_health.txt`; `scripts/prueba_base_detenida.sh` | VERIFICADO (200 y, con la base detenida, 503: `txt/14_base_detenida.txt`) |
| RNF02 | Autorizacion por rol en operaciones de cambio | `TokenFilter`, `Permisos`, `UsuarioAutenticado`, `sesionGuard` | contrato 05, 06, 26, 27; navegador 01, 10, 11; `TokenServiceTest` | VERIFICADO |
| CA01 | Flujo principal con cambio persistido | cliente + API + base | navegador 04 y 05 (conteo en PostgreSQL) | VERIFICADO |
| CA02 | El caso invalido se rechaza sin alterar datos | `ReglasLectura`, `ApiExceptionHandler`, `LecturasComponent` | contrato 17 a 25; navegador 06 y 07 | VERIFICADO |
| CA03 | La API responde 2xx y 4xx segun el contrato | `openapi.yaml`, controladores | contrato 01 a 30 (cuerpos validados contra los esquemas) | VERIFICADO |
| CA04 | Evento IoT simulado | - | - | NO APLICA en P04 |
| CA05 | Otra persona puede preparar, ejecutar y limpiar con el README | README, `verify-module.sh`, `cleanup.sh` | - | VERIFICADO en un equipo; PENDIENTE por otro integrante |

## 3. De componente a requisito

Sirve para revisar que no haya piezas sin motivo.

| Componente | Atiende |
|---|---|
| `AccesoComponent`, `SesionService`, `TokenInterceptor`, `sesionGuard` | RNF02 |
| `LecturasComponent` | RF02, RF03, RF04, RF05, RF06a, RF09 |
| `ApiService`, `modelos.ts` | RF08 |
| `TokenFilter`, `TokenService`, `CredencialesService`, `AuthController`, `Permisos`, `UsuarioAutenticado` | RNF02 |
| `SensorController`, `SensorRepository` | RF01, RF02, RF04 |
| `LecturaController`, `LecturaService`, `LecturaRepository` | RF03, RF05, RF06a, RF09 |
| `ReglasLectura` | RF03, RF04, RF06a, CA02 |
| `ApiExceptionHandler`, `ApiError`, `ApiException` | CA02, CA03 |
| `HealthController` | RNF01 |
| `WebConfig` | RF08 (CORS, metadatos OpenAPI) |
| `sql/01_schema.sql` | RF07 |

## 4. Continuidad con P02 y P03

| Aspecto | P02 (JSP/Servlet) | P03 (JSF/PrimeFaces) | P04 (Angular + API) |
|---|---|---|---|
| Donde se arma la pantalla | servidor (JSP) | servidor (Facelets) | navegador (Angular) |
| Que viaja por la red | HTML y formularios | HTML y respuestas parciales AJAX | JSON |
| Reglas de la lectura | `LecturaValidator` | el mismo `LecturaValidator` | `ReglasLectura` (mismas reglas, nuevos codigos de estado) |
| Rechazo de un valor invalido | 400 con la pagina | mensaje en la vista | 400 o 422 con cuerpo `Error` |
| Identidad | no habia | sesion en servidor con cookie | token firmado en cabecera |
| Persistencia | JDBC directo | JDBC directo | Spring JDBC |
| Base y modelo | 7 tablas | sin cambios | sin cambios |
| Roles | 3 (solo en `anotacion.autor_rol`) | 3, con permisos | 3, los mismos permisos |
