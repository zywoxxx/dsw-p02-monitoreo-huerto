# PR09 - Monitoreo de huerto o ambiente

Proyecto integrador del equipo **DSW-E01** (Desarrollo de Sistemas Web, DSW-19559). Un huerto escolar registra
lecturas de sensores (temperatura, humedad, luz) con su instante y procedencia, avisa cuando una lectura sale del
umbral operativo y permite anotaciones por rol. Todos los datos son ficticios.

| Incremento | Estado | Tecnologia | WAR / contexto |
|---|---|---|---|
| **P03 (actual)** - Web 2.0 | `verify-module.sh M03` -> VERIFICADO el 2026-09-25 (26 casos en navegador, 21 pruebas unitarias) | JSF 2.3 (Mojarra 2.3.9) + PrimeFaces 12 + CDI (Weld 3.1.9) sobre Tomcat 9.0.115; JDBC a PostgreSQL 16 | `web2.war` -> `http://localhost:8080/web2/` |
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

## 2. Estructura

```
dsw-p02-monitoreo-huerto/
├── pom.xml                        # WAR web2: Mojarra 2.3.9, PrimeFaces 12, Weld 3.1.9, jaxb-api, driver PostgreSQL, JUnit 5
├── docker/docker-compose.yml      # PostgreSQL 16 en localhost:5436; ejecuta sql/01 y 02 al crear el volumen
├── sql/                           # 01_schema, 02_seed, 03_consultas_verificacion, 99_cleanup
├── scripts/
│   ├── verify-module.sh           # M02 o M03: build, WAR, PostgreSQL, despliegue, salud y pruebas
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

## 7. Equipo

| Responsabilidad | Integrante | GitHub |
|---|---|---|
| Desarrollo web | Juan Pablo Kuri Ricardez | `juankuri` |
| Datos (PostgreSQL) | Pedro Garcia Padilla | `pedro-gar-pad` |
| Evidencia y documentacion | Alejandro Pacheco Luna | `zywoxxx` |
| Evidencia y documentacion | Ariadna Trejo Alvarez | `ariadna-19` |
