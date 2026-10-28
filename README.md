# PR09 - Monitoreo de huerto o ambiente

Proyecto integrador del equipo **DSW-E01** (Desarrollo de Sistemas Web, DSW-19559). Un huerto escolar registra
lecturas de sensores (temperatura, humedad, luz) con su instante y procedencia, avisa cuando una lectura sale del
umbral operativo y permite anotaciones por rol. Todos los datos son ficticios.

| Incremento | Estado | Tecnologia | WAR / contexto |
|---|---|---|---|
| **P05 (actual)** - integracion Web 3.0 | `verify-module.sh M05` -> VERIFICADO el 2026-10-21 (64 casos del contrato, 23 en navegador, 37 pruebas de la API, 9 del cliente) | Las 13 operaciones del contrato 0.5.0 implementadas: zonas, alertas con cambio de estado (`PATCH`), anotaciones; migracion `sql/04` | mismos puertos que P04; `./scripts/demo_p05.sh` levanta todo |
| P04 - Web 3.0 | `verify-module.sh M04` -> VERIFICADO el 2026-09-29 y el 2026-10-09 (30 casos del contrato, 12 en navegador, 16 pruebas de la API, 5 del cliente) | Angular 16.2.12 + API REST Spring Boot 2.7.18 (Java 11) + PostgreSQL 16; contrato OpenAPI 3.0.3 | `frontend-angular/` en `http://localhost:4200`, `api-spring/` en `http://localhost:8081` |
| P03 - Web 2.0 | `verify-module.sh M03` -> VERIFICADO el 2026-09-25 (26 casos en navegador, 21 pruebas unitarias) | JSF 2.3 (Mojarra 2.3.9) + PrimeFaces 12 + CDI (Weld 3.1.9) sobre Tomcat 9.0.115; JDBC a PostgreSQL 16 | `web2.war` -> `http://localhost:8080/web2/` |
| P02 - Web 1.0 | VERIFICADO el 2026-09-11; evidencia conservada en `docs/evidencia/` y `docs/entrega/` | JSP/Servlet 4.0 sobre Tomcat 9; mismo modelo y misma base | `web1.war` (historial de git hasta `832f377`) |

Modelo de datos (sin cambios desde P02): `zona, variable, sensor, umbral, lectura, alerta, anotacion` (`docs/modelo-datos.md`).
Roles funcionales del PR09: **observador** (captura lecturas y anota), **responsable** y **coordinacion** (consultan y anotan).

## 1. Requisitos

| Componente | Version | Para que |
|---|---|---|
| JDK | 11 | compilar y ejecutar Tomcat |
| Maven | 3.9.9 | construir `web2.war` y correr las pruebas |
| Tomcat | 9.0.115 (Servlet 4.0, `javax`) | contenedor web; Faces y CDI van dentro del WAR |
| PostgreSQL | 16 (Docker `postgres:16`) o instalacion local 11+ | base de datos |
| Docker | cualquiera reciente | levantar PostgreSQL con `docker compose` (opcional si ya tienes PostgreSQL) |
| Git Bash o bash, `curl`, `unzip` | - | scripts de verificacion |
| Python 3.11 + Playwright | para `verify-module.sh M03` y `pruebas_jsf.py` | recorrido de aceptacion en navegador real |
| Node.js | 18.20.8 (npm 10) | P04: compilar y servir el cliente Angular |
| Angular CLI | 16.2.x (se instala con `npm ci`, no hace falta global) | P04 |
| Python: `pyyaml`, `openapi-spec-validator`, `jsonschema` | - | P04: validar el contrato y las respuestas |

## 2. Estructura

