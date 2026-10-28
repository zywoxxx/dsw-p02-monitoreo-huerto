# P05 - Indice de evidencia frente a R05

Producto de equipo DSW-E01: entrega en Eminus como `P05_EQUIPO_01`. La evidencia de texto y las capturas las genera
`./scripts/verify-module.sh M05`; `txt/14_base_detenida.txt` lo genera `./scripts/prueba_base_detenida.sh`. Las rutas
locales, el nombre del equipo y el usuario del sistema se sustituyen por `<REPO>`, `<HOME>`, `<EQUIPO>` y `<USUARIO>`;
los tokens se recortan y las contrasenas no se imprimen. La evidencia de P02, P03 y P04 se conserva intacta.

Evidencias minimas de la guia: **Codigo** (repositorio), **Pruebas API** (R05.1, R05.4), **Build Angular** (R05.2),
**Recorrido extremo a extremo** (R05.2, R05.3).

## R05.1 API Spring funcional: endpoints y respuestas verificables (3 pts)

| Evidencia | Que demuestra | Archivo | Estado |
|---|---|---|---|
| Peticion y respuesta real de cada caso del contrato | 13 operaciones: salud, acceso, zonas, sensores, lecturas, alertas (consulta y cambio de estado) y anotaciones | `txt/pruebas_api.txt` | VERIFICADO (64 de 64) |
| Resumen por caso | VERIFICADO / NO_VERIFICADO de cada uno | `txt/pruebas_api_resultados.txt` | VERIFICADO |
| OpenAPI generado desde el codigo y su comparacion con el contrato escrito | nada implementado fuera del contrato; nada del contrato sin implementar (caso 64) | `txt/openapi_generado.json`, `img/22_swagger_ui.png`, `../../p04/openapi.yaml` | VERIFICADO |
| Contenido del jar | controladores de zonas, alertas y anotaciones dentro del artefacto | `txt/03_jar_contenido.txt` | VERIFICADO |
| Catalogo legible de endpoints | entrada, salida y errores de cada operacion con ejemplos reales | `../endpoints.md` | VERIFICADO |

## R05.2 Integracion Angular: consumo de servicios y flujo de usuario (3 pts)

| Evidencia | Que demuestra | Archivo | Estado |
|---|---|---|---|
| Build del cliente | `ng build` sin errores | `txt/05_build_frontend.txt` | VERIFICADO |
| Pruebas del cliente | 9 specs: sesion por rol, cuerpos que envia `ApiService` (POST lecturas, PATCH alertas, POST anotaciones), parametros de filtro | `txt/06_pruebas_frontend.txt` | VERIFICADO |
| Recorrido en navegador real (Playwright) | 23 casos con los tres roles: acceso, captura, alertas (atender y reabrir), anotaciones (validas e invalidas), filtros, permisos de vista, token invalido | `txt/recorrido_angular.txt` | VERIFICADO (23 de 23) |
| Capturas del flujo de usuario | ver la tabla de capturas al final | `img/01` a `img/22` | VERIFICADO |
| Codigo del cliente | `AlertasComponent`, `AnotacionesComponent`, `ApiService`, `SesionService`, `modelos.ts` | `frontend-angular/src/app/` | repositorio |

## R05.3 Persistencia PostgreSQL: operaciones y estado de datos reproducible (2 pts)

| Evidencia | Que demuestra | Archivo | Estado |
|---|---|---|---|
| Estado antes y despues | tablas, conteos, ultimas lecturas, alertas con `atendida_en`/`atendida_por`, anotaciones | `txt/08_postgres_antes.txt`, `txt/12_postgres_despues.txt` | VERIFICADO |
| Migracion no destructiva | `sql/04` aplicada sobre la base existente; columnas comprobadas en `information_schema` | `txt/08b_migracion_p05.txt`, `sql/04_p05_atencion_alerta.sql`, `sql/01_schema.sql` | VERIFICADO |
| Cambio de estado comprobado en la base | tras `PATCH` true: `atendida = true` y `atendida_por = 'RESPONSABLE'`; tras `PATCH` false: ambas columnas NULL | `txt/pruebas_api.txt` casos 41 y 47; `txt/recorrido_angular.txt` casos 12 y 13 | VERIFICADO |
| Conteos en cada caso | cada alta suma 1; cada rechazo deja la base igual | `txt/pruebas_api.txt` | VERIFICADO |
| Transaccion y base detenida | ninguna escritura a medias; 503 en todas las rutas con la base detenida; recuperacion sin reiniciar | `txt/14_base_detenida.txt` | VERIFICADO |
| Modelo y reglas | donde vive cada regla (API o base) | `../modelo-datos.md`, `../../modelo-datos.md` | VERIFICADO |

