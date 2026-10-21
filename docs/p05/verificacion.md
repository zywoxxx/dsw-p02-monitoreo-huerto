# P05 - Verificacion, fallos encontrados, limitaciones y pendientes

Verificacion completa el 2026-10-21 en el equipo de desarrollo: Windows 11, Java 11.0.32, Maven 3.9.9, Node 18.20.8,
npm 10.8.2, PostgreSQL 16.15 en Docker. Commit de partida de P05: `9f398d6` (cierre de P04); contrato 0.5.0 en
`701016e`. La evidencia de `evidencia/txt` e `evidencia/img` es de la corrida final (09:59, hora local).

## Como se verifico

```bash
./scripts/verify-module.sh M05        # tabla 1: compila, valida el contrato, migra, levanta la API y el cliente, prueba y apaga
./scripts/prueba_base_detenida.sh     # tabla 2: detiene y vuelve a arrancar el contenedor de la base
./scripts/cleanup.sh                  # retira los datos de prueba y las carpetas generadas
```

La guia de P05 pide `cd codigo/dsw-evolucion-web && ./scripts/verify-module.sh M04`. Nuestra ruta es la raiz de este
repositorio; `M04` sigue funcionando (deja su evidencia en `docs/p04/evidencia`) y `M05` es el mismo verificador con
la migracion de P05 y la evidencia en `docs/p05/evidencia`, para no mezclar incrementos.

## 1. Resultado de `verify-module.sh M05` (16 pasos, 0 fallos)

| # | Paso | Resultado | Evidencia |
|---|---|---|---|
| 1 | Java 11 y Node 18 disponibles | VERIFICADO | `txt/00_versiones.txt` |
| 2 | `api-spring` compila con Java 11; **37 pruebas** JUnit en verde (16 de P04 + 21 de P05) | VERIFICADO | `txt/01_build_api.txt`, `txt/02_pruebas_api_unitarias.txt` |
| 3 | El jar contiene los controladores de lecturas, zonas, alertas y anotaciones, el driver de PostgreSQL, Spring JDBC y springdoc | VERIFICADO | `txt/03_jar_contenido.txt` |
| 4 | `application.properties` sin credenciales escritas | VERIFICADO | salida del script |
| 5 | `frontend-angular` compila (`ng build`) | VERIFICADO | `txt/05_build_frontend.txt` |
| 6 | Pruebas del cliente Angular: **9 de 9** (5 de P04 + 4 de P05) | VERIFICADO | `txt/06_pruebas_frontend.txt` |
| 7 | `openapi.yaml` 0.5.0 es OpenAPI 3.0.3 valido: 13 operaciones, 19 esquemas | VERIFICADO | `txt/07_openapi_validacion.txt` |
| 8 | PostgreSQL responde; existen las 7 tablas | VERIFICADO | `txt/08_postgres_antes.txt` |
| 9 | La migracion `sql/04` se aplica sin error (sobre una base que ya la tenia) y `alerta` tiene `atendida_en` y `atendida_por` | VERIFICADO | `txt/08b_migracion_p05.txt` |
| 10 | La API arranca y `/api/health` responde 200 con `db=UP` | VERIFICADO | `txt/09_api_arranque.txt`, `txt/10_health.txt` |
| 11 | Contrato contra la API en marcha: **64 de 64** casos | VERIFICADO | `txt/pruebas_api.txt`, `txt/pruebas_api_resultados.txt` |
| 12 | Recorrido del cliente en navegador con los tres roles: **23 de 23** casos | VERIFICADO | `txt/recorrido_angular.txt`, `img/01` a `img/22` |
| 13 | Las lecturas y anotaciones creadas por la API existen en PostgreSQL; la alerta atendida y reabierta se ve en la base | VERIFICADO | `txt/12_postgres_despues.txt` |
| 14 | La API se detiene y libera el puerto | VERIFICADO | `txt/13_resumen.txt` |

Cada caso del contrato valida el cuerpo de la respuesta contra el esquema de `openapi.yaml` y, en los casos
negativos, cuenta filas en PostgreSQL antes y despues. El ultimo caso (64) compara lo que springdoc deduce del codigo
con el contrato: todo lo implementado esta en el contrato y ya no queda ninguna operacion sin implementar.

## 2. Comprobaciones fuera del script principal

| Caso | Resultado | Evidencia |
|---|---|---|
| Base detenida: `/api/health` 503; `GET /api/sensores`, `POST /api/lecturas`, `PATCH /api/alertas/1` y `POST /api/anotaciones` responden 503 `BASE_NO_DISPONIBLE` | VERIFICADO | `txt/14_base_detenida.txt` |
| El login sigue funcionando con la base detenida (no la usa) y la API se recupera sola al volver el contenedor | VERIFICADO | `txt/14_base_detenida.txt` |
| Las tres rutas nuevas responden 200 con token y 401 sin token | VERIFICADO | `txt/14_base_detenida.txt` |
| Usuario inexistente y contrasena incorrecta dan el mismo mensaje | VERIFICADO | `txt/14_base_detenida.txt` |
| La migracion se puede correr dos veces sin error | VERIFICADO (la base de pruebas ya venia migrada y el paso 9 volvio a aplicarla) | `txt/08b_migracion_p05.txt` |
| Demostracion en localhost con `scripts/demo_p05.sh` (API, cliente y navegador) | VERIFICADO a mano el 2026-10-21 | sin archivo de evidencia |

