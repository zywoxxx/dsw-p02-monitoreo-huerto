# Reporte de verificacion - P02 / M02 - PR09 Monitoreo de huerto o ambiente

Fecha: 2026-09-11. Entorno: Windows 11, Java 11.0.32.1, Maven 3.9.9, Tomcat 9.0.115, PostgreSQL 16.15 (Docker), Git Bash, curl 8.21, Python 3.11 + Playwright (solo capturas).
Comando principal: `CATALINA_HOME=<ruta-tomcat> ./scripts/verify-module.sh M02` (salida en `docs/evidencia/txt/verify-module_salida.txt`).

Estados: **VERIFICADO** (ejecutado y comprobado con evidencia), **NO_VERIFICADO** (no se ejecuto o no se pudo comprobar), **PENDIENTE** (planeado para otro momento/integrante).

## Compilacion, empaquetado y despliegue

| Prueba | Comando | Resultado esperado | Estado | Evidencia |
|---|---|---|---|---|
| Versiones del paquete | `java -version`, `mvn -version` | Java 11, Maven 3.9.9 | VERIFICADO | `txt/00_versiones.txt` |
| Build + pruebas unitarias | `mvn clean package` | `BUILD SUCCESS`, `Tests run: 14, Failures: 0` | VERIFICADO | `txt/01_build.txt`, `txt/02_pruebas_unitarias.txt` |
| Inspeccion del WAR | `unzip -l target/web1.war` | classes, `WEB-INF/web.xml`, 4 vistas, `jstl-1.2.jar`, `postgresql-42.7.2.jar` | VERIFICADO | `txt/03_war_contenido.txt` |
| Despliegue en Tomcat 9 (Windows) | copiar `web1.war` a `webapps/`, `startup.bat` | `Server startup`, contexto `/web1` desplegado | VERIFICADO | `txt/05_tomcat_log.txt` |
| Despliegue en Linux/macOS con `setenv.sh` | `startup.sh` | igual | NO_VERIFICADO | - |
| Ruta de salud | `curl -i /web1/health` | 200, `db=UP`, version PostgreSQL 16 | VERIFICADO | `txt/06_health.txt`, `img/09_health_json.png` |

## PostgreSQL (RF07)

| Prueba | Comando | Resultado esperado | Estado | Evidencia |
|---|---|---|---|---|
| Creacion de esquema y semilla | `docker compose up -d` (ejecuta `01_schema.sql`, `02_seed.sql`) | 7 tablas; conteos zona 2, variable 4, sensor 5, umbral 5, lectura 2, alerta 0, anotacion 1 | VERIFICADO | `txt/04_postgres_verificacion.txt` |
| Persistencia tras el protocolo HTTP | `psql -f sql/03_consultas_verificacion.sql` | lecturas con observacion `verify-module ...`, alerta ALTA y anotacion `[prueba] Hojas...` | VERIFICADO | `txt/15_postgres_despues.txt` |
| Estado final coherente con capturas | idem | las dos lecturas de las capturas (27.5 C en rango y 38 C con alerta ALTA) y la anotacion del OBSERVADOR | VERIFICADO | `txt/17_postgres_estado_final.txt` |
| Limpieza selectiva | `psql -f sql/99_cleanup.sql` | borra solo `origen='manual'` y anotaciones `[prueba]`; semilla intacta | VERIFICADO | bitacora #15 |
| Restricciones de integridad (RNF04) | `CHECK`/`FK` en `01_schema.sql` | rangos, `origen`, `nivel`, `autor_rol` restringidos en BD | VERIFICADO (por definicion del esquema; sin prueba de violacion directa) | `sql/01_schema.sql` |

## Flujo principal y validaciones (HTTP)

