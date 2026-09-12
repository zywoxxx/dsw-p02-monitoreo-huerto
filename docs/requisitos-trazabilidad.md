# Matriz de trazabilidad - RF de la ficha PR09 (C11) -> codigo -> prueba -> evidencia -> R02

| RF (C11) | Criterio de aceptacion en P02 | Codigo | SQL | Prueba | Evidencia | Criterio R02 |
|---|---|---|---|---|---|---|
| RF01 Zonas | GET muestra zonas con nombre, cultivo y ubicacion. | `AnotacionServlet.doGet` -> `AnotacionRepository.findZonas` -> `anotaciones.jsp` (`#tabla-zonas`); columna Zona en `lecturas.jsp` | tabla `zona`, `02_seed.sql` | `verify-module.sh` "GET /anotaciones" | `txt/14a_get_anotaciones.txt`, `img/11_get_zonas_anotaciones.png` | Navegacion (2.5) |
| RF02 Variables | Cada sensor muestra variable, unidad y rango fisico. | `SensorRepository.findActivos` -> `lecturas.jsp` (`#tabla-sensores`) | tabla `variable` con `CHECK` | `verify-module.sh` "GET inicial" | `txt/07_get_inicial.txt`, `img/01_get_inicial_lecturas.png` | Navegacion (2.5) + Persistencia (2.5) |
| RF03 Lecturas | POST valido -> 303 + fila `manual` con instante; POST invalido -> 400 sin insertar. | `LecturaServlet.doPost`, `LecturaValidator`, `LecturaService.registrar`, `LecturaRepository.insertLectura` | `INSERT INTO lectura ... RETURNING id`; `CHECK origen` | `LecturaValidatorTest` (10); `verify-module.sh` "POST valido" y "POST invalido" x3 | `txt/08_*` a `txt/11_*`, `img/02_*` a `img/06_*` | Navegacion (2.5) + Persistencia (2.5) |
| RF04 Umbrales | Umbral [min, max] visible por sensor; base de la alerta. | `Sensor.isConUmbral`, `LecturaValidator.nivelAlerta` | tabla `umbral` con `CHECK` | `LecturaValidatorTest.valorSobreUmbralGeneraAlertaAlta`, `valorBajoUmbralGeneraAlertaBaja` | `txt/02_pruebas_unitarias.txt`, `img/01_*` | Persistencia (2.5) |
| RF05 Historial | GET posterior muestra la lectura nueva ordenada por instante. | `LecturaRepository.findRecientes` -> `lecturas.jsp` (`#tabla-lecturas`) | `ORDER BY registrado_en DESC LIMIT ?`; indice | `verify-module.sh` "GET con persistencia" | `txt/13_get_persistencia.txt`, `txt/15_*`, `txt/17_*` | Persistencia (2.5) |
| RF06 Alertas y anotaciones | Lectura fuera de umbral crea 1 alerta; anotacion valida -> 303, rol invalido/texto corto -> 400. | `LecturaService` (transaccion), `LecturaRepository.insertAlerta`, `AlertaServlet`, `AnotacionServlet`, `AnotacionValidator`, `AnotacionRepository` | `INSERT INTO alerta`, `INSERT INTO anotacion`; `CHECK nivel`, `CHECK autor_rol` | `verify-module.sh` "POST 38 C", "GET alertas", "POST anotacion valida/invalida"; `AnotacionValidatorTest` (4) | `txt/12_*`, `txt/14_*`, `txt/14b_*`, `txt/14c_*`, `img/07_*`, `img/08_*`, `img/12_*`, `img/13_*` | Navegacion (2.5) + Persistencia (2.5) |
| RF07 Modelo relacionado | 7 tablas con FK/UNIQUE/CHECK; conteos y joins verificables. | `sql/01_schema.sql`, repositorios | `03_consultas_verificacion.sql` | `verify-module.sh` "PostgreSQL" | `txt/04_postgres_verificacion.txt`, `txt/15_*`, `txt/17_*`, `docs/modelo-datos.md` | Persistencia (2.5) |
| RF08 API Web 3.0 | Fuera de P02. | - | - | - | - | - |
| RF09 IoT simulado Web 4.0 | Fuera de P02; `origen` ya distingue `simulado`. | `lectura.origen` | `CHECK origen IN ('manual','simulado')` | semilla `simulado` vs capturas `manual` | `img/03_*`, `txt/17_*` | Persistencia (2.5) |
| Salud (RNF01) | `/health` 200 `db=UP`; 503 si no hay BD. | `HealthServlet`, `DbConfig`, `AppContextListener` | `SELECT version(), count(*)` | `verify-module.sh` "Ruta de salud"; prueba con BD detenida | `txt/06_health.txt`, `txt/18_health_sin_bd.txt`, `img/09_*` | Despliegue (2) + Persistencia (2.5) |
| Despliegue | WAR `web1.war` en Tomcat 9.0.115 con variables externas. | `pom.xml`, `web.xml`, `scripts/setenv.*.example` | - | `verify-module.sh` "Despliegue en Tomcat 9" | `txt/01_build.txt`, `txt/03_war_contenido.txt`, `txt/05_tomcat_log.txt` | Despliegue (2) |
| Documentacion | README, acta, F02, modelo, bitacora, indice. | `README.md`, `docs/*.md` | `sql/*.sql` | revision cruzada | `docs/evidencia/INDICE.md` | README, capturas y repositorio (2) |
| Orden tecnico | Estructura Maven estandar, paquetes por capa, sin archivos innecesarios. | `.gitignore`, `.gitattributes` | - | `git status` limpio tras `mvn clean` | arbol en README | Orden y limpieza (1) |

