# Reporte de verificacion - P02 / M02 - PRxx Monitoreo de huerto

Fecha: 2026-09-11. Entorno: Windows 11, Java 11.0.32.1, Maven 3.9.9, Tomcat 9.0.115, PostgreSQL 16.15 (Docker), Git Bash, curl 8.21, Python 3.11 + Playwright (solo capturas).
Comando principal: `CATALINA_HOME=<ruta-tomcat> ./scripts/verify-module.sh M02` (salida en `docs/evidencia/txt/verify-module_salida.txt`).

Estados: **VERIFICADO** (ejecutado y comprobado con evidencia), **NO_VERIFICADO** (no se ejecuto o no se pudo comprobar), **PENDIENTE** (planeado para otro momento/integrante).

## Compilacion, empaquetado y despliegue

| Prueba | Comando | Resultado esperado | Estado | Evidencia |
|---|---|---|---|---|
| Versiones del paquete | `java -version`, `mvn -version` | Java 11, Maven 3.9.9 | VERIFICADO | `txt/00_versiones.txt` |
| Build + pruebas unitarias | `mvn clean package` | `BUILD SUCCESS`, `Tests run: 10, Failures: 0` | VERIFICADO | `txt/01_build.txt`, `txt/02_pruebas_unitarias.txt` |
| Inspeccion del WAR | `unzip -l target/web1.war` | classes, `WEB-INF/web.xml`, vistas, `jstl-1.2.jar`, `postgresql-42.7.2.jar` | VERIFICADO | `txt/03_war_contenido.txt` |
| Despliegue en Tomcat 9 (Windows) | copiar `web1.war` a `webapps/`, `startup.bat` | `Server startup`, contexto `/web1` desplegado | VERIFICADO | `txt/05_tomcat_log.txt` |
| Despliegue en Linux/macOS con `setenv.sh` | `startup.sh` | igual | NO_VERIFICADO | - |
| Ruta de salud | `curl -i /web1/health` | 200, `db=UP`, version PostgreSQL 16 | VERIFICADO | `txt/06_health.txt`, `img/09_health_json.png` |

## PostgreSQL

| Prueba | Comando | Resultado esperado | Estado | Evidencia |
|---|---|---|---|---|
| Creacion de esquema y semilla | `docker compose up -d` (ejecuta `01_schema.sql`, `02_seed.sql`) | 7 tablas; conteos 1/2/4/5/5/2/0 | VERIFICADO | `txt/04_postgres_verificacion.txt` |
| Persistencia tras el protocolo HTTP | `psql -f sql/03_consultas_verificacion.sql` | lecturas con observacion `verify-module ...` y una alerta ALTA | VERIFICADO | `txt/15_postgres_despues.txt` |
| Estado final coherente con capturas | idem | las dos lecturas de las capturas (27.5 C en rango y 38 C con alerta ALTA) | VERIFICADO | `txt/17_postgres_estado_final.txt` |
| Limpieza selectiva | `psql -f sql/99_cleanup.sql` | borra solo `origen='manual'`; semilla intacta (2 lecturas, 0 alertas) | VERIFICADO | bitacora #11 |

## Flujo principal y validaciones (HTTP)

| Prueba | Entrada | Resultado esperado | Estado | Evidencia |
|---|---|---|---|---|
| GET inicial | `GET /web1/lecturas` | 200; catalogo de 5 sensores y 2 lecturas semilla | VERIFICADO | `txt/07_get_inicial.txt`, `img/01_get_inicial_lecturas.png` |
| POST valido (positiva) | `sensorId=<SEN-A-TEMP-01>&valor=25.5` | 303 -> `?creada=N`; fila nueva; sin alerta | VERIFICADO | `txt/08_post_valido.txt`, `img/02_*.png`, `img/03_*.png` |
| POST invalido: no numerico (negativa) | `valor=abc` | 400, "El valor debe ser numerico" | VERIFICADO | `txt/09_*.txt`, `img/04_*.png` |
| POST invalido: vacio (negativa) | `sensorId=&valor=` | 400, dos mensajes | VERIFICADO | `txt/10_*.txt`, `img/06_*.png` |
| POST invalido: rango fisico (negativa) | `valor=150` | 400, "fuera del rango fisico ... [-10.00, 60.00]" | VERIFICADO | `txt/11_*.txt`, `img/05_*.png` |
| POST invalido: sensor inexistente (negativa) | `sensorId=999` | 400, "El sensor seleccionado no existe." | VERIFICADO (curl manual) | bitacora #6 |
| POST invalido: tres decimales | `valor=24.555` | 400 | VERIFICADO (unitaria) / NO_VERIFICADO (HTTP) | `txt/02_pruebas_unitarias.txt` |
| POST invalido: sensor inactivo | sensor con `activo=false` | 400 | VERIFICADO (unitaria) / NO_VERIFICADO (HTTP) | `txt/02_pruebas_unitarias.txt` |
| POST valido con alerta (positiva) | `valor=38` | 303 -> `?creada=N&alerta=ALTA`; fila en `lectura` y `alerta` | VERIFICADO | `txt/12_*.txt`, `img/07_*.png` |
| GET con persistencia | `GET /web1/lecturas` | 200; filas 2 -> 4 | VERIFICADO | `txt/13_*.txt` |
| GET alertas | `GET /web1/alertas` | 200; alerta ALTA listada | VERIFICADO | `txt/14_*.txt`, `img/08_*.png` |
| Ruta inexistente | `GET /web1/ruta-inexistente` | 404 con pagina de error propia | VERIFICADO | `img/10_error_404.png` |
| Base de datos detenida (negativa de infraestructura) | `docker stop` + `GET /health`, `GET /lecturas` | 503 `DOWN` con motivo; 500 con pagina controlada; recuperacion al reiniciar la BD | VERIFICADO | `txt/18_health_sin_bd.txt` |
| Variables `DB_*` ausentes | Tomcat sin `setenv` | 503 "Faltan variables" | NO_VERIFICADO | - |

## Reproducibilidad

| Prueba | Estado | Nota |
|---|---|---|
| `verify-module.sh M02` termina con `RESULTADO: VERIFICADO` en la maquina de desarrollo | VERIFICADO | 15/15 comprobaciones, `txt/16_resumen.txt` |
| Reconstruccion por otro integrante en maquina limpia siguiendo solo el README | PENDIENTE | asignada al equipo antes del cierre |
| `cleanup.sh` deja la semilla intacta y `cleanup.sh --all` retira Tomcat/web1 y el contenedor | VERIFICADO (parcial) | se ejecuto la limpieza selectiva; `--all` NO_VERIFICADO para no perder el entorno de evidencia |

## Limitaciones declaradas

- Sin autenticacion: cualquier visitante puede registrar lecturas (fuera de alcance de P02).
- Conexion JDBC por peticion (sin pool): suficiente para el laboratorio, no para carga concurrente.
- Fechas mostradas en UTC del servidor de BD; la zona horaria local se abordara en un incremento posterior.
