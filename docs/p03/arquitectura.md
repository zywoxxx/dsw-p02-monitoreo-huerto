# P03 - Arquitectura y decisiones tecnicas (Web 2.0 con JSF y PrimeFaces)

Commit de partida de la migracion: `832f377` (ultimo commit de P02, JSP/Servlet). Proyecto PR09, equipo DSW-E01.

## 1. Versiones y por que

| Componente | Version | Motivo |
|---|---|---|
| Java | 11 (JDK 11.0.32) | Version fija del curso. Obliga a agregar `javax.annotation-api` y `jaxb-api`, que el JDK ya no trae. |
| Tomcat | 9.0.115 | Version del paquete docente; implementa Servlet 4.0 / EL 3.0 con espacio `javax`. Cambiar a Tomcat 10 obligaria a migrar todo a `jakarta`. |
| JSF | Mojarra 2.3.9 (`org.glassfish:javax.faces`) | Version confirmada en M02/M03. Un solo jar con API e implementacion; Tomcat no incluye Faces. |
| PrimeFaces | 12.0.0 (artefacto sin classifier) | Version del paquete docente. La variante sin classifier es la de `javax`; la de `jakarta` lleva classifier y no aplica aqui. |
| CDI | Weld Servlet 3.1.9.Final (`weld-servlet-shaded`) | JSF 2.3 exige CDI para `@Named`, `@ViewScoped` y `@Inject`; Tomcat no lo trae. El jar "shaded" incluye API e implementacion y se registra solo. |
| Bean Validation | no se usa | Las reglas ya existian como validadores propios probados con JUnit (P02); agregar Hibernate Validator duplicaria reglas sin aportar nada al alcance. |
| JDBC | PostgreSQL 42.7.2 | Igual que P02. |
| Extras JDK 11 | `javax.annotation-api` 1.3.2, `jaxb-api` 2.3.1 | `@PostConstruct` y `DatatypeConverter` (Mojarra lo usa al cifrar el *flash* en redirecciones). Sin JAXB, cualquier `faces-redirect=true` lanzaba `NoClassDefFoundError`; se detecto en el primer arranque y quedo en la bitacora. |

No se mezclan `javax` y `jakarta`: todas las dependencias empresariales son `javax.*`; `javax.sql` y `javax.crypto` son de Java SE y no se tocan.

## 2. Capas

```
Facelets (.xhtml) + PrimeFaces  ->  beans de presentacion (web/*Bean)  ->  servicios y validadores (service/*)
                                                                        ->  repositorios JDBC (repository/*)  ->  PostgreSQL
```

- **Vistas**: `login.xhtml`, `app/lecturas.xhtml`, `app/alertas.xhtml`, `app/anotaciones.xhtml`, `expirada.xhtml`, `error.xhtml`, plantilla `WEB-INF/templates/plantilla.xhtml`. No contienen SQL ni reglas.
- **Beans**: `SesionBean` (`@SessionScoped`, solo identidad y rol), `LecturaBean`, `AlertaBean`, `AnotacionBean` (`@ViewScoped`, estado de cada formulario). Todos `Serializable`; los repositorios y servicios que contienen tambien lo son porque no guardan estado.
- **Servicios**: `LecturaService` (reutilizado de P02 sin cambios: valida, inserta lectura y alerta en una transaccion), `AnotacionService` (nuevo, concentra lo que en P02 hacia el servlet), `AuthService` (nuevo), `Permisos` (nuevo).
- **Repositorios**: sin cambios respecto a P02. SQL parametrizado, `try-with-resources`, `RETURNING id`.
- **Servlets que quedan**: `HealthServlet` (`/health`, JSON) y el filtro `AutenticacionFilter`. Los servlets de lecturas, alertas y anotaciones y las JSP se eliminaron: el flujo corre por completo en JSF.

## 3. Ciclo JSF aplicado al flujo principal

