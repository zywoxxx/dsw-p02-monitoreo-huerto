# PRxx - Monitoreo de huerto o ambiente - Incremento P02 (web1-jsp)

Aplicacion Web 1.0 con **JSP 2.3 + Servlet 4.0 (javax)**, desplegada como `web1.war` en **Tomcat 9.0.115**, con
persistencia en **PostgreSQL 16** mediante **JDBC parametrizado**. Primer incremento del proyecto integrador
PRxx *Monitoreo de huerto o ambiente* (Desarrollo de Sistemas Web, DSW-19559, actividad P02, rubrica R02).

| | |
|---|---|
| Flujo principal | Registrar una lectura de sensor, validarla, persistirla y generar alerta si sale del umbral. |
| RF del incremento | RF-01 a RF-07 (ver `docs/acta-proyecto.md` y `docs/requisitos-trazabilidad.md`). |
| Modelo | 7 entidades: huerto, zona, tipo_sensor, sensor, umbral, lectura, alerta (`docs/modelo-datos.md`). |
| Estado | `scripts/verify-module.sh M02` -> **15/15 VERIFICADO** el 2026-09-11 (`docs/verification-report.md`). |
| Equipo | 3 roles (desarrollo web, datos, evidencia); ver `docs/acta-proyecto.md`. |

## 1. Requisitos

| Componente | Version confirmada en M02 | Uso |
|---|---|---|
| Java JDK | 11 | compilar y ejecutar Tomcat |
| Apache Maven | 3.9.9 | construir `web1.war` y correr pruebas unitarias |
| Apache Tomcat | 9.0.115 (Servlet 4.0.1, JSP 2.3, `javax.*`) | contenedor web |
| PostgreSQL | 16 (Docker `postgres:16`) o instalacion local 11+ | base de datos |
| Docker Desktop / Docker Engine | cualquiera reciente | levantar PostgreSQL con `docker compose` (opcional si ya tienes PostgreSQL) |
| Git Bash (Windows) o bash (Linux/macOS), `curl`, `unzip` | - | ejecutar `scripts/*.sh` |
| Python 3.11 + Playwright | opcional | regenerar capturas (`scripts/capturas.py`) y anonimizar evidencia |

No se usan frameworks ni servicios externos. Unica biblioteca de vista: JSTL 1.2. Driver: `org.postgresql:postgresql:42.7.2`.

## 2. Estructura del repositorio

```
dsw-p02-monitoreo-huerto/
├── README.md                     # esta guia
├── pom.xml                       # WAR web1, Java 11, JSTL, driver PostgreSQL, JUnit 5
├── .gitignore                    # excluye target/, setenv.*, .env
├── docker/
│   ├── docker-compose.yml        # PostgreSQL 16 local (puerto 5436) que ejecuta sql/01 y 02 al crearse
│   └── .env.example              # variables opcionales del contenedor
├── sql/
│   ├── 01_schema.sql             # 7 tablas con claves, CHECK e indices
│   ├── 02_seed.sql               # datos ficticios: 1 huerto, 2 zonas, 4 tipos, 5 sensores, 5 umbrales, 2 lecturas
│   ├── 03_consultas_verificacion.sql  # evidencia de conexion, tablas, conteos, ultimas lecturas y alertas
│   └── 99_cleanup.sql            # borra solo lecturas/alertas de pruebas (origen = manual)
├── scripts/
│   ├── verify-module.sh          # verificacion reproducible completa (build, WAR, BD, Tomcat, HTTP)
│   ├── cleanup.sh                # limpieza local (--all detiene Tomcat y elimina el contenedor)
│   ├── capturas.py               # capturas del flujo con navegador real (Playwright)
│   ├── anonimizar_evidencia.py   # sustituye rutas locales en docs/evidencia/txt
│   ├── setenv.bat.example        # variables DB_* para Tomcat en Windows
│   └── setenv.sh.example         # variables DB_* para Tomcat en Linux/macOS
├── docs/
│   ├── acta-proyecto.md          # acta breve: equipo/roles, alcance, flujo principal, RF y criterios
│   ├── modelo-datos.md           # diagrama ER (mermaid) y diccionario
│   ├── requisitos-trazabilidad.md# RF -> codigo -> SQL -> prueba -> evidencia -> R02
│   ├── bitacora.md               # fecha, comando, resultado, interpretacion, siguiente accion
│   ├── verification-report.md    # VERIFICADO / NO_VERIFICADO / PENDIENTE por prueba
│   └── evidencia/
│       ├── INDICE.md             # cada evidencia relacionada con un criterio de R02
│       ├── img/                  # 10 capturas del flujo, validaciones y despliegue
│       ├── txt/                  # salidas de build, WAR, Tomcat, psql y curl (rutas anonimizadas)
│       └── individual/           # P02_APELLIDO_NOMBRE.md por integrante
└── src/
    ├── main/java/mx/uv/dsw/huerto/
    │   ├── config/      DbConfig (variables de entorno), AppContextListener
    │   ├── model/       Sensor, Lectura, Alerta
    │   ├── repository/  SensorRepository, LecturaRepository (JDBC parametrizado)
    │   ├── service/     LecturaValidator, LecturaService (transaccion), ValidacionException
    │   └── web/         LecturaServlet (/lecturas), AlertaServlet (/alertas), HealthServlet (/health)
    ├── main/webapp/
    │   ├── index.jsp                 # redirige a /lecturas
    │   ├── css/estilos.css
    │   └── WEB-INF/web.xml, WEB-INF/views/{lecturas,alertas,error}.jsp
    └── test/java/mx/uv/dsw/huerto/service/LecturaValidatorTest.java   # 10 pruebas (positivas y negativas)
```