```
dsw-p02-monitoreo-huerto/
├── pom.xml                        # WAR web2: Mojarra 2.3.9, PrimeFaces 12, Weld 3.1.9, jaxb-api, driver PostgreSQL, JUnit 5
├── api-spring/                    # P04: API REST Spring Boot 2.7.18 (Java 11); paquetes config, seguridad, error, salud, sensores, lecturas
├── frontend-angular/              # P04: cliente Angular 16.2.12; src/app/core, acceso, lecturas; proxy.conf.json
├── docker/docker-compose.yml      # PostgreSQL 16 en localhost:5436; ejecuta sql/01 y 02 al crear el volumen
├── sql/                           # 01_schema, 02_seed, 03_consultas_verificacion, 99_cleanup
├── scripts/
│   ├── verify-module.sh           # M02, M03 o M04 (M04 delega en verify-m04.sh)
│   ├── verify-m04.sh, pruebas_api.py, recorrido_angular.py, prueba_base_detenida.sh, diagramas_p04.py   # P04
│   ├── redeploy-tomcat.sh         # reinicio limpio de Tomcat (Windows bloquea los jars desplegados)
│   ├── pruebas_jsf.py             # recorrido de aceptacion P03 con Playwright (capturas + conteos en psql)
│   ├── cleanup.sh                 # borra datos de prueba; --all detiene Tomcat y elimina el contenedor
│   ├── setenv.bat.example / setenv.sh.example   # variables DB_* para Tomcat
│   └── capturas.py, capturas_psql.ps1, generar_entrega.py, diagrama_er.py, anonimizar_evidencia.py  # evidencia P02
├── docs/
│   ├── p03/                       # arquitectura, trazabilidad-r03, pruebas-aceptacion, verificacion, evidencia/ (INDICE, img, txt)
│   ├── evidencia/, entrega/       # P02 (intactos)
│   ├── acta-proyecto.md, F02-seleccion-proyecto.md, modelo-datos.md, requisitos-trazabilidad.md
│   └── bitacora.md, verification-report.md
└── src/
    ├── main/java/mx/uv/dsw/huerto/
    │   ├── config/      DbConfig (DB_URL/DB_USER/DB_PASSWORD desde el entorno), AppContextListener
    │   ├── model/       Zona, Sensor, Lectura, Alerta, Anotacion, Usuario
    │   ├── repository/  SensorRepository, LecturaRepository, AnotacionRepository (JDBC parametrizado)
    │   ├── service/     LecturaValidator, LecturaService (transaccion), AnotacionValidator, AnotacionService, AuthService, Permisos
    │   └── web/         SesionBean, LecturaBean, AlertaBean, AnotacionBean, AutenticacionFilter, HealthServlet, Mensajes
    ├── main/resources/usuarios.properties        # usuarios ficticios con hash PBKDF2 (no hay contrasenas en claro)
    ├── main/webapp/
    │   ├── login.xhtml, index.xhtml, expirada.xhtml, error.xhtml
    │   ├── app/lecturas.xhtml, app/alertas.xhtml, app/anotaciones.xhtml
    │   ├── WEB-INF/templates/plantilla.xhtml, web.xml, faces-config.xml, beans.xml
    │   └── resources/css/huerto.css
    └── test/java/mx/uv/dsw/huerto/service/       # 21 pruebas JUnit
```

Capas: Facelets y PrimeFaces presentan; los beans coordinan; los servicios validan y abren la transaccion; los
repositorios concentran el SQL. Ninguna vista tiene SQL ni reglas (`docs/p03/arquitectura.md`).

## 3. Configuracion y despliegue (P03)

Los comandos estan probados en Windows 11 con Git Bash. Donde PowerShell difiere, se indica.

### 3.1 Base de datos

```bash
docker compose -f docker/docker-compose.yml up -d        # PostgreSQL 16 en localhost:5436
docker exec -i dsw-p02-huerto-db psql -U huerto_app -d huerto_db < sql/03_consultas_verificacion.sql
```