## R05.4 Errores y validacion: casos invalidos y respuestas controladas (2 pts)

| Evidencia | Que demuestra | Archivo | Estado |
|---|---|---|---|
| Rechazos de lecturas | 400 (no numerico, decimales, faltantes, JSON roto, observacion larga), 404, 409, 422, 401, 403 | `txt/pruebas_api.txt` casos 17 a 27 | VERIFICADO |
| Rechazos del cambio de estado | 403 por rol, 409 por estado repetido, 400 por cuerpo, 404, 401 | casos 39, 40, 42 a 46 | VERIFICADO |
| Rechazos de anotaciones | texto corto, largo, con espacios, sin zona, sin texto, lectura negativa, zona o lectura inexistente, lectura de otra zona, sin token | casos 54 a 63 | VERIFICADO |
| Parametros de consulta invalidos | 400 en `zonaId=abc`, `nivel=MEDIA`, `atendida=quiza`, `origen=inventado` | casos 08, 11, 34, 36, 49 | VERIFICADO |
| Errores vistos desde el cliente | 400, 404 y 422 en pantalla con lo capturado conservado | `img/06`, `img/07`, `img/14`, `img/15`, `img/16` | VERIFICADO |
| Cuerpo de error uniforme y sin trazas | mismo esquema `Error` en todos | `txt/pruebas_api.txt` (validado contra el esquema) | VERIFICADO |

## R05.5 Pruebas y repositorio: resultados, README y trazabilidad (2 pts)

| Evidencia | Archivo | Estado |
|---|---|---|
| Pruebas unitarias del backend (37) | `txt/01_build_api.txt`, `txt/02_pruebas_api_unitarias.txt` | VERIFICADO |
| Resumen de la verificacion reproducible | `txt/13_resumen.txt`, `txt/00_versiones.txt` | VERIFICADO |
| README con instalacion, migracion, ejecucion, demostracion, verificacion y limpieza | `README.md`, secciones 7 y 8 | VERIFICADO |
| Trazabilidad RF -> componente -> prueba -> evidencia -> R05 | `../trazabilidad-r05.md` | VERIFICADO |
| Verificacion, fallos, limitaciones y pendientes | `../verificacion.md` | VERIFICADO |
| Arquitectura y decisiones D10 a D17 | `../arquitectura.md` | VERIFICADO |
| Bitacora del incremento | `../../bitacora.md`, entradas de P05 | VERIFICADO |
| Historial de commits | `git log --oneline 9f398d6..HEAD` | VERIFICADO |

## Despliegue en Docker detras de nginx (complemento a R05.1 y R05.3)

| Evidencia | Que demuestra | Archivo | Estado |
|---|---|---|---|
| Los 64 casos del contrato contra `http://localhost` (nginx -> api -> db, cada uno en su contenedor) | la pila en Docker cumple el mismo contrato; 63 VERIFICADO y el caso 29 (CORS) no aplica por ser el mismo origen | `docker/pruebas_api.txt`, `docker/pruebas_api_resultados.txt` | VERIFICADO |
| Definicion de los contenedores y la red | `docker/docker-compose.yml` (perfil `app`), `api-spring/Dockerfile`, `frontend-angular/Dockerfile`, `frontend-angular/nginx.conf`, `../diagramas/05_docker_nginx.png` | repositorio | VERIFICADO |

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
| `img/12_alerta_atendida.png` | Responsable marca la alerta como atendida: etiqueta con rol y fecha |
| `img/13_alerta_reabierta.png` | La misma alerta reabierta: vuelve a pendiente |
| `img/14_anotacion_texto_corto.png` | Texto "ok": 400 en pantalla, lo capturado se conserva |
| `img/15_anotacion_texto_largo.png` | 301 caracteres: el cliente no recorta y la API responde 400 |
| `img/16_anotacion_lectura_inexistente.png` | Lectura 999999: 404 en pantalla |
| `img/17_anotacion_valida.png` | Anotacion registrada y firmada por RESPONSABLE |
| `img/18_anotaciones_filtro_zona.png` | Lista filtrada por zona |
| `img/19_alertas_coordinacion.png` | Coordinacion ve las alertas sin botones de atender |
| `img/20_anotacion_coordinacion.png` | Anotacion firmada por COORDINACION |
| `img/21_token_invalido.png` | Token alterado: regreso al acceso |
| `img/22_swagger_ui.png` | Operaciones que publica springdoc |

Los numeros 10 y 11 no existen: el recorrido numera las capturas por caso y esos dos casos (salir y coordinacion sin
botones de captura) no toman captura propia.
