# P05 - Trazabilidad: requisito -> componente -> prueba -> evidencia -> criterio R05

Los requisitos son los de la ficha PR09 (C11) y el acta; no se agrego ninguno. "Contrato NN" es el caso NN de
`scripts/pruebas_api.py` (`evidencia/txt/pruebas_api_resultados.txt`); "navegador NN" es el caso NN de
`scripts/recorrido_angular.py` (`evidencia/txt/recorrido_angular.txt`); "JUnit" son las pruebas de `api-spring/src/test`.

Estados: **VERIFICADO** (se ejecuto y hay evidencia), **NO_VERIFICADO** (existe pero no se probo), **PENDIENTE**.

## 1. Requisitos funcionales

| RF | Requisito | Operacion del contrato | Cliente Angular | API Spring Boot | PostgreSQL | Prueba | Estado |
|---|---|---|---|---|---|---|---|
| RF01 | Zonas | `GET /api/zonas` | `AnotacionesComponent` (select de zona y filtro) | `ZonaController`, `ZonaRepository` | `zona` | contrato 30, 31; navegador 17, 18 | VERIFICADO |
| RF02 | Variables con unidad y rango fisico | `GET /api/sensores` | ficha del sensor en `LecturasComponent` | `SensorController`, `SensorRepository` | `variable` | contrato 07; navegador 03 | VERIFICADO (sin cambios desde P04) |
| RF03 | Registrar lecturas | `POST /api/lecturas` | `LecturasComponent` | `LecturaController`, `LecturaService`, `ReglasLectura` | `lectura` | contrato 12, 17 a 26; navegador 04, 06, 07; JUnit | VERIFICADO (sin cambios desde P04) |
| RF04 | Umbrales | `GET /api/sensores` | ficha del sensor | `SensorRepository`, `ReglasLectura.nivelAlerta` | `umbral` | contrato 07, 16; JUnit | VERIFICADO |
| RF05 | Historial | `GET /api/lecturas`, `/{id}` | tabla, filtro y paginador de lecturas | `LecturaService.listar` | `lectura` | contrato 09 a 11, 13, 28; navegador 08 | VERIFICADO |
| RF06a | Alerta automatica y su consulta | `POST /api/lecturas` (objeto `alerta`); **`GET /api/alertas`, `GET /api/alertas/{id}`** | **`AlertasComponent`**: tabla, filtros por nivel y estado, paginador | `LecturaService` (genera); **`AlertaController`, `AlertaService`, `AlertaRepository`** (consulta) | `alerta` | contrato 14, 15, 32 a 38; navegador 05, 11, 19, 21 | VERIFICADO |
| RF06b | **Cambio de estado de la alerta** (atender / reabrir) | **`PATCH /api/alertas/{id}`** | botones "Marcar atendida" y "Reabrir" en `AlertasComponent`; `ApiService.cambiarAtencion` | `AlertaController` (permiso `ATENDER_ALERTA`), `AlertaService.cambiarAtencion` (`@Transactional`), `AlertaRepository.actualizarAtencion` | `alerta.atendida`, `atendida_en`, `atendida_por`; `ck_alerta_atencion` | contrato 39 a 47; navegador 12, 13, 19, 21; JUnit `AlertaControllerTest` | VERIFICADO |
| RF06c | Anotaciones por rol | **`GET /api/anotaciones`, `/{id}`, `POST /api/anotaciones`** | **`AnotacionesComponent`**: formulario con zona, lectura opcional y contador; lista con filtro por zona | `AnotacionController` (permiso `ANOTAR`), `AnotacionService`, `ReglasAnotacion`, `AnotacionRepository` | `anotacion` (`CHECK autor_rol`, texto >= 3, `VARCHAR(300)`) | contrato 48 a 63; navegador 14 a 18, 20; JUnit `ReglasAnotacionTest`, `AnotacionControllerTest` | VERIFICADO |
| RF07 | Modelo relacionado | todas | - | repositorios | 7 tablas; migracion `sql/04` | `03_consultas_verificacion.sql` antes y despues; paso "migracion" del verificador | VERIFICADO |
| RF08 | API Web 3.0 | las 13 operaciones de `openapi.yaml` 0.5.0 | `ApiService` (9 llamadas), `TokenInterceptor` | `api-spring/` completo | - | contrato 64 (todo lo implementado esta en el contrato y nada del contrato falta) | VERIFICADO: 13 de 13 |
| RF09 | Fuente IoT simulada (Web 4.0) | filtro `origen=simulado` | filtro de procedencia | `LecturaRepository` | `lectura.origen` | contrato 10; navegador 08 | consulta VERIFICADO; el simulador no es parte de P05 |

## 2. Requisitos no funcionales y criterios de aceptacion