1. GET `/app/lecturas.xhtml`: el `f:viewAction` crea `LecturaBean`; su `@PostConstruct` consulta sensores e historial. Si PostgreSQL no responde, el bean agrega un mensaje de error y oculta el formulario; como el bean se crea antes del render, `p:messages` lo muestra (sin el `viewAction` el bean se creaba durante el render y el mensaje se perdia; quedo registrado en la bitacora).
2. Al elegir sensor, `p:ajax process="@this" update="infoSensor"` muestra unidad, rango fisico y umbral sin recargar.
3. `p:commandButton process="@form" update="@form :mensajes :formTabla:tablaLecturas"`: postback AJAX. El valor viaja como texto (`p:inputText`) y lo valida `LecturaValidator`; no se usa `p:inputNumber` porque redondea silenciosamente 24.555 a 24.56, y la regla es rechazarlo.
4. Si hay errores, el bean no limpia nada: al re-renderizar `@form`, los campos conservan lo capturado. Solo tras confirmar la persistencia se vacian `valor` y `observacion` y se recarga el historial.
5. `p:blockUI` sobre el formulario mientras dura la peticion evita el doble clic. Como el envio es AJAX, recargar la pagina hace un GET y no reenvía el formulario.
6. Sesion o vista caducada: `AutenticacionFilter` responde a peticiones AJAX con un `partial-response` de redireccion (una redireccion HTTP normal rompe la respuesta parcial); `ViewExpiredException` se mapea a `expirada.xhtml` y, con `PrimeExceptionHandlerFactory`, tambien funciona en AJAX.

## 4. Control de sesion y permisos

- **Autenticacion**: `AuthService` lee `usuarios.properties` (dentro del WAR) con contrasenas como hash PBKDF2-HMAC-SHA256 con sal y 120 000 iteraciones; compara en tiempo constante. Usuarios ficticios: `observador`, `responsable`, `coordinacion` (contrasenas en el README). No hay registro publico ni recuperacion de contrasena porque no estan en el alcance aprobado, y no se agrega una entidad `usuario` para no salir del modelo de siete entidades; si el equipo lo aprueba mas adelante, la tabla es el cambio natural.
- **Sesion**: al entrar se renueva el id de sesion (`changeSessionId`, contra fijacion), se guarda el usuario en `SesionBean` y en un atributo plano de `HttpSession` que lee el filtro. Salir invalida la sesion. Caducidad: 20 minutos (`web.xml`). Cookie `HttpOnly`, seguimiento solo por cookie.
- **Permisos** (`Permisos.java`, derivados del acta, seccion 2): OBSERVADOR registra lecturas y anota; RESPONSABLE y COORDINACION consultan y anotan. Se comprueban en el servidor dentro de `guardar()` de cada bean, ademas de ocultar el formulario. `autor_rol` de la anotacion sale de la sesion, nunca de un campo.
- **Ambiguedad declarada**: el acta dice que el responsable "define zonas, sensores y umbrales" pero no que capture lecturas; se sigue el acta al pie de la letra. Cambiar eso es una linea en `Permisos`.
- **CSRF**: los postbacks JSF llevan `javax.faces.ViewState` con guardado en servidor; una peticion sin ViewState valido no ejecuta acciones. Las salidas se escapan por defecto en Facelets.

## 5. Persistencia

Sin cambios de esquema respecto a P02: siete tablas, `CHECK` de rangos, procedencia (`manual`/`simulado`), nivel de alerta y rol de anotacion. La transaccion lectura + alerta se conserva en `LecturaService`. El unico cambio en `config` es `DriverManager.setLoginTimeout(5)` para que, con la base caida, la vista avise en segundos en lugar de esperar el tiempo de conexion por defecto.

Variables `DB_URL`, `DB_USER`, `DB_PASSWORD`: las lee `DbConfig` de propiedades de la JVM o del entorno; en Tomcat se definen en `bin/setenv.bat` o `bin/setenv.sh` (no versionados). Un archivo `.env` no lo carga Java: solo lo usa `docker compose`. Desde el host la base es `localhost:5436`; el nombre de servicio `db` solo vale entre contenedores.

## 6. Despliegue

WAR `web2.war`, contexto `/web2`. En Windows Tomcat bloquea los jars de `WEB-INF/lib` mientras corre y el autodespliegue puede conservar clases viejas; por eso `scripts/redeploy-tomcat.sh` detiene Tomcat, borra el despliegue anterior y la cache de `work/`, copia el WAR y vuelve a arrancar. `verify-module.sh M03` lo usa.

## 7. Que no se hizo a proposito

CRUD de zonas, sensores o umbrales; atencion o cierre de alertas; graficas; API REST; simulador IoT; Angular o Spring Boot. Todo eso pertenece a otras etapas o requiere alcance aprobado en el foro. Los filtros, la paginacion y los mensajes son mejoras de interaccion sobre funciones que ya existian, no funciones nuevas.