Credenciales de laboratorio: base `huerto_db`, usuario `huerto_app`, contrasena `huerto_dev` (cambiables con
`docker/.env`, ver `.env.example`). Si ya tienes PostgreSQL instalado, crea el rol y la base y ejecuta `sql/01_schema.sql`
y `sql/02_seed.sql` con `psql`; ajusta el puerto en `DB_URL`. El esquema no cambio entre P02 y P03: una base de P02 sirve
tal cual. No borres el volumen para resolver problemas de configuracion; el script de limpieza solo toca datos de prueba.

### 3.2 Variables de entorno de Tomcat

La aplicacion lee `DB_URL`, `DB_USER` y `DB_PASSWORD` de propiedades de la JVM o del entorno. Tomcat las toma de
`bin/setenv.bat` (Windows) o `bin/setenv.sh` (Linux/macOS), que no se versionan:

```bash
cp scripts/setenv.bat.example "$CATALINA_HOME/bin/setenv.bat"      # Windows
cp scripts/setenv.sh.example  "$CATALINA_HOME/bin/setenv.sh" && chmod +x "$CATALINA_HOME/bin/setenv.sh"   # Linux/macOS
```

Contenido: `DB_URL=jdbc:postgresql://localhost:5436/huerto_db`, `DB_USER=huerto_app`, `DB_PASSWORD=huerto_dev`.
Un archivo `.env` no lo lee Java; solo lo usa `docker compose`.

### 3.3 Compilar

```bash
mvn clean package            # 21 pruebas unitarias; genera target/web2.war
```

### 3.4 Desplegar

Primera vez (Tomcat detenido o sin `web2` desplegado):

```bash
cp target/web2.war "$CATALINA_HOME/webapps/"
"$CATALINA_HOME/bin/startup.sh"          # Windows: %CATALINA_HOME%\bin\startup.bat
```

Redespliegue: en Windows Tomcat bloquea los jars de `WEB-INF/lib` y el autodespliegue puede conservar clases viejas.
Usa el script, que detiene Tomcat, borra el despliegue anterior y vuelve a arrancar:

```bash
export CATALINA_HOME=/c/Tools/apache-tomcat-9.0.115       # tu ruta
./scripts/redeploy-tomcat.sh target/web2.war web2
```

### 3.5 Entrar

| URL | Que es |
|---|---|
| `http://localhost:8080/web2/` | Redirige al acceso o al flujo principal segun haya sesion |
| `http://localhost:8080/web2/login.xhtml` | Inicio de sesion |
| `http://localhost:8080/web2/app/lecturas.xhtml` | Flujo principal: sensores, captura de lectura, historial con filtros y paginacion |
| `http://localhost:8080/web2/app/alertas.xhtml` | Alertas generadas |
| `http://localhost:8080/web2/app/anotaciones.xhtml` | Zonas y anotaciones (firmadas con el rol de la sesion) |
| `http://localhost:8080/web2/health` | JSON de salud; 503 si PostgreSQL no responde |

Usuarios de prueba (ficticios; el archivo `usuarios.properties` solo guarda hashes con sal):

| Usuario | Contrasena | Rol | Puede |
|---|---|---|---|
| `observador` | `Observador#2026` | OBSERVADOR | registrar lecturas, anotar, consultar |
| `responsable` | `Responsable#2026` | RESPONSABLE | anotar, consultar |
| `coordinacion` | `Coordinacion#2026` | COORDINACION | anotar, consultar |

La sesion caduca a los 20 minutos de inactividad. "Salir" la invalida. Las vistas de `/app` sin sesion redirigen al acceso,
tambien en peticiones AJAX.

### 3.6 Detener sin perder datos

`"$CATALINA_HOME/bin/shutdown.sh"` (o `shutdown.bat`) y `docker compose -f docker/docker-compose.yml stop`. El volumen de
PostgreSQL conserva los datos. `./scripts/cleanup.sh` borra solo lecturas `manual` y anotaciones que empiezan con
`[prueba]`; `./scripts/cleanup.sh --all` ademas retira `web1`/`web2` de Tomcat y elimina el contenedor **y su volumen**
(revisa el script antes de usar esa opcion).

