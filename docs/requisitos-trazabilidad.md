# Matriz de trazabilidad - RF del PRxx -> codigo -> prueba -> evidencia -> R02

| RF | Criterio de aceptacion (resumen) | Codigo que lo implementa | SQL | Prueba | Evidencia | Criterio R02 |
|---|---|---|---|---|---|---|
| RF-01 Catalogo de sensores | GET `/lecturas` 200 con tabla de sensores activos. | `LecturaServlet.doGet` -> `SensorRepository.findActivos` -> `WEB-INF/views/lecturas.jsp` (`#tabla-sensores`) | `01_schema.sql` (sensor, zona, huerto, tipo_sensor, umbral), `02_seed.sql` | `verify-module.sh` paso "GET inicial" | `txt/07_get_inicial.txt`, `img/01_get_inicial_lecturas.png` | Navegacion JSP/Servlet (2.5) |
| RF-02 Registrar lectura | POST valido -> 303 + fila en `lectura`. | `LecturaServlet.doPost` -> `LecturaService.registrar` -> `LecturaRepository.insertLectura` | `INSERT INTO lectura ... RETURNING id` | `verify-module.sh` "POST valido"; `LecturaValidatorTest.valorValidoEnRango` | `txt/08_post_valido.txt`, `img/02_formulario_lectura_valida.png`, `img/03_post_valido_resultado.png` | Navegacion (2.5) + Persistencia (2.5) |
| RF-03 Validar lectura | POST invalido -> 400 con mensajes, sin insertar. | `LecturaValidator` (parseSensorId, parseValor, parseObservacion, validarRangoFisico), `LecturaService` (sensor inexistente), `LecturaServlet` (status 400) | `CHECK` en `lectura`, `tipo_sensor` | `LecturaValidatorTest` (6 pruebas negativas); `verify-module.sh` pasos "POST invalido" x3 | `txt/09_*`, `txt/10_*`, `txt/11_*`, `img/04_*`, `img/05_*`, `img/06_*` | Navegacion (2.5) |
| RF-04 Consultar lecturas recientes | GET posterior muestra la nueva lectura. | `LecturaRepository.findRecientes` -> `lecturas.jsp` (`#tabla-lecturas`) | `SELECT ... ORDER BY registrado_en DESC LIMIT ?` | `verify-module.sh` "GET con persistencia" (cuenta filas antes/despues) | `txt/13_get_persistencia.txt`, `txt/15_postgres_despues.txt`, `txt/17_postgres_estado_final.txt` | Persistencia (2.5) |
| RF-05 Alerta automatica | Lectura fuera de umbral crea 1 alerta en la misma transaccion. | `LecturaValidator.nivelAlerta` / `mensajeAlerta`, `LecturaService.registrar` (commit/rollback), `LecturaRepository.insertAlerta` | `INSERT INTO alerta ...`; `alerta.lectura_id UNIQUE` | `LecturaValidatorTest.valorSobreUmbralGeneraAlertaAlta`, `valorBajoUmbralGeneraAlertaBaja`; `verify-module.sh` "POST 38 C" | `txt/12_post_valido_con_alerta.txt`, `img/07_post_valido_con_alerta.png` | Persistencia (2.5) |
| RF-06 Consultar alertas | GET `/alertas` 200 con la alerta. | `AlertaServlet` -> `LecturaRepository.findAlertas` -> `alertas.jsp` | `SELECT ... FROM alerta JOIN ...` | `verify-module.sh` "GET alertas" | `txt/14_get_alertas.txt`, `img/08_get_alertas.png` | Navegacion (2.5) |
| RF-07 Ruta de salud | GET `/health` 200 `db=UP`; 503 si no hay BD. | `HealthServlet`, `DbConfig` | `SELECT version(), count(*)` | `verify-module.sh` "Ruta de salud" | `txt/06_health.txt`, `img/09_health_json.png` | Despliegue en Tomcat (2) + Persistencia (2.5) |
| Despliegue | WAR `web1.war` desplegado en Tomcat 9.0.115 con variables externas. | `pom.xml` (finalName web1), `web.xml`, `scripts/setenv.*.example`, `AppContextListener` | - | `verify-module.sh` "Despliegue en Tomcat 9" | `txt/01_build.txt`, `txt/03_war_contenido.txt`, `txt/05_tomcat_log.txt` | Despliegue en Tomcat (2) |
| Documentacion | README, acta, modelo, bitacora, indice de evidencia. | `README.md`, `docs/*.md` | `sql/*.sql` | Revision cruzada del equipo | `docs/evidencia/INDICE.md` | README, capturas y repositorio (2) |
| Orden tecnico | Estructura Maven estandar, nombres consistentes, sin archivos innecesarios. | `.gitignore`, paquetes `config/model/repository/service/web` | - | `git status` limpio tras `mvn clean` | Arbol del repositorio en README | Orden y limpieza (1) |

## Errores esperados (entrada -> salida)

| Entrada (POST /lecturas) | Salida esperada | Estado |
|---|---|---|
| `sensorId=<temp>&valor=25.5` | 303 -> `/lecturas?creada=N`; fila en `lectura`; sin alerta | VERIFICADO |
| `sensorId=<temp>&valor=38` | 303 -> `/lecturas?creada=N&alerta=ALTA`; fila en `lectura` y en `alerta` | VERIFICADO |
| `sensorId=<temp>&valor=abc` | 400 "El valor debe ser numerico" | VERIFICADO |
| `sensorId=&valor=` | 400 "Debe seleccionar un sensor." + "El valor de la lectura es obligatorio." | VERIFICADO |
| `sensorId=<temp>&valor=150` | 400 "fuera del rango fisico permitido ... [-10.00, 60.00]" | VERIFICADO |
| `sensorId=999&valor=20` | 400 "El sensor seleccionado no existe." | VERIFICADO (curl manual, bitacora) |
| `valor=24.555` | 400 "admite como maximo 2 decimales" | VERIFICADO (unitaria) / NO_VERIFICADO por HTTP |
| sensor con `activo = FALSE` | 400 "esta inactivo" | VERIFICADO (unitaria) / NO_VERIFICADO por HTTP (la semilla no tiene sensores inactivos) |
| Tomcat sin `DB_*` | `/health` 503 `{"status":"DOWN",...}`; `/lecturas` pagina de error | VERIFICADO (bitacora 2026-09-11) |
