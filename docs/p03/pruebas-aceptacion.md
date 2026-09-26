# P03 - Pruebas de aceptacion

Tres capas de prueba, con el resultado declarado por separado:

- **Unitarias (JUnit 5, sin Tomcat ni base)**: 21 casos en `mvn package`. Reglas de lecturas (10), casos limite agregados en P03 (3), anotaciones (4) y autenticacion/permisos (4).
- **Navegador real (Playwright sobre Chromium)**: `scripts/pruebas_jsf.py`. Hace lo que haria una persona (entrar, elegir, capturar, leer mensajes) y comprueba en PostgreSQL con `psql` que la base cambio o no cambio. Los POST con `curl` de P02 no sirven aqui: un postback JSF necesita cookie de sesion, `ViewState`, identificadores de componentes y devuelve respuestas parciales.
- **Manuales**: las que no se pueden automatizar de forma honesta con las herramientas disponibles quedan marcadas.

Datos de referencia (semilla): sensor `SEN-A-TEMP-01`, rango fisico [-10, 60] C, umbral [15, 32] C.

## Casos, entrada y resultado esperado

| # | Caso | Como se ejecuta | Resultado esperado | Estado |
|---|---|---|---|---|
| 1 | Arranque JSF, beans CDI y recursos PrimeFaces | `GET /web2/` | Redirige a `login.xhtml`; la pagina carga `primefaces.js` y renderiza `p:inputText`/`p:password` | VERIFICADO |
| 1b | AJAX parcial | Elegir `SEN-A-TEMP-01` | Sin recargar, aparece "Temperatura ambiente ... unidad C ... rango fisico [-10.00, 60.00] ... umbral [15.00, 32.00]" | VERIFICADO |
| 2 | Lectura valida y consulta posterior | 25.5 | Mensaje "Lectura #N registrada", fila nueva con `manual`, formulario limpio, `lectura` +1, `alerta` igual | VERIFICADO |
| 3a | Alerta ALTA | 38 | Mensaje de alerta ALTA; `lectura` +1 y `alerta` +1; etiqueta ALTA en la fila | VERIFICADO |
| 3b | Alerta BAJA | 10 | Igual con BAJA | VERIFICADO |
| 3c | Vista de alertas | `/app/alertas.xhtml` | Lista ALTA y BAJA, filtro por nivel | VERIFICADO |
| 4 | Limites operativos exactos | 15 y 32 | Ambas validas, sin alerta | VERIFICADO (tambien en `LecturaValidatorLimitesTest`) |
| 5a | Campo vacio | valor en blanco | "El valor de la lectura es obligatorio"; conteos iguales | VERIFICADO |
| 5b | No numerico | `abc` | "debe ser numerico"; conteos iguales; el formulario conserva `abc` y la observacion | VERIFICADO |
| 6 | Fisicamente imposible | 150 | "fuera del rango fisico"; conteos iguales | VERIFICADO |
| 7 | Mas de dos decimales | 24.555 | "admite como maximo 2 decimales"; no se guarda 24.56 | VERIFICADO |
| 8 | Sensor inexistente / inactivo | Sin sensor elegido | "Debe seleccionar un sensor". Un sensor inexistente o inactivo no se puede elegir desde el `p:selectOneMenu` (solo lista activos); esas dos reglas se prueban con JUnit | VERIFICADO (UI) / NO_VERIFICADO por navegador para inexistente e inactivo |
| 9a | Anotacion valida | Cama A + texto | Mensaje con el rol OBSERVADOR; fila con etiqueta OBSERVADOR; `anotacion` +1 | VERIFICADO |
| 9b | Anotacion corta | `ok` | "al menos 3 caracteres"; sin cambios | VERIFICADO |
| 9c | Anotacion larga | 301 caracteres inyectados en el DOM | PrimeFaces recorta a 300 en el cliente (`maxlength`) y el servidor acepta 300. La regla `>300 -> rechazo` del servidor se comprueba en `AnotacionValidatorTest.textoInvalido` | VERIFICADO con esa aclaracion |
| 9d | Referencia invalida | lectura 999999 | "La lectura #999999 no existe."; sin cambios | VERIFICADO |
| 10 | Filtros, orden y paginacion | Filtro Zona = Invernadero 1; clic en columna Valor | El historial se reduce (0 filas: la semilla solo tiene lecturas en Cama A) y muestra el mensaje de "ninguna coincide"; el paginador esta presente; la columna ordena | VERIFICADO (con menos de 10 filas por pagina no hay segunda pagina que recorrer; se verifico la presencia del paginador y el cambio de filas por pagina en el control) |
| 11a | Acceso directo sin sesion | `GET /app/lecturas.xhtml` | 302 a `login.xhtml?expirada=1` | VERIFICADO |
| 11b | Credenciales incorrectas | contrasena mala | "Usuario o contrasena incorrectos." | VERIFICADO |
| 11c | Sesion valida | observador | Cabecera con usuario y rol; catalogo e historial cargados | VERIFICADO |
| 11d | Cierre de sesion | boton Salir | `login.xhtml?salida=1`; `/app` vuelve a pedir acceso | VERIFICADO |
| 11e | Sesion expirada durante AJAX | se borran las cookies y se envia el formulario | Redireccion al acceso; la base no cambia | VERIFICADO |
| 12 | Accion no permitida por rol | coordinacion | No hay formulario de lecturas y se explica por que; la anotacion se firma COORDINACION | VERIFICADO (el rechazo en servidor de un POST forjado no se ejercio; esta en `LecturaBean.guardar` y `AuthServiceTest.permisosPorRol`) |
| 13 | Base de datos no disponible | `docker stop` del contenedor | "Base de datos no disponible" y sin formulario; al arrancar la base, vuelve a funcionar | VERIFICADO |
| 14 | Fallo de transaccion | restriccion temporal `NOT VALID` que impide insertar alertas ALTA; lectura 40 | "Error de persistencia"; `lectura` y `alerta` sin cambios (no queda la lectura sin su alerta) | VERIFICADO |
| 15 | Reenvio del formulario | F5 despues de guardar | Conteos iguales: el envio fue AJAX y recargar solo hace GET | VERIFICADO |

## Pendientes y limites declarados

- Caducidad por tiempo real (20 minutos de inactividad): se probo el efecto (sesion ausente durante un envio AJAX), no la espera de 20 minutos. NO_VERIFICADO por tiempo; PENDIENTE como prueba manual.
- Despliegue en Linux/macOS con `setenv.sh`: NO_VERIFICADO (solo Windows).
- Reproduccion completa por otro integrante en una maquina limpia: PENDIENTE.
- Paginacion con mas de 10 lecturas: el control existe y funciona en la interfaz, pero el recorrido automatizado no llega a una segunda pagina; PENDIENTE como prueba manual (basta registrar mas lecturas o elegir 10 filas por pagina con mas de 10 registros).