## Criterios de aceptacion C11 seleccionados para P02

| CA | Enunciado (C11) | Como se demuestra en P02 | Estado |
|---|---|---|---|
| CA01 | Desde una base inicial con datos sinteticos se completa el flujo principal y se observa el cambio persistido. | Semilla -> POST 25.5 y 38 -> historial y `psql` muestran las filas y la alerta. | VERIFICADO |
| CA02 | El caso invalido se rechaza con mensaje comprensible y sin alterar datos. | POST `abc`, vacio, `150`, sensor `999`, rol `ADMIN`, texto `ok` -> 400 con mensaje; conteos sin cambio. | VERIFICADO |
| CA05 | Otra persona puede preparar, ejecutar, probar y limpiar con el README. | README + `docker compose` + `verify-module.sh` + `cleanup.sh`. | VERIFICADO en la maquina de desarrollo; PENDIENTE por otro integrante |
| CA06 | Autoria, contribucion individual, limitaciones y cambios de alcance. | Commits por autor, `docs/evidencia/individual/`, `verification-report.md`, acta y F02. | VERIFICADO |
| CA03 / CA04 | API 2xx/4xx; evento IoT simulado. | Web 3.0 / 4.0. | NO APLICA en P02 |

## Errores esperados (entrada -> salida)

| Entrada | Salida esperada | Estado |
|---|---|---|
| POST `/lecturas` `sensorId=<temp>&valor=25.5` | 303 -> `?creada=N`; fila `manual`; sin alerta | VERIFICADO |
| POST `/lecturas` `valor=38` | 303 -> `?creada=N&alerta=ALTA`; fila en `lectura` y `alerta` | VERIFICADO |
| POST `/lecturas` `valor=abc` | 400 "El valor debe ser numerico" | VERIFICADO |
| POST `/lecturas` `sensorId=&valor=` | 400 con dos mensajes | VERIFICADO |
| POST `/lecturas` `valor=150` | 400 "fuera del rango fisico ... [-10.00, 60.00]" | VERIFICADO |
| POST `/lecturas` `sensorId=999` | 400 "El sensor seleccionado no existe." | VERIFICADO (curl manual, bitacora #6) |
| POST `/lecturas` `valor=24.555` | 400 "admite como maximo 2 decimales" | VERIFICADO (unitaria) / NO_VERIFICADO (HTTP) |
| POST `/lecturas` sensor `activo=false` | 400 "esta inactivo" | VERIFICADO (unitaria) / NO_VERIFICADO (HTTP) |
| POST `/anotaciones` rol OBSERVADOR, texto valido | 303 -> `?creada=N`; fila en `anotacion` | VERIFICADO |
| POST `/anotaciones` rol `ADMIN`, texto `ok` | 400 con dos mensajes | VERIFICADO |
| BD detenida | `/health` 503 `DOWN`; `/lecturas` pagina de error | VERIFICADO |
| Tomcat sin `DB_*` | `/health` 503 "Faltan variables" | NO_VERIFICADO |
