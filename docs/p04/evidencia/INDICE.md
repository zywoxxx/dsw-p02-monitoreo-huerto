# P04 - Indice de evidencia frente a R04

Producto de equipo DSW-E01: entrega en Eminus como `P04_EQUIPO_01`. La justificacion individual se entrega como
`P04_APELLIDO_NOMBRE`. La evidencia de texto y las capturas de esta carpeta las genera
`./scripts/verify-module.sh M04`; `txt/14_base_detenida.txt` lo genera `./scripts/prueba_base_detenida.sh`.
Las rutas locales, el nombre del equipo y el usuario del sistema se sustituyen por `<REPO>`, `<HOME>`, `<EQUIPO>` y
`<USUARIO>`. Los tokens se recortan y las contrasenas no se imprimen. La evidencia de P02 y P03 se conserva intacta.

Evidencias minimas de la guia: **Diagrama** (R04.1), **OpenAPI** (R04.4), **Modelo de datos** (R04.3),
**Justificacion individual** (R04.5).

## R04.1 Diagrama de arquitectura (3 pts)

| Evidencia | Que demuestra | Archivo | Estado |
|---|---|---|---|
| Diagrama de componentes | Tres capas, componentes de cada una, protocolo entre ellas, lo implementado y lo pendiente | `../diagramas/01_componentes.png` | VERIFICADO |
| Diagrama de secuencia | Flujo principal con el orden de las comprobaciones y sus salidas de error | `../diagramas/02_secuencia.png` | VERIFICADO |
| Diagrama de despliegue | Procesos, puertos, variables de entorno, proxy de desarrollo | `../diagramas/03_despliegue.png` | VERIFICADO |
| Responsabilidades por componente | Que hace y que no hace cada pieza | `../arquitectura.md`, secciones 1 a 3 | VERIFICADO |
| El diagrama corresponde al codigo | Clases dentro del jar; estructura de carpetas | `txt/03_jar_contenido.txt`, `api-spring/`, `frontend-angular/` | VERIFICADO |
| Generador de los diagramas | Se pueden regenerar | `scripts/diagramas_p04.py` | VERIFICADO |

## R04.2 Justificacion Angular / Spring Boot: decisiones y alternativas (2.5 pts)

| Evidencia | Que demuestra | Archivo | Estado |
|---|---|---|---|
| Tabla de decisiones D1 a D9 | Decision, alternativas revisadas, motivo y costo aceptado | `../arquitectura.md`, seccion 4 | VERIFICADO |
| Versiones usadas | Java 11, Spring Boot 2.7.18, Angular 16.2.12, Node 18.20.8 | `txt/00_versiones.txt`, `api-spring/pom.xml`, `frontend-angular/package.json` | VERIFICADO |
| Estructura compilable del backend | `mvn clean package` con 16 pruebas | `txt/01_build_api.txt`, `txt/02_pruebas_api_unitarias.txt` | VERIFICADO |
| Estructura compilable del frontend | `ng build` y 5 pruebas | `txt/05_build_frontend.txt`, `txt/06_pruebas_frontend.txt` | VERIFICADO |
| Seguridad basica | Token, roles, CORS, errores sin trazas, sin credenciales en el repositorio | `../arquitectura.md`, seccion 5; casos 05, 06, 26, 27 y 29 de `txt/pruebas_api.txt` | VERIFICADO |
| Continuidad con P02 y P03 | Que cambia y que se conserva | `../trazabilidad-rf.md`, seccion 4 | VERIFICADO |

## R04.3 Modelo PostgreSQL (2 pts)