## 4. Datos de prueba y casos

Sensor `SEN-A-TEMP-01` (Cama A): rango fisico [-10, 60] C, umbral operativo [15, 32] C.

| Entrada | Resultado |
|---|---|
| 25.5 | valida, sin alerta |
| 38 / 10 | valida, alerta ALTA / BAJA en la misma transaccion |
| 15 / 32 | validas, sin alerta (limites) |
| vacio, `abc` | rechazada, se conserva lo capturado |
| 150 | rechazada por rango fisico; PostgreSQL no cambia |
| 24.555 | rechazada por decimales; no se redondea |

Anotaciones: de 3 a 300 caracteres; el rol sale de la sesion; una referencia a lectura inexistente se rechaza.

## 5. Verificacion reproducible

```bash
export CATALINA_HOME=/c/Tools/apache-tomcat-9.0.115
python -m pip install playwright && python -m playwright install chromium   # una vez
./scripts/verify-module.sh M03
./scripts/cleanup.sh
```

Compila, corre las pruebas unitarias, inspecciona el WAR, consulta PostgreSQL, redespliega, espera `/health`, comprueba
la pagina de acceso y la proteccion de `/app`, ejecuta el recorrido en navegador (`pruebas_jsf.py`: 26 casos con conteos
antes/despues en la base) y vuelve a consultar PostgreSQL. Deja todo en `docs/p03/evidencia/` (rutas anonimizadas) y termina
con `RESULTADO: VERIFICADO` o `NO_VERIFICADO`. Variables opcionales: `BASE_URL`, `PSQL_CMD`, `SKIP_DEPLOY=1`;
`SKIP_DB_DOWN=1` y `SKIP_TX_TEST=1` omiten los dos casos que tocan la infraestructura.

Sin Python/Playwright el recorrido queda PENDIENTE y hay que repetirlo a mano con los casos de
`docs/p03/pruebas-aceptacion.md`. `./scripts/verify-module.sh M02` sigue disponible para el incremento anterior.

## 6. Decisiones que conviene poder explicar

- **Por que Weld**: JSF 2.3 exige CDI para `@Named`/`@ViewScoped`; Tomcat no lo trae. Weld Servlet se registra solo e
  inyecta tambien en filtros.
- **Por que `p:inputText` y no `p:inputNumber` para el valor**: un convertidor numerico redondea 24.555; la regla del
  huerto es rechazarlo, y `LecturaValidator` lo hace con `BigDecimal`.
- **Por que `f:viewAction` en cada vista**: crea el bean antes del render; si no, el mensaje "base de datos no disponible"
  se generaba despues de que `p:messages` ya se habia pintado.
- **Por que el filtro responde con `partial-response`**: una redireccion HTTP normal rompe la respuesta parcial de JSF; asi el
  navegador va al acceso tambien cuando la sesion caduca a mitad de un envio AJAX.
- **Por que no hay tabla de usuarios**: el modelo aprobado tiene siete entidades; los usuarios ficticios viven en
  `usuarios.properties` con hash PBKDF2. Migrarlos a una tabla es el siguiente paso natural si se aprueba.
- **Por que `jaxb-api`**: Mojarra 2.3.9 usa `DatatypeConverter` al cifrar el *flash* en cada `faces-redirect`; el JDK 11 no lo trae.

Mas detalle en `docs/p03/arquitectura.md`; trazabilidad en `docs/p03/trazabilidad-r03.md`; estados de prueba en
`docs/p03/pruebas-aceptacion.md` y `docs/p03/verificacion.md`; fallos encontrados y corregidos en `docs/bitacora.md`.

## 7. P04: arquitectura Web 3.0 (Angular + API Spring Boot)

P04 separa la aplicacion en un cliente Angular y una API REST que hablan JSON. La base, el modelo, los tres roles y
el flujo principal son los mismos. P02 y P03 siguen en el repositorio y no se tocaron.

