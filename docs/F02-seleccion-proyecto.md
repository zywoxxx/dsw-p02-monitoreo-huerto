# F02 - Seleccion y delimitacion del proyecto integrador

Publicacion del equipo en el foro F02 (formativo, 0 puntos; 24 al 30 de agosto de 2026) segun la plantilla de C11.
Banco consultado: C11 *Banco de proyectos integradores* (10 fichas PR01-PR10). Solo datos ficticios.

## Comparacion de al menos tres opciones

| Criterio (C11) | PR09 Monitoreo de huerto o ambiente | PR03 Monitoreo de laboratorio de computo | PR01 Control de inventario inteligente |
|---|---|---|---|
| Problema | Observaciones ambientales sin contexto ni alertas basicas. | Incidencias y condiciones ambientales sin relacion con equipos ni mantenimiento. | Existencias dispersas; faltantes detectados tarde. |
| Usuarios (3 roles) | Responsable de huerto, observador, coordinacion. | Encargado de laboratorio, soporte tecnico, coordinacion. | Responsable de almacen, captura, coordinacion. |
| Datos (entidades) | zona, variable, lectura, umbral, alerta, anotacion (6). | equipo, laboratorio, incidencia, lectura, alerta, usuario (6). | producto, movimiento, categoria, usuario, lectura_sensor (5). |
| Complejidad orientativa | Media. | Media-alta. | Media. |
| IoT Web 4.0 | Temperatura/humedad simulada por eventos periodicos: directa y sin hardware. | Temperatura, humedad o consumo electrico simulado. | Temperatura de almacen o nivel de stock simulado. |
| Riesgo principal | Presentar simulacion como medicion real. Control: etiquetar procedencia, unidad y estado simulado. | Usar telemetria para vigilar personas. | Alteracion de existencias; requiere autorizacion por rol y bitacora inmutable. |
| Conocimiento del equipo | Alto: variables fisicas sencillas y reglas de umbral claras. | Medio: mezcla inventario + incidencias + telemetria. | Medio: reglas de inventario (existencia calculada, salidas mayores a existencia). |
| Decision | **Opcion principal.** | **Segunda opcion** (mismo patron lectura/umbral/alerta). | Descartada: el riesgo exige autorizacion por rol y bitacora inmutable desde P02. |

Decision redactada: *Seleccionamos PR09 porque podemos demostrar lecturas, umbrales, alertas y anotaciones con datos
sinteticos y sin hardware, con un modelo de 7 entidades que cabe en el periodo; excluimos riego automatico y
recomendaciones agronomicas. Si PR09 no se confirma, tomamos PR03, que comparte el patron lectura-umbral-alerta.*

## Plantilla de publicacion

```
Equipo: EQUIPO_NN (sustituir por el numero asignado)
Integrantes: Alejandro Pacheco Luna (zywoxxx), Juan Pablo Kuri Ricardez (juankuri),
             Ariadna Trejo Alvarez (ariadna-19), Pedro Garcia Padilla (pedro-gar-pad)
Proyecto solicitado: PR09 - Monitoreo de huerto o ambiente
Segunda opcion: PR03 - Monitoreo de laboratorio de computo

Problema y usuarios:
  Un huerto escolar registra observaciones ambientales (temperatura, humedad de suelo, humedad relativa,
  luminosidad) en libretas y mensajes sueltos, sin instante, unidad ni procedencia; no se reconocen tendencias
  ni se avisa cuando una variable sale del rango operativo. Usuarios (tres roles funcionales): responsable de
  huerto (define zonas y umbrales), observador (captura lecturas y anotaciones), coordinacion (consulta
  historial y alertas). Todos los datos son ficticios.

Alcance minimo:
  Zonas del huerto; variables con unidad y rango fisico; sensores por zona; lecturas con instante, valor y
  procedencia (manual o simulado); umbral operativo por sensor; historial de lecturas; alertas automaticas
  (BAJA/ALTA) y anotaciones por rol.
  Exclusiones: control automatico de riego real, recomendaciones agronomicas, hardware obligatorio,
  autenticacion avanzada. Posibles ampliaciones (no comprometidas): atencion de alertas, graficas historicas.

Flujo principal y resultado observable:
  El observador abre /lecturas, elige un sensor y captura un valor. El sistema valida (sensor existente,
  valor numerico con 2 decimales, dentro del rango fisico de la variable), guarda la lectura etiquetada
  como "manual" y, si sale del umbral, crea una alerta en la misma transaccion. Resultado observable: la
  lectura aparece en el historial, la alerta en /alertas y ambas filas en PostgreSQL.

RF prioritarios que implementara primero (P02, Web 1.0):
  RF01 Zonas, RF02 variables, RF03 lecturas, RF04 umbrales, RF05 historial, RF06 alertas y anotaciones,
  RF07 persistencia relacionada del modelo. RF08 (API) en Web 3.0 y RF09 (IoT simulado) en Web 4.0.

Datos principales en PostgreSQL (7 entidades):
  zona, variable, sensor (extension justificada: dispositivo que mide una variable en una zona y sera la
  fuente IoT simulada), umbral, lectura, alerta, anotacion. Llaves foraneas, UNIQUE y CHECK
  (rangos, origen IN manual/simulado, nivel IN BAJA/ALTA, rol IN los tres roles funcionales).

Evolucion prevista Web 1.0 a Web 4.0:
  Web 1.0 (P02): JSP/Servlet en Tomcat 9: captura manual de lecturas, historial, alertas y anotaciones.
  Web 2.0: formularios y tablas JSF/PrimeFaces con validacion en componentes y filtros por zona/variable.
  Web 3.0: API Spring Boot (/health, GET lecturas, POST lectura con 2xx/4xx) y dashboard Angular.
  Web 4.0: simulador que publica lecturas periodicas etiquetadas como "simulado" con dispositivo, instante,
  variable, unidad y valor; las alertas se generan por el mismo umbral.

Fuente o simulacion IoT:
  Simulacion, sin hardware. Cada evento incluye codigo de sensor (dispositivo), instante, variable,
  unidad y valor, y se etiqueta origen = 'simulado'. Nunca se presenta como medicion real.

Riesgo principal y control inicial:
  Presentar simulacion como medicion real. Control desde P02: columna lectura.origen (manual/simulado)
  visible en la interfaz, unidad siempre junto al valor, datos ficticios declarados en README.

Criterios de aceptacion seleccionados (C11):
  CA01 flujo principal completo con cambio persistido (P02), CA02 caso invalido rechazado con mensaje
  y sin alterar datos (P02), CA05 otra persona reproduce con el README (P02), CA06 autoria y
  contribucion individual (P02). CA03 (API 2xx/4xx) y CA04 (evento IoT) se cumpliran en Web 3.0 y 4.0.

Repositorio del equipo, si ya existe:
  https://github.com/zywoxxx/dsw-p02-monitoreo-huerto
```

## Estado

- Publicado en F02 dentro de la ventana (24-30 de agosto de 2026).
- Confirmacion del facilitador: **registrar aqui la fecha y el texto de la respuesta en F02** cuando se reciba o
  si ya se recibio (la seleccion solo se considera confirmada mediante esa respuesta).
- El identificador PR09 se conserva en P02-P08; cualquier cambio de alcance se justificara en el mismo foro.