Capas (M02): **la JSP presenta**, **el Servlet coordina**, **el Service valida y abre la transaccion**, **el Repository
concentra el SQL parametrizado**. Ninguna vista contiene SQL ni credenciales.

## 3. Instalacion y despliegue

### 3.1 Clonar

```bash
git clone https://github.com/zywoxxx/dsw-p02-monitoreo-huerto.git
cd dsw-p02-monitoreo-huerto
```

### 3.2 Base de datos PostgreSQL 16

**Opcion A - Docker (recomendada, reproducible):**

```bash
docker compose -f docker/docker-compose.yml up -d
docker exec -i dsw-p02-huerto-db psql -U huerto_app -d huerto_db < sql/03_consultas_verificacion.sql
```

La primera vez el contenedor ejecuta `sql/01_schema.sql` y `sql/02_seed.sql`. Queda escuchando en `localhost:5436`,
base `huerto_db`, usuario `huerto_app`, contrasena `huerto_dev` (**valores ficticios de laboratorio**; cambialos con
`docker/.env`, ver `.env.example`).

**Opcion B - PostgreSQL ya instalado (11 o superior):**

```bash
psql -U postgres -c "CREATE USER huerto_app WITH PASSWORD 'huerto_dev';"
psql -U postgres -c "CREATE DATABASE huerto_db OWNER huerto_app;"
psql -U huerto_app -d huerto_db -f sql/01_schema.sql
psql -U huerto_app -d huerto_db -f sql/02_seed.sql
```

Ajusta despues `DB_URL` al puerto de tu servidor (por defecto 5432).

### 3.3 Variables de entorno en Tomcat (sin secretos en el codigo)

La aplicacion lee `DB_URL`, `DB_USER` y `DB_PASSWORD` desde propiedades de la JVM (`-DDB_URL=...`) o variables de
entorno. En Tomcat se definen en `bin/setenv.bat` (Windows) o `bin/setenv.sh` (Linux/macOS), que **no se versionan**:

```bash
# Windows (Git Bash)
cp scripts/setenv.bat.example "$CATALINA_HOME/bin/setenv.bat"
# Linux/macOS
cp scripts/setenv.sh.example "$CATALINA_HOME/bin/setenv.sh" && chmod +x "$CATALINA_HOME/bin/setenv.sh"
```

Contenido de ejemplo:

```
DB_URL=jdbc:postgresql://localhost:5436/huerto_db
DB_USER=huerto_app
DB_PASSWORD=huerto_dev
```

### 3.4 Compilar y empaquetar

```bash
mvn clean package
```

Salida esperada: `Tests run: 10, Failures: 0`, `BUILD SUCCESS` y `target/web1.war`.
Inspeccion del WAR: `unzip -l target/web1.war` (debe listar `WEB-INF/classes/mx/uv/dsw/huerto/...`, `WEB-INF/lib/postgresql-42.7.2.jar`, `WEB-INF/lib/jstl-1.2.jar`, `WEB-INF/web.xml`, `WEB-INF/views/*.jsp`).

### 3.5 Desplegar en Tomcat 9

```bash
cp target/web1.war "$CATALINA_HOME/webapps/"
"$CATALINA_HOME/bin/startup.sh"        # Windows: %CATALINA_HOME%\bin\startup.bat
```

