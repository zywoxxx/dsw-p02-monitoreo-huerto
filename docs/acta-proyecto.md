# Acta breve de proyecto - PR09 Monitoreo de huerto o ambiente

| Campo | Valor |
|---|---|
| Experiencia educativa | Desarrollo de Sistemas Web (DSW-19559 / NRC 19559) |
| Proyecto del banco (C11) | **PR09 - Monitoreo de huerto o ambiente** (complejidad orientativa: media) |
| Seleccion | Publicada en F02 (ver `docs/F02-seleccion-proyecto.md`); segunda opcion PR03 |
| Actividad | P02 - Aplicacion Web 1.0 con JSP, Tomcat y PostgreSQL (primer incremento); 31/ago/2026 00:00 a 11/sep/2026 23:45 |
| Equipo | DSW-E01 |
| Instrumento | R02 (10 puntos) |
| Fecha del acta | 2026-09-11 |
| Repositorio | https://github.com/zywoxxx/dsw-p02-monitoreo-huerto |

## 1. Equipo (organizacion interna del trabajo)

| Responsabilidad en P02 | Integrante | GitHub |
|---|---|---|
| Desarrollo web (JSP/Servlet, WAR, Tomcat) | Juan Pablo Kuri Ricardez | `juankuri` |
| Datos (modelo PostgreSQL, scripts SQL, repositorios JDBC) | Pedro Garcia Padilla | `pedro-gar-pad` |
| Evidencia y documentacion (capturas, protocolo HTTP, README, bitacora, indice R02) | Alejandro Pacheco Luna, Ariadna Trejo Alvarez | `zywoxxx`, `ariadna-19` |

Todos revisan el codigo de los demas; la contribucion de cada integrante se describe en el documento de entrega del equipo (`docs/entrega/P02_EQUIPO_01.docx`, seccion 10).

## 2. Roles funcionales del sistema (limite C11: hasta tres)

| Rol (ficha PR09) | Que hace en el sistema | En P02 |
|---|---|---|
| Responsable de huerto | Define zonas, sensores y umbrales; anota decisiones. | Zonas, sensores y umbrales se cargan por SQL (`sql/02_seed.sql`); puede anotar con rol RESPONSABLE. |
| Observador | Captura lecturas manuales y anotaciones de campo. | Formulario `/lecturas` (POST) y `/anotaciones` con rol OBSERVADOR. |
| Coordinacion | Consulta historial, alertas y anotaciones. | `/lecturas`, `/alertas`, `/anotaciones` (GET); puede anotar con rol COORDINACION. |

P02 no incluye autenticacion (fuera del alcance de Web 1.0); el rol se declara en la anotacion y queda persistido con
restriccion `CHECK` en PostgreSQL. La autorizacion por rol en operaciones de cambio (RNF02) se abordara en Web 2.0/3.0.

## 3. Problema y objetivo (ficha PR09)

**Problema:** las observaciones ambientales de un huerto no se conservan con contexto (instante, unidad, procedencia)
ni permiten reconocer tendencias y alertas basicas. **Usuarios:** responsable de huerto, observador y coordinacion.

**Objetivo del incremento P02:** entregar el flujo principal *registrar y consultar lecturas con alerta automatica y
anotaciones* como WAR JSP/Servlet desplegado en Tomcat 9 con persistencia en PostgreSQL 16.

## 4. Alcance del incremento P02

**Incluye (alcance minimo de la ficha):** zonas (RF01), variables con unidad y rango fisico (RF02), lecturas con
instante, valor y procedencia (RF03), umbrales por sensor (RF04), historial (RF05), alertas automaticas y anotaciones
por rol (RF06), modelo relacionado de 7 entidades (RF07), ruta de salud, README y evidencia reproducible.

**Excluye (exclusiones de la ficha e incrementos posteriores):** control automatico de riego real, recomendaciones
agronomicas, hardware obligatorio, autenticacion, alta de zonas/sensores desde la interfaz, atencion de alertas,
graficas, API REST (RF08, Web 3.0) y simulador IoT (RF09, Web 4.0).

## 5. Flujo principal

1. El observador abre `/web1/lecturas`: ve sensores por zona y variable con su umbral, y el historial (GET).
2. Selecciona un sensor, captura el valor y una observacion opcional, y envia el formulario (POST).
3. El servidor valida: sensor existente y activo, valor numerico con maximo dos decimales, valor dentro del rango
   fisico de la variable, observacion de maximo 200 caracteres.
4. Si hay errores responde **400** con la lista de errores conservando lo capturado; no se inserta nada (CA02).
5. Si es valida inserta la lectura con `origen = 'manual'`; si el valor sale del umbral operativo inserta ademas una
   alerta BAJA o ALTA en la misma transaccion.