| Prueba | Entrada | Resultado esperado | Estado | Evidencia |
|---|---|---|---|---|
| GET inicial (RF01, RF02, RF04, RF05) | `GET /web1/lecturas` | 200; 5 sensores con zona, variable, rango y umbral; 2 lecturas `simulado` | VERIFICADO | `txt/07_get_inicial.txt`, `img/01_*.png` |
| POST valido (RF03, CA01) | `sensorId=<SEN-A-TEMP-01>&valor=25.5` | 303 -> `?creada=N`; fila `manual` con instante; sin alerta | VERIFICADO | `txt/08_post_valido.txt`, `img/02_*.png`, `img/03_*.png` |
| POST invalido: no numerico (CA02) | `valor=abc` | 400, "El valor debe ser numerico" | VERIFICADO | `txt/09_*.txt`, `img/04_*.png` |
| POST invalido: vacio (CA02) | `sensorId=&valor=` | 400, dos mensajes | VERIFICADO | `txt/10_*.txt`, `img/06_*.png` |
| POST invalido: rango fisico (prueba minima "validar unidad/rango") | `valor=150` | 400, "fuera del rango fisico ... [-10.00, 60.00]" | VERIFICADO | `txt/11_*.txt`, `img/05_*.png` |
| POST invalido: sensor inexistente | `sensorId=999` | 400, "El sensor seleccionado no existe." | VERIFICADO (curl manual) | bitacora #6 |
| POST invalido: tres decimales | `valor=24.555` | 400 | VERIFICADO (unitaria) / NO_VERIFICADO (HTTP) | `txt/02_pruebas_unitarias.txt` |
| POST invalido: sensor inactivo | sensor con `activo=false` | 400 | VERIFICADO (unitaria) / NO_VERIFICADO (HTTP) | `txt/02_pruebas_unitarias.txt` |
| POST valido con alerta (RF06, prueba minima "activar alertas") | `valor=38` | 303 -> `?creada=N&alerta=ALTA`; fila en `lectura` y `alerta` | VERIFICADO | `txt/12_*.txt`, `img/07_*.png` |
| GET con persistencia (RF05) | `GET /web1/lecturas` | 200; filas 2 -> 4, ordenadas por instante | VERIFICADO | `txt/13_*.txt` |
| GET alertas (RF06) | `GET /web1/alertas` | 200; alerta ALTA listada | VERIFICADO | `txt/14_*.txt`, `img/08_*.png` |
| GET zonas y anotaciones (RF01, RF06) | `GET /web1/anotaciones` | 200; 2 zonas y la anotacion semilla | VERIFICADO | `txt/14a_*.txt`, `img/11_*.png` |
| POST anotacion valida (RF06, roles funcionales) | zona Cama A, rol OBSERVADOR, texto valido | 303 -> `?creada=N`; fila en `anotacion` | VERIFICADO | `txt/14b_*.txt`, `img/12_*.png` |
| POST anotacion invalida | rol `ADMIN`, texto `ok` | 400 con dos mensajes | VERIFICADO | `txt/14c_*.txt`, `img/13_*.png` |
| Anotacion con lectura inexistente | `lecturaId=999` | 400 "La lectura #999 no existe." | NO_VERIFICADO (implementado, sin caso en el protocolo) | - |
| Desactivar/atender alertas (prueba minima de la ficha) | - | - | PENDIENTE (incremento posterior) | - |
| Ruta inexistente | `GET /web1/ruta-inexistente` | 404 con pagina de error propia | VERIFICADO | `img/10_error_404.png` |
| Base de datos detenida | `docker stop` + `GET /health`, `GET /lecturas` | 503 `DOWN` con motivo; 500 con pagina controlada; recuperacion al reiniciar | VERIFICADO | `txt/18_health_sin_bd.txt` |
| Variables `DB_*` ausentes | Tomcat sin `setenv` | 503 "Faltan variables" | NO_VERIFICADO | - |

## Criterios de aceptacion C11 en P02

| CA | Estado | Evidencia |
|---|---|---|
| CA01 flujo principal completo con cambio persistido | VERIFICADO | `img/03_*`, `img/07_*`, `txt/15_*`, `txt/17_*` |
| CA02 caso invalido rechazado con mensaje y sin alterar datos | VERIFICADO | `txt/09_*` a `txt/11_*`, `txt/14c_*`, conteos sin cambio en `txt/15_*` |
| CA05 otra persona reproduce con el README | VERIFICADO en la maquina de desarrollo / PENDIENTE por otro integrante | `txt/16_resumen.txt` |
| CA06 autoria, contribucion individual, limitaciones, cambios de alcance | VERIFICADO | commits, `docs/evidencia/individual/`, este reporte, `docs/F02-seleccion-proyecto.md` |
| CA03 API 2xx/4xx, CA04 evento IoT | NO APLICA en P02 (Web 3.0 / 4.0) | - |

## Reproducibilidad

| Prueba | Estado | Nota |
|---|---|---|
| `verify-module.sh M02` termina con `RESULTADO: VERIFICADO` en la maquina de desarrollo | VERIFICADO | 18/18 comprobaciones, `txt/16_resumen.txt` |
| Reconstruccion por otro integrante en maquina limpia siguiendo solo el README | PENDIENTE | asignada al equipo antes del cierre |
| `cleanup.sh` deja la semilla intacta; `cleanup.sh --all` retira Tomcat/web1 y el contenedor | VERIFICADO (parcial) | limpieza selectiva ejecutada; `--all` NO_VERIFICADO para no perder el entorno de evidencia |

## Limitaciones declaradas

- Sin autenticacion: el rol funcional se declara en el formulario de anotaciones y se persiste, pero no se verifica identidad (fuera del alcance de Web 1.0; RNF02 se atendera en Web 2.0/3.0).
- Conexion JDBC por peticion (sin pool): suficiente para el laboratorio, no para carga concurrente.
- Fechas mostradas en UTC del servidor de BD; la zona horaria local se abordara en un incremento posterior.
- Zonas, sensores y umbrales se cargan por SQL; su alta desde la interfaz corresponde al responsable en Web 2.0.