| Id | Requisito | Componentes | Prueba | Estado |
|---|---|---|---|---|
| RNF01 | Ruta de salud (200 / 503) | `HealthController` | contrato 01; `scripts/prueba_base_detenida.sh` (`txt/14_base_detenida.txt`) | VERIFICADO |
| RNF02 | Autorizacion por rol en operaciones de cambio | `TokenFilter`, `Permisos`, `UsuarioAutenticado`; `sesionGuard` y `SesionService.puedeAtenderAlertas` | contrato 05, 06, 26, 27, 39, 40, 46, 63; navegador 01, 19, 21, 22 | VERIFICADO: los tres roles ejercidos contra la API |
| CA01 | Flujo principal con cambio persistido | cliente + API + base | navegador 04, 05, 12, 17 (conteo en PostgreSQL en cada paso) | VERIFICADO |
| CA02 | Lo invalido se rechaza sin alterar datos | `ReglasLectura`, `ReglasAnotacion`, `AlertaService`, `ApiExceptionHandler` | contrato 17 a 25, 39, 40, 42 a 46, 54 a 63; navegador 06, 07, 14, 15, 16 | VERIFICADO |
| CA03 | La API responde 2xx y 4xx segun el contrato | `openapi.yaml`, controladores | contrato 01 a 64 (cuerpos validados contra los esquemas) | VERIFICADO |
| CA04 | Evento IoT simulado | - | - | NO APLICA en P05 |
| CA05 | Otra persona puede preparar, ejecutar, probar y limpiar con el README | README, `verify-module.sh M05`, `demo_p05.sh`, `cleanup.sh` | - | VERIFICADO en un equipo; PENDIENTE por otro integrante |

## 3. Criterios de R05

| Criterio R05 | Pts | Que lo demuestra | Evidencia |
|---|---|---|---|
| API Spring funcional: endpoints y respuestas verificables | 3 | 13 operaciones implementadas, incluida salud, consulta y cambio de estado; cada respuesta validada contra el contrato | `txt/pruebas_api.txt` (peticion y respuesta real de cada caso), `txt/openapi_generado.json`, `img/22_swagger_ui.png` |
| Integracion Angular: consumo de servicios y flujo de usuario | 3 | el cliente consume las 9 llamadas de `ApiService` a traves del proxy; recorrido en navegador real con los tres roles | `txt/recorrido_angular.txt`, `img/01` a `img/22`, `txt/06_pruebas_frontend.txt` |
| Persistencia PostgreSQL: operaciones y estado reproducible | 2 | conteos antes y despues en cada caso; migracion idempotente; estado de la alerta comprobado en la base tras atender y reabrir | `txt/08_postgres_antes.txt`, `txt/08b_migracion_p05.txt`, `txt/12_postgres_despues.txt`, contrato 41, 47 |
| Errores y validacion: casos invalidos y respuestas controladas | 2 | 400, 401, 403, 404, 409, 422 y 503 con el mismo cuerpo `Error`; la base no cambia en ninguno | contrato 17 a 27, 34, 36, 38 a 40, 42 a 46, 49, 53 a 63; `txt/14_base_detenida.txt`; navegador 06, 07, 14 a 16 |
| Pruebas y repositorio: resultados, README y trazabilidad | 2 | JUnit, Karma, contrato y navegador en un solo comando; README reproducible; este documento | `txt/01_build_api.txt`, `txt/02_pruebas_api_unitarias.txt`, `txt/06_pruebas_frontend.txt`, `txt/13_resumen.txt`, `README.md`, `docs/bitacora.md` |

## 4. De componente a requisito

| Componente nuevo en P05 | Atiende |
|---|---|
| `ZonaController`, `ZonaRepository`, `Zona` | RF01 |
| `AlertaController`, `AlertaService`, `AlertaRepository`, `Alerta`, `CambioAtencionRequest` | RF06a, RF06b, RNF02, CA02 |
| `AnotacionController`, `AnotacionService`, `AnotacionRepository`, `ReglasAnotacion`, `Anotacion`, `AnotacionRequest` | RF06c, CA02 |
| `Permisos.ATENDER_ALERTA` | RNF02 |
| `sql/04_p05_atencion_alerta.sql`, cambio en `01_schema.sql` | RF06b, RF07 |
| `AlertasComponent` | RF06a, RF06b |
| `AnotacionesComponent` | RF01, RF06c |
| `ApiService.zonas/alertas/cambiarAtencion/anotaciones/registrarAnotacion`, `modelos.ts` | RF08 |
| `SesionService.puedeAtenderAlertas`, `puedeAnotar` | RNF02 (solo comodidad de vista; la API decide) |
| `scripts/verify-m05.sh`, `pruebas_api.py` (casos 30 a 64), `recorrido_angular.py` (casos 11 a 21), `prueba_base_detenida.sh`, `demo_p05.sh` | CA03, CA05 |

## 5. Continuidad P02 -> P03 -> P04 -> P05

| Aspecto | P02 | P03 | P04 | P05 |
|---|---|---|---|---|
| Zonas, alertas y anotaciones | JSP + servlets | vistas JSF | solo en el contrato | API + vistas Angular |
| Cambio de estado de una alerta | no existia | no existia | no existia | `PATCH /api/alertas/{id}` |
| Rol que firma la anotacion | campo del formulario | sesion del servidor | - | token |
| Base | 7 tablas | sin cambios | sin cambios | mismas 7 tablas; `alerta` con 2 columnas mas (migracion) |
| Roles ejercidos en las pruebas | 3 (en `autor_rol`) | 3 | OBSERVADOR y COORDINACION | los 3 (RESPONSABLE atiende alertas) |