6. Responde **303** hacia `/web1/lecturas?creada=ID`; el GET muestra el mensaje, la nueva fila y el aviso de alerta.
   `/web1/alertas` lista las alertas y `/web1/anotaciones` permite a cualquiera de los tres roles anotar una zona (CA01).

## 6. Requisitos funcionales del PR09 y criterios de aceptacion en P02

| RF (C11) | Descripcion de la ficha | Criterio de aceptacion verificable en P02 |
|---|---|---|
| RF01 | Zonas | GET `/anotaciones` y `/lecturas` responden 200 y muestran las zonas (nombre, cultivo, ubicacion). |
| RF02 | Cultivos o variables | Cada sensor muestra su variable con unidad y rango fisico; la tabla `variable` tiene `CHECK (valor_minimo < valor_maximo)`. |
| RF03 | Lecturas | POST `/lecturas` valido -> 303 y fila en `lectura` con `origen='manual'` e instante; POST invalido (vacio, no numerico, fuera de rango fisico, sensor inexistente) -> 400 con mensaje y sin insertar. |
| RF04 | Umbrales | Cada sensor tiene un umbral [minimo, maximo] visible en el catalogo; `CHECK (minimo < maximo)`. |
| RF05 | Historial | GET `/lecturas` posterior al POST muestra la lectura nueva ordenada por instante; verificable con `psql`. |
| RF06 | Alertas y anotaciones | Una lectura fuera del umbral crea exactamente una alerta (BAJA/ALTA) visible en `/alertas`; POST `/anotaciones` valido -> 303 y fila en `anotacion` con rol valido; rol fuera de los tres o texto < 3 -> 400. |
| RF07 | Persistir y relacionar el modelo minimo | 7 tablas con FK, UNIQUE y CHECK; `sql/03_consultas_verificacion.sql` muestra conteos y joins. |
| RF08 | API Web 3.0 | Fuera de P02 (planeado). |
| RF09 | Fuente IoT simulada Web 4.0 | Fuera de P02; desde P02 la columna `origen` ya distingue `manual`/`simulado`. |

Criterios de aceptacion C11 seleccionados para P02: **CA01, CA02, CA05, CA06**. CA03 y CA04 corresponden a Web 3.0/4.0.

## 7. Restricciones y acuerdos

- Stack fijo del modulo: Java 11, Maven 3.9.9, Tomcat 9.0.115 (Servlet 4.0 / JSP 2.3, `javax`), PostgreSQL 16, JDBC con `PreparedStatement`.
- Sin integraciones externas ni frameworks adicionales (unica biblioteca de vista: JSTL 1.2).
- Credenciales solo por variables de entorno `DB_URL`, `DB_USER`, `DB_PASSWORD`; datos ficticios; sin rutas privadas en la evidencia.
- Maximo tres roles funcionales; cada commit identifica a su autor.
- La limpieza (`scripts/cleanup.sh`) solo afecta recursos locales declarados en el repositorio.

## 8. Riesgo principal (ficha PR09) y control

| Riesgo | Control en P02 | Comprobacion |
|---|---|---|
| Presentar simulacion como medicion real | Columna `lectura.origen` (`manual`/`simulado`) con `CHECK`, etiqueta visible en el historial, unidad junto a cada valor, datos declarados ficticios en README y vistas. | La semilla (simulada) y las capturas (manual) se distinguen en `/lecturas` y en `txt/17_postgres_estado_final.txt`. |
| Entorno no reproducible | `docker/docker-compose.yml` + `scripts/verify-module.sh` + README. | 18/18 comprobaciones VERIFICADO. |
| Credenciales en el codigo | `DbConfig` solo lee entorno; `.gitignore` excluye `setenv.*` y `.env`. | Revision del repositorio. |

Pruebas minimas de la ficha: validar unidad/rango (RF03, 400 por rango fisico), conservar tiempo (`registrado_en`
en cada lectura), activar alertas correctamente (38 C -> ALTA; 25.5 C -> sin alerta). Desactivar/atender alertas
queda para un incremento posterior (declarado).

## 9. Firmas

| Nombre | GitHub | Conformidad |
|---|---|---|
| Juan Pablo Kuri Ricardez | `juankuri` | 2026-09-11 |
| Pedro Garcia Padilla | `pedro-gar-pad` | 2026-09-11 |
| Alejandro Pacheco Luna | `zywoxxx` | 2026-09-11 |
| Ariadna Trejo Alvarez | `ariadna-19` | 2026-09-11 |