## 3. Fallos que encontramos al probar

| Fallo | Como aparecio | Correccion |
|---|---|---|
| La primera corrida de `verify-module.sh M05` termino con 2 NO_VERIFICADO: el caso 16 del contrato ("15 y 32 sin alerta") vio una alerta de mas, y el caso 02 del navegador recibio un 504 del proxy | Una ejecucion anterior del verificador que detuvimos a medias dejo vivo su recorrido en navegador; corrio en paralelo con la nueva, inserto las lecturas 103 y 105 (una con alerta) entre los conteos del caso 16 y saturo el proxy de desarrollo en el caso 02 | No era un defecto de la aplicacion. Se detuvieron los procesos sobrantes y se repitio la verificacion completa: 0 fallos. Queda anotado porque la guia pide conservar el primer error significativo |
| Condicion de carrera al atender una alerta: el servicio leia el estado y luego hacia el `UPDATE` sin condicion, asi que dos peticiones simultaneas podian "atender" la misma alerta y ambas recibir 200 | Revision de codigo | El `UPDATE` exige ahora `atendida = NOT :atendida`; si no cambia ninguna fila, el servicio responde 409 igual que si el estado ya fuera el pedido. Sin prueba automatica de concurrencia (ver pendientes) |

## 4. Lo que no esta verificado o queda pendiente

| Asunto | Estado | Nota |
|---|---|---|
| Dos peticiones simultaneas de `PATCH` sobre la misma alerta | NO_VERIFICADO | La condicion del `UPDATE` lo cubre por construccion; no hay prueba de concurrencia |
| Caducidad real del token a los 30 minutos contra la API en marcha | NO_VERIFICADO | Probada con reloj fijo en `TokenServiceTest` |
| Peticion CORS real desde otro origen en el navegador | NO_VERIFICADO | Se prueba el *preflight* con peticiones directas; en desarrollo el navegador usa el proxy |
| Servir el resultado de `ng build` desde un servidor web; despliegue en Linux o macOS | NO_VERIFICADO | Solo `ng serve` en Windows 11 con Git Bash |
| Reproduccion por otro integrante en una maquina limpia (CA05) | PENDIENTE | |
| Confirmacion del facilitador en F02 | PENDIENTE | Sigue sin registrarse en `docs/F02-seleccion-proyecto.md`; no afirmamos que este confirmada |

## 5. Limitaciones conocidas

- Un token emitido no se puede revocar antes de sus 30 minutos; vive en `sessionStorage` y se pierde al cerrar la pestana.
- Sin HTTPS ni limite de intentos de acceso: todo corre en `localhost`.
- Los usuarios siguen en un archivo dentro del jar; cambiar una contrasena implica reconstruir.
- La atencion de una alerta guarda el rol, no la persona: el modelo no tiene tabla de usuarios (decision del acta).
- `GET /api/anotaciones` cambio de lista a pagina entre 0.4.0 y 0.5.0; el cliente de P04 no lo consumia, asi que no rompio nada, pero es un cambio de contrato y esta anotado en `openapi.yaml`.
- springdoc nombra los esquemas segun las clases Java (`CambioAtencionRequest`, `PaginaAlerta`), no como el contrato; se comparan rutas y metodos.
- Los datos de prueba quedan en la base hasta ejecutar `cleanup.sh`.

## 6. Diferencias entre la consigna y lo entregado

- "Salud, consulta y cambio de estado": salud es `/api/health`; consulta son los `GET`; el cambio de estado es
  `PATCH /api/alertas/{id}` (atender o reabrir). Registrar lecturas y anotaciones tambien cambia el estado del sistema,
  pero entendemos que la consigna pide un recurso cuyo estado se modifique, y la alerta ya tenia la columna `atendida`
  desde P02 sin que nadie la cambiara.
- "Pruebas 200/201/400/401" del procedimiento: cubiertas y ampliadas con 403, 404, 409, 422 y 503, porque el contrato
  los define y el cliente los muestra.
- La guia pide `verify-module.sh M04`; usamos `M05` por lo explicado arriba. `M04` sigue disponible.
- No se uso ningun servicio externo: PostgreSQL en Docker local, sin APIs de terceros, sin CDN en el cliente compilado.

## 7. Contribuciones del equipo en P05

P05 es de equipo. Las contribuciones de cada integrante las registra quien las hizo, aqui o en `docs/bitacora.md`,
antes de entregar; no se inventan. Reparto acordado en el acta: desarrollo web (Juan Pablo Kuri Ricardez), datos
(Pedro Garcia Padilla), evidencia y documentacion (Alejandro Pacheco Luna y Ariadna Trejo Alvarez). Los commits de
P05 en este repositorio estan a nombre de la cuenta que hizo la integracion (`zywoxxx`).
