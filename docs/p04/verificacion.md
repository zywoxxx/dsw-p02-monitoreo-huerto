# P04 - Verificacion, limitaciones y pendientes

Verificacion completa el 2026-09-29 (cierre del codigo) y repetida el 2026-10-09 antes de entregar; la evidencia de
`evidencia/txt` e `img` es de la corrida final, salvo `14_base_detenida.txt`, del 2026-09-29. Equipo de prueba: Windows 11, Java 11.0.32, Maven 3.9.9, Node 18.20.8,
npm 10.8.2, PostgreSQL 16.15 en Docker. Commit de partida: `bf78beb`.

## Como se verifico

```bash
./scripts/verify-module.sh M04        # todo lo de la tabla 1
./scripts/prueba_base_detenida.sh     # tabla 2 (detiene y vuelve a arrancar el contenedor de la base)
./scripts/cleanup.sh                  # retira las lecturas de prueba y las carpetas generadas
```

La guia pide ejecutar `cd codigo/dsw-evolucion-web && ./scripts/verify-module.sh M04`. Nuestra ruta es la raiz de
este repositorio; el script es el mismo de P02 y P03, ahora con el modulo `M04`.

## 1. Resultado de `verify-module.sh M04`

| # | Paso | Resultado | Evidencia |
|---|---|---|---|
| 1 | Java 11 y Node 18 disponibles | VERIFICADO | `txt/00_versiones.txt` |
| 2 | `api-spring` compila con Java 11; 16 pruebas en verde | VERIFICADO | `txt/01_build_api.txt`, `txt/02_pruebas_api_unitarias.txt` |
| 3 | El jar contiene controladores, driver de PostgreSQL, Spring JDBC y springdoc | VERIFICADO | `txt/03_jar_contenido.txt` |
| 4 | `application.properties` sin credenciales escritas | VERIFICADO | salida del script |
| 5 | `frontend-angular` compila (`ng build`) | VERIFICADO | `txt/05_build_frontend.txt` |
| 6 | Pruebas del cliente Angular: 5 de 5 | VERIFICADO | `txt/06_pruebas_frontend.txt` |
| 7 | `openapi.yaml` es OpenAPI 3.0.3 valido (10 operaciones, 16 esquemas) | VERIFICADO | `txt/07_openapi_validacion.txt` |
| 8 | PostgreSQL responde; existen las 7 tablas | VERIFICADO | `txt/08_postgres_antes.txt` |
| 9 | La API arranca y `/api/health` responde 200 con `db=UP` | VERIFICADO | `txt/09_api_arranque.txt`, `txt/10_health.txt` |
| 10 | Contrato contra la API en marcha: 30 de 30 casos | VERIFICADO | `txt/pruebas_api.txt`, `txt/pruebas_api_resultados.txt` |
| 11 | Recorrido del cliente en navegador: 12 de 12 casos | VERIFICADO | `txt/recorrido_angular.txt`, `img/01` a `img/11` |
| 12 | Las lecturas creadas existen en PostgreSQL | VERIFICADO | `txt/12_postgres_despues.txt` |
| 13 | La API se detiene y libera el puerto | VERIFICADO | `txt/13_resumen.txt` |

Las pruebas del contrato no solo miran el codigo de estado: cada cuerpo de respuesta se valida contra el esquema
correspondiente de `openapi.yaml`, y en cada caso negativo se cuenta antes y despues en PostgreSQL para comprobar
que no se guardo nada.

## 2. Comprobaciones fuera del script principal

| Caso | Resultado | Evidencia |
|---|---|---|
| Base detenida: `/api/health` responde 503 `DOWN` | VERIFICADO | `txt/14_base_detenida.txt` |
| Base detenida: `GET /api/sensores` y `POST /api/lecturas` responden 503 `BASE_NO_DISPONIBLE` y no se guarda nada | VERIFICADO | `txt/14_base_detenida.txt` |
| Al volver la base, la API se recupera sin reiniciarla | VERIFICADO | `txt/14_base_detenida.txt` |
| Las rutas solo definidas en el contrato responden 404 con token y 401 sin token | VERIFICADO | `txt/14_base_detenida.txt` |
| Usuario inexistente y contrasena incorrecta dan el mismo mensaje | VERIFICADO | `txt/14_base_detenida.txt` |
| Sin `DB_URL`, `DB_USER` y `DB_PASSWORD` la API no arranca | VERIFICADO a mano el 2026-09-29 (`Application run failed`); sin archivo de evidencia |

## 3. Fallos que encontramos al probar