| Documento | Contenido |
|---|---|
| `docs/p04/arquitectura.md` | Componentes, responsabilidades, decisiones con alternativas, seguridad, despliegue |
| `docs/p04/openapi.yaml` | Contrato de la API (OpenAPI 3.0.3) |
| `docs/p04/endpoints.md` | Catalogo de endpoints con entradas, salidas y errores |
| `docs/p04/modelo-datos.md` | Modelo PostgreSQL y su relacion con los recursos de la API |
| `docs/p04/trazabilidad-rf.md` | RF -> componente -> prueba |
| `docs/p04/verificacion.md` | Estados VERIFICADO / NO_VERIFICADO / PENDIENTE, fallos y limitaciones |
| `docs/p04/evidencia/INDICE.md` | Evidencia frente a cada criterio de R04 |
| `docs/p04/individual/` | Registro individual de cada integrante |

### 7.1 Preparar

```bash
docker compose -f docker/docker-compose.yml up -d     # la misma base de P02 y P03
cd frontend-angular && npm ci && cd ..                # dependencias del cliente (una vez)
python -m pip install pyyaml openapi-spec-validator jsonschema playwright
python -m playwright install chromium                 # para las pruebas en navegador
```

### 7.2 API (terminal 1)

```bash
export DB_URL=jdbc:postgresql://localhost:5436/huerto_db
export DB_USER=huerto_app
export DB_PASSWORD=huerto_dev
# opcionales: JWT_SECRET (32 caracteres o mas), CORS_ORIGIN (http://localhost:4200), PORT (8081)
mvn -f api-spring/pom.xml clean package               # 16 pruebas; genera api-spring/target/api-spring.jar
java -jar api-spring/target/api-spring.jar
```

En PowerShell las variables se definen con `$env:DB_URL = "..."`. Sin las tres variables `DB_*` la API no arranca.
Sin `JWT_SECRET` se genera un secreto distinto en cada arranque y los tokens anteriores dejan de valer.

### 7.3 Cliente (terminal 2)

```bash
cd frontend-angular
npx ng serve                                          # http://localhost:4200; reenvia /api a la API
```

| URL | Que es |
|---|---|
| `http://localhost:4200/` | Cliente Angular: acceso y flujo principal |
| `http://localhost:8081/api/health` | Salud de la API; 503 si PostgreSQL no responde |
| `http://localhost:8081/swagger-ui.html` | Operaciones implementadas, generadas desde el codigo |
| `http://localhost:8081/v3/api-docs` | OpenAPI generado (el de referencia es `docs/p04/openapi.yaml`) |

Los usuarios de prueba son los de la seccion 3.5. El token dura 30 minutos.

### 7.4 Probar la API sin el cliente

```bash
TOKEN=$(curl -s -X POST http://localhost:8081/api/auth/login -H 'Content-Type: application/json'   -d '{"usuario":"observador","contrasena":"Observador#2026"}' | python -c "import sys,json; print(json.load(sys.stdin)['token'])")
curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8081/api/sensores"
curl -s -i -X POST http://localhost:8081/api/lecturas -H "Authorization: Bearer $TOKEN"   -H 'Content-Type: application/json' -d '{"sensorId":2,"valor":25.5,"observacion":"[prueba] manual"}'
```

### 7.5 Verificar y limpiar

```bash
./scripts/verify-module.sh M04        # con la API y el cliente detenidos: el script los arranca y los apaga
./scripts/prueba_base_detenida.sh     # opcional: detiene y vuelve a arrancar el contenedor de la base
./scripts/cleanup.sh                  # retira lecturas de prueba y carpetas generadas
```

