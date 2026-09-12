# Indice de evidencia P02 - relacion con la rubrica R02

Producto de equipo: nombrar la carpeta/archivo de entrega en Eminus como `P02_EQUIPO_NN` (NN = numero de equipo).
Evidencia individual: `individual/P02_APELLIDO_NOMBRE.md` (una por integrante; incluida `P02_PACHECO_ALEJANDRO.md`).
Toda la evidencia se genera con `scripts/verify-module.sh M02` (texto) y `scripts/capturas.py` (imagenes); las
rutas locales se sustituyen por `<REPO>`, `<CATALINA_HOME>` y `<HOME>`.

## R02.1 Navegacion JSP/Servlet y flujo funcional (2.5 pts)

| Evidencia | Que demuestra | Archivo |
|---|---|---|
| Captura GET inicial | Pagina `/lecturas` servida por `LecturaServlet` + `lecturas.jsp`: catalogo y lecturas semilla | `img/01_get_inicial_lecturas.png` |
| Captura formulario lleno | Recorrido del usuario antes del POST | `img/02_formulario_lectura_valida.png` |
| Captura POST valido | 303 -> GET con mensaje "Lectura #N registrada" y fila nueva | `img/03_post_valido_resultado.png` |
| Captura validacion negativa (no numerico) | 400 con lista de errores y valores conservados | `img/04_post_invalido_no_numerico.png` |
| Captura validacion negativa (rango fisico) | 400 "fuera del rango fisico" | `img/05_post_invalido_rango_fisico.png` |
| Captura validacion negativa (vacio) | 400 con dos errores | `img/06_post_invalido_vacio.png` |
| Captura POST con alerta | Regla de negocio: lectura guardada + aviso de alerta ALTA | `img/07_post_valido_con_alerta.png` |
| Captura vista de alertas | Segunda pagina/servlet (`AlertaServlet` + `alertas.jsp`) | `img/08_get_alertas.png` |
| Captura error 404 | Pagina de error propia via `web.xml` | `img/10_error_404.png` |
| Respuestas HTTP crudas del recorrido | Codigos 200/303/400 y HTML devuelto por cada paso | `txt/07_*.txt` a `txt/14_*.txt` |
| Controladores y vistas | Codigo fuente | `src/main/java/mx/uv/dsw/huerto/web/*.java`, `src/main/webapp/WEB-INF/views/*.jsp` |

## R02.2 Despliegue correcto en Tomcat (2 pts)

| Evidencia | Que demuestra | Archivo |
|---|---|---|
| Log de compilacion | `BUILD SUCCESS`, WAR generado | `txt/01_build.txt` |
| Contenido del WAR | Estructura estandar (`WEB-INF/classes`, `lib`, `web.xml`, vistas) | `txt/03_war_contenido.txt` |
| Log de Tomcat | Despliegue de `web1.war` y `Server startup` | `txt/05_tomcat_log.txt` |
| Ruta de salud | Aplicacion ejecutandose y conectada (JSON) | `txt/06_health.txt`, `img/09_health_json.png` |
| Instrucciones | Pasos de instalacion y despliegue | `README.md` seccion "Instalacion y despliegue", `scripts/setenv.*.example` |
| Resumen de la verificacion | 15/15 VERIFICADO | `txt/16_resumen.txt`, `txt/verify-module_salida.txt` |

## R02.3 Persistencia en PostgreSQL (2.5 pts)

| Evidencia | Que demuestra | Archivo |
|---|---|---|
| Modelo de datos | 7 entidades, relaciones, reglas | `docs/modelo-datos.md`, `sql/01_schema.sql` |
| Semilla | Datos ficticios de prueba | `sql/02_seed.sql` |
| Conexion y esquema | `version()`, 7 tablas, conteos | `txt/04_postgres_verificacion.txt` |
| Operaciones verificables | Filas insertadas por el protocolo HTTP (lectura + alerta) | `txt/15_postgres_despues.txt` |
| Estado final coherente con capturas | Las dos lecturas de las capturas (27.5 C y 38 C) y su alerta ALTA | `txt/17_postgres_estado_final.txt` |
| Degradacion controlada | 503 con BD detenida y recuperacion | `txt/18_health_sin_bd.txt` |
| Repositorios JDBC | SQL parametrizado, transaccion, cierre de recursos | `src/main/java/mx/uv/dsw/huerto/repository/*.java`, `service/LecturaService.java` |
| Configuracion externa | Sin credenciales en el codigo | `src/main/java/mx/uv/dsw/huerto/config/DbConfig.java`, `.gitignore` |

## R02.4 README, capturas y repositorio (2 pts)

| Evidencia | Archivo |
|---|---|
| Guia completa (requisitos, instalacion, despliegue, datos de prueba, pruebas) | `README.md` |
| Acta breve, flujo principal, RF y criterios de aceptacion | `docs/acta-proyecto.md` |
| Trazabilidad RF -> codigo -> prueba -> evidencia -> R02 | `docs/requisitos-trazabilidad.md` |
| Bitacora con fallos diagnosticados | `docs/bitacora.md` |
| Estados VERIFICADO / NO_VERIFICADO / PENDIENTE | `docs/verification-report.md` |
| Historial de commits por componente | `git log --oneline` |

## R02.5 Orden y limpieza tecnica (1 pt)

| Evidencia | Archivo |
|---|---|
| Estructura Maven estandar y paquetes por capa (`config`, `model`, `repository`, `service`, `web`) | arbol en `README.md` |
| Exclusion de artefactos y secretos | `.gitignore` (`target/`, `setenv.*`, `.env`) |
| Script de limpieza que solo toca recursos declarados | `scripts/cleanup.sh`, `sql/99_cleanup.sql` |
| Pruebas unitarias separadas de la persistencia | `src/test/java/.../LecturaValidatorTest.java`, `txt/02_pruebas_unitarias.txt` |