| Fallo | Como aparecio | Correccion |
|---|---|---|
| El login sin contrasena respondia 401 y el contrato dice 400 | caso 04 de `pruebas_api.py` | `AuthController` valida primero que vengan los dos campos |
| Con la base detenida, `POST /api/lecturas` respondia 500 en lugar de 503 | `prueba_base_detenida.sh` | `ApiExceptionHandler` tambien atiende `TransactionException`: si la transaccion no se puede abrir, la excepcion no es de acceso a datos. Se agrego la prueba `baseNoDisponible` |
| `/api/health` publicaba la version completa de PostgreSQL, con sistema operativo y compilador | revision de la respuesta | Se recorta a "PostgreSQL 16.15" |
| El registro de arranque de Spring Boot escribia el nombre del equipo y el usuario del sistema en la evidencia | revision de `txt/09_api_arranque.txt` | `spring.main.log-startup-info=false` y el anonimizador sustituye ambos datos |
| Las pruebas de Angular no arrancaban: el navegador no se conectaba a Karma | `ng test` agotaba el tiempo de espera | Chromium reciente separa el modo sin ventana en `chrome-headless-shell`; el script usa ese ejecutable |
| Un caso del recorrido fallaba por la propia prueba, no por el cliente | caso 03 de `recorrido_angular.py` | La prueba buscaba una URL que terminara en `/api/sensores` y el cliente envia `?activo=true` |

## 4. Lo que no esta verificado o queda pendiente

| Asunto | Estado | Nota |
|---|---|---|
| `GET /api/zonas`, `GET /api/alertas`, `GET` y `POST /api/anotaciones` | PENDIENTE | Definidos en el contrato; sin controlador, servicio ni repositorio |
| Vistas de alertas y anotaciones en Angular | PENDIENTE | Dependen de lo anterior |
| Caducidad real del token a los 30 minutos contra la API en marcha | NO_VERIFICADO | Probada con reloj fijo en `TokenServiceTest`; no se espero media hora |
| Rol RESPONSABLE | NO_VERIFICADO contra la API | Se probo COORDINACION; ambos tienen los mismos permisos en `Permisos` |
| Peticion CORS real desde otro origen en el navegador | NO_VERIFICADO | Se probo el *preflight* con peticiones directas; en desarrollo el navegador usa el proxy |
| Servir el resultado de `ng build` desde un servidor web | NO_VERIFICADO | Solo se probo `ng serve` |
| Despliegue en Linux o macOS | NO_VERIFICADO | Solo Windows 11 con Git Bash |
| Reproduccion por otro integrante en una maquina limpia (CA05) | PENDIENTE | |
| Confirmacion del facilitador en F02 | PENDIENTE | Sigue sin registrarse en `docs/F02-seleccion-proyecto.md`; no afirmamos que este confirmada |
| Justificaciones individuales de los otros tres integrantes | PENDIENTE | Cada quien escribe la suya; ver `individual/LEEME.md` |

## 5. Limitaciones conocidas

- Un token emitido no se puede revocar; deja de valer a los 30 minutos o al reiniciar la API sin `JWT_SECRET`.
- El token se guarda en `sessionStorage`; se pierde al cerrar la pestana y un script inyectado podria leerlo.
- No hay limite de intentos de acceso ni HTTPS: todo corre en `localhost`.
- Los usuarios estan en un archivo dentro del jar; cambiar una contrasena implica reconstruir.
- springdoc nombra los esquemas segun las clases Java, asi que el documento generado y el contrato escrito no
  coinciden en los nombres; se comparan rutas y metodos, no nombres de esquemas.
- Las lecturas de prueba quedan en la base hasta ejecutar `cleanup.sh`.

## 6. Diferencias entre la consigna y lo entregado

- La consigna pide "estructura inicial compilable". Entregamos eso y ademas el flujo principal funcionando, porque
  era la forma de comprobar que el contrato se puede cumplir. Lo que no se implemento esta marcado como PENDIENTE.
- La consigna pide mantener "maximo tres roles y el flujo principal aprobado": son los mismos de P02 y P03.
- La guia pide el contrato OpenAPI generado. Se entrega el escrito a mano (`openapi.yaml`), que es el de referencia,
  y el generado por springdoc (`evidencia/txt/openapi_generado.json`).

## 7. Contribuciones del equipo en P04

Las contribuciones de cada integrante las registra quien las hizo, en su archivo de `docs/p04/individual/`; aqui no
se inventan. Los commits de P04 en este repositorio estan a nombre de la cuenta que hizo la integracion (`zywoxxx`).
Reparto acordado en el acta: desarrollo web (Juan Pablo Kuri Ricardez), datos (Pedro Garcia Padilla), evidencia y
documentacion (Alejandro Pacheco Luna y Ariadna Trejo Alvarez).
