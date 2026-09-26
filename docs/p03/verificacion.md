# P03 - Verificacion, limitaciones y contribuciones

Fecha: 2026-09-25. Entorno probado: Windows 11, JDK 11.0.32, Maven 3.9.9, Tomcat 9.0.115 (`C:\Tools`), PostgreSQL 16.15 en Docker (`localhost:5436`), Git Bash, Python 3.11 + Playwright (Chromium). Commit de partida: `832f377` (P02). Comando: `CATALINA_HOME=/c/Tools/apache-tomcat-9.0.115 ./scripts/verify-module.sh M03`.

## Resultado de la corrida oficial

`docs/p03/evidencia/txt/16_resumen.txt`:

| Paso | Estado |
|---|---|
| Java 11 disponible | VERIFICADO |
| `mvn clean package`: 21 pruebas, `target/web2.war` | VERIFICADO |
| WAR con Mojarra, PrimeFaces, Weld, `beans.xml`, vistas XHTML y sin JSP | VERIFICADO |
| PostgreSQL responde, 7 tablas | VERIFICADO |
| Redespliegue limpio de `web2` y `/health` 200 con `db=UP` | VERIFICADO |
| `login.xhtml` con PrimeFaces; `/app` sin sesion redirige | VERIFICADO |
| Recorrido en navegador (`pruebas_jsf.py`): 26 casos | VERIFICADO (26/26) |
| Lecturas y anotaciones del recorrido en PostgreSQL | VERIFICADO |

El detalle por caso esta en `pruebas-aceptacion.md` y en `evidencia/txt/pruebas_jsf_resultados.txt`; la bitacora del recorrido con conteos antes/despues, en `evidencia/txt/pruebas_jsf.txt`.

## Que no esta verificado o queda pendiente

- Caducidad real de 20 minutos: NO_VERIFICADO (se comprobo el comportamiento con la sesion ausente, no la espera).
- Sensor inexistente o inactivo y anotacion de 301 caracteres desde el navegador: NO_VERIFICADO por ese medio; PrimeFaces no permite enviarlos. Ambas reglas estan en JUnit.
- Rechazo en servidor de un POST forjado por un rol sin permiso: NO_VERIFICADO por HTTP; el chequeo esta en `LecturaBean.guardar` y en `AuthServiceTest.permisosPorRol`.
- Paginacion con mas de 10 filas y despliegue en Linux/macOS: PENDIENTE.
- Reproduccion por otro integrante en una maquina limpia (CA05): PENDIENTE.
- Confirmacion del facilitador en F02: sigue sin registrarse en `docs/F02-seleccion-proyecto.md`; no se afirma que este confirmada.

## Diferencias entre la consigna y la documentacion, resueltas explicitamente

- La guia P03 pide `cd codigo/dsw-evolucion-web && ./scripts/verify-module.sh M03`. Nuestra ruta real es la raiz de este repositorio; el script acepta `M02` y `M03` y documenta la ruta.
- El acta (P02) reparte los permisos por rol; P03 exige control de sesion. Se implemento autenticacion con usuarios ficticios y los permisos del acta tal cual (solo el observador captura lecturas). Si el equipo quiere que el responsable tambien capture, es un cambio de una linea en `Permisos.java` y debe anotarse en el acta.
- El rol de la anotacion dejo de ser un campo del formulario (P02) y ahora sale de la sesion: es la unica diferencia de comportamiento visible respecto a P02, y es la que pide la consigna ("no confundir seleccionar un rol con autenticar").
- La comparativa Web 1.0-4.0 con rubrica R01 que aparece en la consigna es otra actividad (individual); no se fusiono con P03/R03.

## Limitaciones tecnicas conocidas

- Una conexion JDBC por peticion, sin *pool*; suficiente para el laboratorio.
- Usuarios en un archivo de propiedades dentro del WAR: cambiar una contrasena implica regenerar el hash y reconstruir. Es deliberado para no salir del modelo de siete entidades.
- Las fechas se muestran en la zona horaria del servidor de base de datos (UTC en el contenedor).
- Sin HTTPS en el laboratorio: la cookie de sesion es `HttpOnly` pero no `Secure`.

## Contribuciones del equipo en P03

Las contribuciones reales de cada integrante en este incremento deben registrarse aqui por quien las hizo antes de entregar; no se inventan. Reparto acordado en el acta: desarrollo web (Juan Pablo Kuri Ricardez), datos (Pedro Garcia Padilla), evidencia y documentacion (Alejandro Pacheco Luna y Ariadna Trejo Alvarez). Los commits de P03 en este repositorio estan a nombre de la cuenta que hizo la integracion (`zywoxxx`).