Comprobar salud y navegar:

| URL | Que es |
|---|---|
| `http://localhost:8080/web1/health` | JSON: `{"status":"UP","db":"UP","postgres":"PostgreSQL 16...","lecturas":N}`; 503 si la BD no responde |
| `http://localhost:8080/web1/lecturas` | Flujo principal: catalogo de sensores, formulario de lectura, lecturas recientes |
| `http://localhost:8080/web1/alertas` | Alertas generadas por lecturas fuera de umbral |
| `http://localhost:8080/web1/` | Redirige a `/lecturas` |

Si el puerto 8080 esta ocupado por otro servicio que no te pertenece, cambia el puerto en `conf/server.xml` y
usa `BASE_URL=http://localhost:PUERTO/web1` en los scripts.

## 4. Datos de prueba

Sensores de la semilla (`sql/02_seed.sql`). El **rango fisico** rechaza la lectura (400); el **umbral** la acepta pero
genera alerta:

| Sensor | Tipo (unidad) | Zona | Rango fisico | Umbral operativo |
|---|---|---|---|---|
| `SEN-A-TEMP-01` | Temperatura ambiente (C) | Cama A | [-10, 60] | [15, 32] |
| `SEN-A-HSUE-01` | Humedad de suelo (%) | Cama A | [0, 100] | [40, 80] |
| `SEN-I1-TEMP-01` | Temperatura ambiente (C) | Invernadero 1 | [-10, 60] | [18, 30] |
| `SEN-I1-HAIR-01` | Humedad relativa (%) | Invernadero 1 | [0, 100] | [50, 85] |
| `SEN-I1-LUZ-01` | Luminosidad (lux) | Invernadero 1 | [0, 100000] | [2000, 60000] |

Valores sugeridos con `SEN-A-TEMP-01`:

| Entrada | Resultado |
|---|---|
| `25.5` | Positiva: 303, lectura guardada, "en rango" |
| `38` | Positiva con alerta: 303, lectura guardada + alerta **ALTA** |
| `10` | Positiva con alerta: 303, lectura guardada + alerta **BAJA** |
| `abc` | Negativa: 400 "El valor debe ser numerico" |
| vacio | Negativa: 400 "El valor de la lectura es obligatorio" |
| `150` | Negativa: 400 "fuera del rango fisico permitido ... [-10.00, 60.00]" |
| `24.555` | Negativa: 400 "admite como maximo 2 decimales" |
| sensor `999` (curl) | Negativa: 400 "El sensor seleccionado no existe" |

## 5. Verificacion reproducible

```bash
export CATALINA_HOME=/ruta/a/apache-tomcat-9.0.115     # Windows Git Bash: /c/Tools/apache-tomcat-9.0.115
./scripts/verify-module.sh M02
```

El script compila, corre las pruebas unitarias, inspecciona el WAR, consulta PostgreSQL, (re)despliega en Tomcat,
espera la ruta de salud y ejecuta el protocolo HTTP completo con `curl`. Cada paso imprime `VERIFICADO` o
`NO_VERIFICADO`, guarda su salida en `docs/evidencia/txt/` y al final anonimiza las rutas locales. Termina con
`RESULTADO: VERIFICADO` (codigo 0) o `NO_VERIFICADO` (codigo 1). Variables opcionales: `BASE_URL`, `PSQL_CMD`,
`SKIP_DEPLOY=1`.

Protocolo manual equivalente (URL, entrada, accion, resultado):

```bash
B=http://localhost:8080/web1
curl -i $B/lecturas                                                  # 200, catalogo + lecturas
curl -i -X POST -d "sensorId=2&valor=25.5" $B/lecturas               # 303, Location: /web1/lecturas?creada=N
curl -i -X POST -d "sensorId=2&valor=abc"  $B/lecturas               # 400, "El valor debe ser numerico"
curl -i -X POST -d "sensorId=2&valor=38"   $B/lecturas               # 303, ...&alerta=ALTA
curl -i $B/lecturas                                                  # 200, la lectura nueva aparece
curl -i $B/alertas                                                   # 200, alerta ALTA listada
docker exec -i dsw-p02-huerto-db psql -U huerto_app -d huerto_db < sql/03_consultas_verificacion.sql
```

(`sensorId` es el id de `SEN-A-TEMP-01`; el script lo obtiene del HTML del catalogo porque depende del orden de insercion.)

Capturas de pantalla (opcional):

```bash
python -m pip install playwright && python -m playwright install chromium
python scripts/capturas.py            # genera docs/evidencia/img/01..10
```