`verify-module.sh M04` compila la API y el cliente, corre sus pruebas, valida `openapi.yaml`, arranca la API, ejecuta
los 30 casos del contrato (`scripts/pruebas_api.py`), sirve el cliente y hace el recorrido en navegador
(`scripts/recorrido_angular.py`), consulta PostgreSQL y apaga todo. Deja la evidencia en `docs/p04/evidencia/`.
Variables opcionales: `API_PORT`, `WEB_PORT`, `PSQL_CMD`, `CHROME_BIN`, `SKIP_FRONT=1`, `SKIP_NAVEGADOR=1`.

Implementado: salud, acceso, sensores y lecturas. Definido en el contrato y pendiente de implementar: zonas, alertas
y anotaciones.

## 8. P05: integracion completa (zonas, alertas con cambio de estado, anotaciones)

P05 completa lo que P04 dejo solo en el contrato. Las 13 operaciones de `docs/p04/openapi.yaml` (version 0.5.0)
estan implementadas, el cliente Angular tiene las vistas de alertas y anotaciones, y la API ofrece un cambio de
estado: el responsable del huerto marca una alerta como atendida o la reabre (`PATCH /api/alertas/{id}`).

| Documento | Contenido |
|---|---|
| `docs/p05/arquitectura.md` | Que se agrego, el cambio de estado, decisiones D10 a D17 con alternativas, seguridad, despliegue |
| `docs/p05/modelo-datos.md` | Columnas nuevas de `alerta`, migracion, estados, reglas |
| `docs/p05/endpoints.md` | Catalogo completo de las 13 operaciones con ejemplos reales |
| `docs/p05/trazabilidad-r05.md` | RF -> componente -> prueba -> evidencia -> criterio R05 |
| `docs/p05/verificacion.md` | Estados VERIFICADO / NO_VERIFICADO / PENDIENTE, fallos encontrados y limitaciones |
| `docs/p05/evidencia/INDICE.md` | Evidencia frente a cada criterio de R05 |

### 8.1 Si ya tienes la base de P04: aplica la migracion

```bash
docker exec -i dsw-p02-huerto-db psql -U huerto_app -d huerto_db -v ON_ERROR_STOP=1 < sql/04_p05_atencion_alerta.sql
```

Agrega `atendida_en` y `atendida_por` a `alerta` sin tocar filas; se puede correr mas de una vez. Una base creada
desde cero con `docker compose` ya las trae (`sql/01_schema.sql`). Nada se borra.

### 8.2 Ejecutar

Igual que en P04 (seccion 7.2 y 7.3): la API en el 8081 con las variables `DB_*` y el cliente con `npx ng serve` en
el 4200. Rutas del cliente: `/lecturas`, `/alertas`, `/anotaciones`. Quien puede que:

| Operacion | OBSERVADOR | RESPONSABLE | COORDINACION |
|---|---|---|---|
| Consultar zonas, sensores, lecturas, alertas y anotaciones | si | si | si |
| Registrar lectura (`POST /api/lecturas`) | si | no (403) | no (403) |
| Atender o reabrir una alerta (`PATCH /api/alertas/{id}`) | no (403) | si | no (403) |
| Registrar anotacion (`POST /api/anotaciones`) | si | si | si |

### 8.3 Probar el cambio de estado sin el cliente

```bash
TOKEN=$(curl -s -X POST http://localhost:8081/api/auth/login -H 'Content-Type: application/json'   -d '{"usuario":"responsable","contrasena":"Responsable#2026"}' | python -c "import sys,json; print(json.load(sys.stdin)['token'])")
curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8081/api/alertas?atendida=false&tamano=3"
curl -s -i -X PATCH http://localhost:8081/api/alertas/1 -H "Authorization: Bearer $TOKEN"   -H 'Content-Type: application/json' -d '{"atendida":true}'        # 200; repetirlo responde 409
curl -s -i -X POST http://localhost:8081/api/anotaciones -H "Authorization: Bearer $TOKEN"   -H 'Content-Type: application/json' -d '{"zonaId":1,"texto":"[prueba] riego manual por la tarde"}'   # 201
```

### 8.4 Verificar y limpiar

