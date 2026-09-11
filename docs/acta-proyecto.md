# Acta breve de proyecto - PRxx Monitoreo de huerto o ambiente

| Campo | Valor |
|---|---|
| Experiencia educativa | Desarrollo de Sistemas Web (DSW-19559 / NRC 19559) |
| Proyecto del banco | **PRxx - Monitoreo de huerto o ambiente** (identificador confirmado en F02; sustituir `xx` por el numero asignado al equipo) |
| Actividad | P02 - Aplicacion Web 1.0 con JSP, Tomcat y PostgreSQL (primer incremento) |
| Instrumento | R02 (10 puntos) |
| Fecha del acta | 2026-09-11 |
| Repositorio | `dsw-p02-monitoreo-huerto` (GitHub: usuario `zywoxxx`) |

## 1. Equipo y roles (maximo tres)

| Rol | Responsabilidad en P02 | Integrante |
|---|---|---|
| R1 - Desarrollo web (JSP/Servlet) | Controladores, vistas JSP, servicio de validacion, empaquetado WAR y despliegue en Tomcat 9. | *(nombre por confirmar por el equipo)* |
| R2 - Datos (PostgreSQL) | Modelo de 7 entidades, scripts SQL de esquema, semilla, verificacion y limpieza; repositorios JDBC parametrizados. | *(nombre por confirmar por el equipo)* |
| R3 - Evidencia y documentacion | Capturas del flujo principal, validaciones positivas y negativas, protocolo HTTP, README, bitacora e indice de evidencia frente a R02. | Alejandro (GitHub `zywoxxx`) |

Los tres roles revisan el codigo de los demas; ningun integrante entrega sin evidencia individual atribuible.

## 2. Problema y objetivo

Un huerto escolar o ambiente controlado necesita registrar mediciones (temperatura, humedad de suelo,
humedad relativa, luminosidad) y detectar cuando una medicion sale del rango operativo deseado.
El objetivo del PRxx es una aplicacion web que centralice sensores, lecturas, umbrales y alertas.

**Objetivo del incremento P02:** entregar el flujo principal *registrar y consultar lecturas con alerta
automatica* como WAR JSP/Servlet desplegado en Tomcat 9 con persistencia en PostgreSQL 16.

## 3. Alcance del incremento P02

**Incluye**
- Catalogo de sensores activos con zona, huerto, rango fisico y umbral (RF-01).
- Registro manual de una lectura por formulario (RF-02) con validacion positiva/negativa (RF-03).
- Listado de lecturas recientes con persistencia (RF-04).
- Generacion automatica de alerta cuando la lectura excede el umbral (RF-05) y su consulta (RF-06).
- Ruta de salud que comprueba la conexion a PostgreSQL (RF-07).
- Modelo de datos de 7 entidades, scripts SQL, README, evidencia reproducible.

**No incluye (incrementos posteriores)**
- Autenticacion de usuarios y roles de acceso.
- Alta/baja de huertos, zonas y sensores desde la interfaz (se cargan por SQL).
- Atencion/cierre de alertas y graficas historicas.
- Ingesta automatica desde dispositivos o simuladores (llegara con la API del modulo correspondiente).

## 4. Flujo principal

1. El operador abre `/web1/lecturas` y ve el catalogo de sensores y las lecturas recientes (GET).
2. Selecciona un sensor, captura el valor medido y una observacion opcional, y envia el formulario (POST).
3. El servidor valida: sensor seleccionado y existente, valor numerico con maximo dos decimales,
   valor dentro del rango fisico del tipo de sensor, observacion de maximo 200 caracteres.
4. Si hay errores, responde **400** y muestra la lista de errores conservando lo capturado.
5. Si es valida, inserta la lectura; si el valor sale del umbral operativo del sensor, inserta ademas
   una alerta (BAJA o ALTA) en la misma transaccion.
6. Responde **303** (POST-Redirect-GET) hacia `/web1/lecturas?creada=ID`; el GET muestra el mensaje de
   exito, la nueva fila y, si aplica, el aviso de alerta. `/web1/alertas` lista las alertas generadas.

## 5. Requisitos funcionales prioritarios y criterios de aceptacion

| RF | Descripcion | Criterio de aceptacion |
|---|---|---|
| RF-01 | Consultar catalogo de sensores activos | GET `/lecturas` responde 200 y muestra codigo, tipo, unidad, zona, huerto, rango fisico y umbral de cada sensor activo. |
| RF-02 | Registrar lectura manual | POST `/lecturas` con sensor valido y valor en rango responde 303 y la lectura queda en la tabla `lectura` con `origen='manual'`. |
| RF-03 | Validar la lectura | POST con valor vacio, no numerico, con mas de dos decimales, fuera del rango fisico, sensor vacio/inexistente/inactivo u observacion > 200 responde 400 con mensajes especificos y **no** inserta nada. |
| RF-04 | Consultar lecturas recientes | GET `/lecturas` posterior al POST muestra la lectura nueva (persistencia verificable tambien con `psql`). |
| RF-05 | Generar alerta automatica | Una lectura fuera de `[umbral.minimo, umbral.maximo]` crea exactamente una fila en `alerta` con nivel BAJA o ALTA y mensaje descriptivo; una lectura en rango no crea alerta. |
| RF-06 | Consultar alertas | GET `/alertas` responde 200 y lista las alertas con sensor, valor, nivel, mensaje y fecha. |
| RF-07 | Ruta de salud | GET `/health` responde 200 con `db=UP` y version de PostgreSQL; 503 si faltan variables o la base no responde. |

## 6. Restricciones y acuerdos

- Tecnologias fijas del modulo: Java 11, Maven 3.9.9, Tomcat 9.0.115 (Servlet 4.0 / JSP 2.3, espacio `javax`), PostgreSQL 16, JDBC con `PreparedStatement`.
- Sin integraciones externas ni frameworks adicionales (unica biblioteca de vista: JSTL 1.2).
- Credenciales solo por variables de entorno `DB_URL`, `DB_USER`, `DB_PASSWORD`; el repositorio no contiene secretos ni datos reales.
- Maximo tres roles; cada commit identifica a su autor.
- La limpieza (`scripts/cleanup.sh`) solo afecta recursos locales declarados en el repositorio.

## 7. Riesgos identificados

| Riesgo | Mitigacion en P02 |
|---|---|
| Entorno no reproducible en otra maquina | `docker/docker-compose.yml` + `scripts/verify-module.sh` + README paso a paso. |
| Mezcla de `javax` y `jakarta` | Dependencias fijadas a Servlet 4.0.1 y Tomcat 9; documentado en README. |
| Credenciales en el codigo | `DbConfig` solo lee entorno; `.gitignore` excluye `setenv.*` y `.env`. |
| Evidencia no atribuible | Bitacora con fecha/comando/resultado, indice de evidencia y explicacion individual por rol. |

## 8. Firmas

| Rol | Nombre | Conformidad |
|---|---|---|
| R1 | | |
| R2 | | |
| R3 | Alejandro (`zywoxxx`) | 2026-09-11 |