Limpieza:

```bash
./scripts/cleanup.sh          # borra lecturas/alertas de prueba (origen = manual) y target/
./scripts/cleanup.sh --all    # ademas detiene Tomcat, retira web1 y elimina contenedor + volumen
```

## 6. Pruebas

- **Unitarias (JUnit 5, sin BD):** `src/test/java/.../LecturaValidatorTest.java`, 10 casos: 3 positivos (valor en rango,
  alerta ALTA, alerta BAJA) y 7 negativos (vacio, no numerico, tres decimales, fuera de rango fisico, sensor invalido,
  sensor inactivo, observacion larga). Se ejecutan en `mvn package`.
- **HTTP (integracion):** `scripts/verify-module.sh` (automatico) o el protocolo manual de la seccion 5.
- **Persistencia:** `sql/03_consultas_verificacion.sql` antes y despues del protocolo.
- **Infraestructura:** con la BD detenida `/health` responde 503 y `/lecturas` muestra la pagina de error controlada
  (`docs/evidencia/txt/18_health_sin_bd.txt`).

Estados declarados por prueba en `docs/verification-report.md`.

## 7. Evidencia

Indice completo relacionado con R02 en `docs/evidencia/INDICE.md`.

| Captura | Contenido |
|---|---|
| `img/01_get_inicial_lecturas.png` | GET inicial: catalogo de 5 sensores y 2 lecturas semilla |
| `img/02_formulario_lectura_valida.png` | Formulario lleno (27.5 C) antes del POST |
| `img/03_post_valido_resultado.png` | Resultado del POST valido: mensaje de exito y fila nueva |
| `img/04_post_invalido_no_numerico.png` | Validacion negativa: `abc` |
| `img/05_post_invalido_rango_fisico.png` | Validacion negativa: `150` |
| `img/06_post_invalido_vacio.png` | Validacion negativa: campos vacios |
| `img/07_post_valido_con_alerta.png` | POST 38 C: lectura guardada y alerta ALTA |
| `img/08_get_alertas.png` | Vista de alertas |
| `img/09_health_json.png` | Ruta de salud con version de PostgreSQL |
| `img/10_error_404.png` | Pagina de error controlada |

## 8. Decisiones de diseno (para poder explicarlas)

| Decision | Por que | Alternativa considerada | Consecuencia |
|---|---|---|---|
| JSP solo presenta; reglas en `LecturaValidator`/`LecturaService`; SQL en `*Repository` | Separar capas permite probar las reglas sin Tomcat ni BD (10 pruebas JUnit). | Scriptlets con JDBC dentro de la JSP. | Mas clases, pero cada una explicable y probable. |
| POST-Redirect-GET (303) | Evita reenvios duplicados al refrescar y demuestra persistencia con un GET independiente. | Responder 200 con la lista en el mismo POST. | Se necesita pasar el resultado por query string (`creada`, `alerta`). |
| Lectura + alerta en una transaccion (`setAutoCommit(false)`) | Si falla la alerta no debe quedar una lectura huerfana. | Dos operaciones autocommit. | Una conexion por peticion; sin pool (limitacion declarada). |
| Dos rangos: fisico (`tipo_sensor`) y operativo (`umbral`) | Distingue "entrada imposible" (400) de "valor preocupante" (alerta). | Un solo rango. | Modelo de 7 entidades en vez de 5. |
| Credenciales por entorno (`DbConfig`) | M02 exige no versionar secretos; el WAR es el mismo en cualquier entorno. | JNDI `context.xml` de Tomcat. | Hay que crear `setenv.*` en cada maquina (documentado). |
| JSTL 1.2 con `<c:out>` | Escapa HTML y evita XSS en observaciones. | HTML manual con scriptlets. | Un jar adicional en el WAR (414 KB). |

## 9. Seguridad y datos

- Sin credenciales, tokens ni datos personales en el repositorio; `setenv.*` y `.env` estan en `.gitignore`.
- Todos los datos son ficticios (huerto escolar demo). Las rutas locales en la evidencia se sustituyen por marcadores.
- Consultas solo con `PreparedStatement`; salida HTML escapada con JSTL; la pagina de error no muestra trazas.

## 10. Autoria

Producto de equipo del PRxx (3 roles, ver `docs/acta-proyecto.md`). Rol de evidencia y documentacion: Alejandro
(`zywoxxx`). Cada integrante conserva su explicacion individual en `docs/evidencia/individual/`.