```bash
./scripts/verify-module.sh M05        # con la API y el cliente detenidos: el script los arranca y los apaga
./scripts/prueba_base_detenida.sh     # opcional: detiene y vuelve a arrancar el contenedor de la base
./scripts/cleanup.sh                  # retira lecturas, alertas y anotaciones de prueba y carpetas generadas
```

`verify-module.sh M05` hace lo mismo que `M04` (compila la API y el cliente, corre sus pruebas, valida el contrato,
arranca la API, ejecuta `pruebas_api.py`, sirve el cliente y hace el recorrido en navegador con
`recorrido_angular.py`, consulta PostgreSQL y apaga todo) mas la migracion de `sql/04`, y deja la evidencia en
`docs/p05/evidencia/`. La guia de P05 pide `verify-module.sh M04`; ese modulo sigue funcionando y deja su evidencia en
`docs/p04/evidencia/`, pero la de P05 se genera con `M05` para no mezclar incrementos.

## 9. Todo en Docker: PostgreSQL, API y cliente detras de nginx

Cada pieza corre en su contenedor sobre la red Docker `huerto`, y nginx es la unica entrada: sirve el cliente
Angular ya compilado y reenvia `/api` (y la documentacion de springdoc) al contenedor de la API. La API y la base
no exponen puertos al equipo (la base conserva el 5436 solo para `psql` y los scripts de verificacion).

| Contenedor | Imagen | Que hace | Puerto en el equipo |
|---|---|---|---|
| `dsw-p02-huerto-db` | `postgres:16` | la misma base de P02 a P05, mismo volumen `pgdata` | 5436 (solo herramientas) |
| `dsw-p02-huerto-api` | `huerto-api:0.5.0` (`api-spring/Dockerfile`: Maven -> JRE 11 alpine, usuario sin privilegios) | Spring Boot en el 8081, solo dentro de la red | ninguno |
| `dsw-p02-huerto-web` | `huerto-web:0.5.0` (`frontend-angular/Dockerfile`: Node 18 compila -> `nginx:1.27-alpine`) | nginx con `frontend-angular/nginx.conf`: `/` estaticos, `/api/` -> `api:8081` | `WEB_PORT` (80) |

```bash
docker compose -f docker/docker-compose.yml --profile app up -d --build   # construye las dos imagenes y levanta los tres
docker compose -f docker/docker-compose.yml --profile app ps              # estado y salud de cada contenedor
docker compose -f docker/docker-compose.yml --profile app logs -f api     # registro de la API
docker compose -f docker/docker-compose.yml --profile app down            # detiene todo; el volumen de datos se conserva
```

Entrar en `http://localhost` (o `http://localhost:WEB_PORT` si se cambio en `docker/.env`); Swagger en
`http://localhost/swagger-ui.html`. Como el navegador solo habla con nginx, cliente y API comparten origen y no hay
peticiones entre origenes. El secreto del token se fija con `JWT_SECRET` en `docker/.env`; si se deja vacio la API
genera uno al arrancar. Los arranques dependen de la salud: la API espera a que PostgreSQL acepte conexiones y nginx
espera a que `/api/health` responda 200.

Sin `--profile app`, `docker compose up -d` levanta solo la base, como en los incrementos anteriores, asi que
`verify-module.sh`, `demo_p05.sh` y los scripts siguen funcionando igual. Para probar el contrato contra la pila en
Docker: `API_URL=http://localhost ORIGEN_WEB=http://localhost python scripts/pruebas_api.py`.

## 10. Equipo

| Responsabilidad | Integrante | GitHub |
|---|---|---|
| Desarrollo web | Juan Pablo Kuri Ricardez | `juankuri` |
| Datos (PostgreSQL) | Pedro Garcia Padilla | `pedro-gar-pad` |
| Evidencia y documentacion | Alejandro Pacheco Luna | `zywoxxx` |
| Evidencia y documentacion | Ariadna Trejo Alvarez | `ariadna-19` |
