# Indice de evidencia P02 (PR09) - relacion con la rubrica R02

Producto de equipo DSW-E01: nombrar la entrega en Eminus como `P02_EQUIPO_01`.
Documento de entrega del equipo: `docs/entrega/P02_EQUIPO_01.docx` (y su PDF). Las contribuciones de cada integrante estan en su seccion 10.
Toda la evidencia se genera con `scripts/verify-module.sh M02` (texto) y `scripts/capturas.py` (imagenes); las
rutas locales se sustituyen por `<REPO>`, `<CATALINA_HOME>` y `<HOME>`.

## R02.1 Navegacion JSP/Servlet y flujo funcional (2.5 pts)

| Evidencia | Que demuestra | Archivo |
|---|---|---|
| Captura GET inicial | `/lecturas` (LecturaServlet + lecturas.jsp): sensores por zona/variable con umbral e historial semilla (RF01, RF02, RF04, RF05) | `img/01_get_inicial_lecturas.png` |
| Captura formulario lleno | Recorrido del observador antes del POST (RF03) | `img/02_formulario_lectura_valida.png` |
| Captura POST valido | 303 -> GET con "Lectura #N registrada", fila `manual` (CA01) | `img/03_post_valido_resultado.png` |
| Captura validacion negativa (no numerico) | 400 con lista de errores y valores conservados (CA02) | `img/04_post_invalido_no_numerico.png` |
| Captura validacion negativa (rango fisico) | 400 "fuera del rango fisico" (prueba minima de la ficha: validar unidad/rango) | `img/05_post_invalido_rango_fisico.png` |
| Captura validacion negativa (vacio) | 400 con dos errores | `img/06_post_invalido_vacio.png` |
| Captura POST con alerta | Lectura guardada + aviso de alerta ALTA (RF06) | `img/07_post_valido_con_alerta.png` |
| Captura vista de alertas | AlertaServlet + alertas.jsp (RF06) | `img/08_get_alertas.png` |
| Captura zonas y anotaciones | AnotacionServlet + anotaciones.jsp (RF01, RF06) | `img/11_get_zonas_anotaciones.png` |
| Captura anotacion valida / invalida | 303 con mensaje; 400 por texto corto (roles funcionales) | `img/12_post_anotacion_valida.png`, `img/13_post_anotacion_invalida.png` |
| Captura error 404 | Pagina de error propia via `web.xml` | `img/10_error_404.png` |
| Respuestas HTTP crudas | Codigos 200/303/400 y HTML de cada paso | `txt/07_*` a `txt/14c_*` |
| Controladores y vistas | Codigo fuente | `src/main/java/mx/uv/dsw/huerto/web/*.java`, `src/main/webapp/WEB-INF/views/*.jsp` |

## R02.2 Despliegue correcto en Tomcat (2 pts)

| Evidencia | Que demuestra | Archivo |
|---|---|---|
| Log de compilacion | `BUILD SUCCESS`, 14 pruebas unitarias, WAR generado | `txt/01_build.txt`, `txt/02_pruebas_unitarias.txt` |
| Contenido del WAR | Estructura estandar (`WEB-INF/classes`, `lib`, `web.xml`, vistas) | `txt/03_war_contenido.txt` |
| Log de Tomcat | Despliegue de `web1.war` y `Server startup` | `txt/05_tomcat_log.txt` |
| Ruta de salud | Aplicacion ejecutandose y conectada (JSON) | `txt/06_health.txt`, `img/09_health_json.png` |
| Instrucciones | Pasos de instalacion y despliegue | `README.md` seccion 3, `scripts/setenv.*.example` |
| Resumen de la verificacion | 18/18 VERIFICADO | `txt/16_resumen.txt`, `txt/verify-module_salida.txt` |

## R02.3 Persistencia en PostgreSQL (2.5 pts)

| Evidencia | Que demuestra | Archivo |
|---|---|---|
| Modelo de datos | 7 entidades (6 de la ficha PR09 + sensor), relaciones, `CHECK` | `docs/modelo-datos.md`, `sql/01_schema.sql` |
| Semilla | Datos ficticios etiquetados `simulado` | `sql/02_seed.sql` |
| Conexion y esquema | `version()`, 7 tablas, conteos | `txt/04_postgres_verificacion.txt` |
| Capturas de psql (PostgreSQL 16, Docker) | Conexion, tablas y conteos; estructura de `lectura` y `anotacion` (FK, CHECK, indices); lecturas con procedencia, alertas y anotaciones | `img/14_psql_docker_tablas.png`, `img/17_psql_docker_estructura.png`, `img/15_psql_docker_lecturas.png` |
| Captura de psql (PostgreSQL 17 instalado, Opcion B) | Mismas 7 tablas y lectura registrada desde la aplicacion en el puerto 5433 | `img/16_psql_nativo_pg17.png` |
| Operaciones verificables | Filas insertadas por el protocolo HTTP (lectura, alerta, anotacion) | `txt/15_postgres_despues.txt` |
| Estado final coherente con capturas | Las dos lecturas de las capturas (27.5 C y 38 C), su alerta ALTA y la anotacion | `txt/17_postgres_estado_final.txt` |
| Degradacion controlada | 503 con BD detenida y recuperacion | `txt/18_health_sin_bd.txt` |
| Opcion B del README | La misma aplicacion conectada a PostgreSQL 17.11 instalado en Windows (puerto 5433) solo cambiando `DB_URL`: esquema, semilla, `/health`, POST 303 y 400, consulta psql | `txt/19_postgres_nativo_opcionB.txt` |
| Repositorios JDBC | SQL parametrizado, transaccion, cierre de recursos | `src/main/java/mx/uv/dsw/huerto/repository/*.java`, `service/LecturaService.java` |
| Configuracion externa | Sin credenciales en el codigo | `src/main/java/mx/uv/dsw/huerto/config/DbConfig.java`, `.gitignore` |

## R02.4 README, capturas y repositorio (2 pts)

| Evidencia | Archivo |
|---|---|
| Guia completa (requisitos, instalacion, despliegue, datos de prueba, pruebas) | `README.md` |
| Seleccion F02 (comparacion de tres opciones y plantilla) | `docs/F02-seleccion-proyecto.md` |
| Acta breve, roles funcionales, flujo principal, RF de la ficha y criterios de aceptacion | `docs/acta-proyecto.md` |
| Trazabilidad RF (C11) -> codigo -> prueba -> evidencia -> R02 | `docs/requisitos-trazabilidad.md` |
| Bitacora con fallos diagnosticados | `docs/bitacora.md` |
| Estados VERIFICADO / NO_VERIFICADO / PENDIENTE | `docs/verification-report.md` |
| Historial de commits por autor | `git log --oneline` |

## R02.5 Orden y limpieza tecnica (1 pt)

| Evidencia | Archivo |
|---|---|
| Estructura Maven estandar y paquetes por capa (`config`, `model`, `repository`, `service`, `web`) | arbol en `README.md` |
| Exclusion de artefactos y secretos; finales de linea normalizados | `.gitignore`, `.gitattributes` |
| Script de limpieza que solo toca recursos declarados | `scripts/cleanup.sh`, `sql/99_cleanup.sql` |
| Pruebas unitarias separadas de la persistencia | `src/test/java/...`, `txt/02_pruebas_unitarias.txt` |
