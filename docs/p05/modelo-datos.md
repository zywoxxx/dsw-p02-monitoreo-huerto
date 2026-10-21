# P05 - Modelo de datos: que cambia y como lo usa la API

El modelo sigue siendo el de P02: siete tablas (`zona`, `variable`, `sensor`, `umbral`, `lectura`, `alerta`,
`anotacion`), descritas en `docs/modelo-datos.md` y, con su relacion con la API, en `docs/p04/modelo-datos.md`.
Aqui solo esta lo que P05 agrega o usa por primera vez.

## 1. Cambio en `alerta`

| Columna | Tipo | Desde | Para que |
|---|---|---|---|
| `atendida` | `BOOLEAN NOT NULL DEFAULT false` | P02 | estado de la alerta; hasta P04 nadie la cambiaba |
| `atendida_en` | `TIMESTAMPTZ` | **P05** | instante en que se atendio; `NULL` si esta pendiente |
| `atendida_por` | `VARCHAR(15)` | **P05** | rol que la atendio; `NULL` si esta pendiente |

Restriccion `ck_alerta_atencion`: `(atendida AND atendida_en IS NOT NULL AND atendida_por IN (los tres roles)) OR
(NOT atendida AND atendida_en IS NULL AND atendida_por IS NULL)`. Asi la base no admite una alerta "atendida" sin
saber cuando ni por quien, ni una pendiente con restos de una atencion anterior.

### Migracion

`sql/04_p05_atencion_alerta.sql` agrega las dos columnas con `ADD COLUMN IF NOT EXISTS` y la restriccion solo si no
existe. Se puede ejecutar varias veces y no toca filas: las alertas que ya habia quedan pendientes, con las columnas
nuevas en `NULL`, que es justo el estado coherente. `01_schema.sql` incluye las columnas para instalaciones limpias.
No hay cambio destructivo ni perdida de datos; el volumen de Docker se conserva.

## 2. Estados de una alerta

| Estado | `atendida` | `atendida_en` | `atendida_por` | Como se llega |
|---|---|---|---|---|
| pendiente | `false` | `NULL` | `NULL` | al crearse (lectura fuera del umbral) o con `PATCH {atendida: false}` |
| atendida | `true` | `now()` del servidor | rol del token | con `PATCH {atendida: true}` por RESPONSABLE |

Pedir el estado en el que ya esta responde 409 y no escribe nada.

## 3. De tabla a recurso (lo nuevo)

| Recurso del contrato | Tablas | Campo JSON <- columna |
|---|---|---|
| `Zona` | `zona` | `id`, `nombre`, `cultivo`, `ubicacion` directos |
| `Alerta` | `alerta` + `lectura` + `sensor` + `variable` + `zona` | `lecturaId` <- `alerta.lectura_id`; `sensorCodigo` <- `sensor.codigo`; `variable`, `unidad` <- `variable`; `zonaId`, `zona` <- `zona`; `valor` <- `lectura.valor`; `nivel`, `mensaje`, `atendida`, `atendidaEn`, `atendidaPor`, `creadaEn` <- `alerta` |
| `CambioAtencion` (entrada) | `alerta` | `atendida` -> `atendida`; `atendida_en` y `atendida_por` los pone el servidor |
| `Anotacion` | `anotacion` + `zona` | `zonaId`, `zona` <- `zona`; `lecturaId` <- `anotacion.lectura_id` (ausente si es `NULL`); `autorRol` <- `autor_rol`; `texto`, `creadaEn` |
| `NuevaAnotacion` (entrada) | `anotacion` | `zonaId` -> `zona_id`; `lecturaId` -> `lectura_id`; `texto` -> `texto` (recortado); `autor_rol` <- rol del token; `creada_en` <- `now()` |

## 4. Donde vive cada regla nueva

| Regla | En la API | En PostgreSQL |
|---|---|---|
| Solo RESPONSABLE atiende | `Permisos`, `AlertaController` (403) | - |
| No repetir el estado | `AlertaService` (409) | - |
| Atencion coherente (instante y rol juntos) | `AlertaService` los escribe juntos en una transaccion | `ck_alerta_atencion` |
| Rol valido en la atencion | viene del token, que solo emite los tres roles | `ck_alerta_atencion` |
| Zona de la anotacion existe | `AnotacionService` (404) | FK `anotacion.zona_id` |
| Lectura de la anotacion existe | `AnotacionService` (404) | FK `anotacion.lectura_id` |
| La lectura pertenece a la zona | `AnotacionService` (422) | - (no hay FK compuesta) |
| Texto de 3 a 300 tras recortar | `ReglasAnotacion` (400) | `CHECK (length(trim(texto)) >= 3)`, `VARCHAR(300)` |
| Rol de la anotacion | viene del token | `CHECK autor_rol` |

## 5. Consultas de comprobacion

`sql/03_consultas_verificacion.sql` muestra ahora `atendida_en` y `atendida_por` en la consulta de alertas.
`verify-module.sh M05` lo ejecuta antes y despues de las pruebas (`evidencia/txt/08_postgres_antes.txt`,
`12_postgres_despues.txt`); entre ambos se ven las lecturas, alertas y anotaciones creadas por la API, y una alerta
atendida y reabierta por el recorrido.

`sql/99_cleanup.sql` sigue retirando solo lo creado por las pruebas: lecturas `manual` con sus alertas y anotaciones
cuyo texto empieza con `[prueba]`.