| Evidencia | Que demuestra | Archivo | Estado |
|---|---|---|---|
| Modelo entidad-relacion | 7 tablas y sus relaciones | `../../evidencia/img/00_modelo_er.png` | VERIFICADO |
| Tablas, restricciones y relaciones | PK, FK, UNIQUE, CHECK | `../modelo-datos.md`, secciones 1 y 2; `sql/01_schema.sql` | VERIFICADO |
| De tabla a recurso de la API | Que columnas forman cada esquema del contrato | `../modelo-datos.md`, seccion 3 | VERIFICADO |
| Donde vive cada regla | API y base | `../modelo-datos.md`, seccion 4 | VERIFICADO |
| Estado de la base antes y despues | Tablas, conteos, lecturas creadas por la API con procedencia `manual` | `txt/08_postgres_antes.txt`, `txt/12_postgres_despues.txt` | VERIFICADO |
| Transaccion lectura + alerta | Con la base detenida no queda ninguna lectura a medias | `txt/14_base_detenida.txt` | VERIFICADO |

## R04.4 Endpoints y contratos (2.5 pts)

| Evidencia | Que demuestra | Archivo | Estado |
|---|---|---|---|
| Contrato OpenAPI | 10 operaciones, 16 esquemas, errores y seguridad | `../openapi.yaml` | VERIFICADO (valida como OpenAPI 3.0.3) |
| Validacion del contrato | Lista de operaciones y respuestas | `txt/07_openapi_validacion.txt` | VERIFICADO |
| Catalogo legible | Entrada, salida y errores de cada operacion, con ejemplos reales | `../endpoints.md` | VERIFICADO |
| Pruebas del contrato | 30 casos: 2xx, 400, 401, 403, 404, 409, 422, CORS | `txt/pruebas_api.txt`, `txt/pruebas_api_resultados.txt` | VERIFICADO |
| Base no disponible | 503 en salud, consulta y registro | `txt/14_base_detenida.txt` | VERIFICADO |
| OpenAPI generado desde el codigo | Lo implementado esta dentro del contrato | `txt/openapi_generado.json`, `img/11_swagger_ui.png` | VERIFICADO |
| El cliente consume el contrato | Acceso, captura valida, alerta, errores 400 y 422, filtro, rol sin permiso, token invalido | `txt/recorrido_angular.txt`, `img/01_acceso.png` a `img/10_token_invalido.png` | VERIFICADO |
| Operaciones de zonas, alertas y anotaciones | Definidas, sin implementar | `../openapi.yaml` | PENDIENTE |

## R04.5 Aportacion individual (2 pts)

| Evidencia | Archivo | Estado |
|---|---|---|
| Registro individual de Alejandro Pacheco Luna: aportacion, decisiones y alternativa justificada | `../individual/P04_PACHECO_ALEJANDRO.md` | ENTREGADO |
| Registros de los otros integrantes | `../individual/LEEME.md` (formato); cada quien entrega el suyo | PENDIENTE |
| Bitacora del incremento | `../../bitacora.md`, entradas de P04 | VERIFICADO |
| Historial de commits | `git log --format='%h %an %ad %s' --date=short -- api-spring frontend-angular docs/p04 scripts` | VERIFICADO |

## Capturas

| Archivo | Contenido |
|---|---|
| `img/01_acceso.png` | Sin sesion, `/lecturas` lleva al acceso |
| `img/02_acceso_rechazado.png` | Contrasena incorrecta: mensaje del 401 |
| `img/03_lecturas_observador.png` | Observador: formulario e historial servidos por la API |
| `img/04_lectura_valida.png` | 25.5: mensaje de exito y fila nueva |
| `img/05_lectura_con_alerta.png` | 38: aviso de alerta ALTA |
| `img/06_valor_no_numerico.png` | `abc`: 400 con error por campo; se conserva lo escrito |
| `img/07_fuera_de_rango_fisico.png` | 150: 422 con el rango fisico |
| `img/08_filtro_simulado.png` | Historial filtrado por procedencia |
| `img/09_lecturas_coordinacion.png` | Coordinacion: consulta sin formulario |
| `img/10_token_invalido.png` | Token alterado: regreso al acceso |
| `img/11_swagger_ui.png` | Operaciones que publica springdoc |
