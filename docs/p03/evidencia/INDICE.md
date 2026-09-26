# P03 - Indice de evidencia frente a R03

Producto de equipo DSW-E01: entrega en Eminus como `P03_EQUIPO_01`. Toda la evidencia de esta carpeta la genera
`CATALINA_HOME=... ./scripts/verify-module.sh M03` (salidas de texto) y, dentro de el, `scripts/pruebas_jsf.py`
(capturas y bitacora del recorrido en navegador). Las rutas locales se sustituyen por `<REPO>`, `<CATALINA_HOME>` y `<HOME>`.
La evidencia de P02 se conserva intacta en `docs/evidencia/`.

## R03.1 JSF y PrimeFaces (3 pts)

| Evidencia | Que demuestra | Archivo |
|---|---|---|
| Contenido del WAR | Mojarra 2.3.9, PrimeFaces 12.0.0, Weld 3.1.9, `beans.xml`, `faces-config.xml`, vistas `.xhtml`; ningun `.jsp` | `txt/03_war_contenido.txt` |
| Log de Tomcat | Arranque de Weld (CDI en servlets y filtros), Mojarra y PrimeFaces en `/web2` | `txt/05_tomcat_log.txt`, `txt/05_tomcat_despliegue.txt` |
| Pagina de acceso | Facelets con `p:inputText`, `p:password`, `p:commandButton`, `p:messages` | `txt/07_login_xhtml.txt`, `img/01_acceso.png` |
| Vista principal | Plantilla Facelets, `p:panel`, `p:selectOneMenu` con filtro, `p:dataTable` | `img/04_lecturas_inicial_observador.png` |
| AJAX parcial | `p:ajax` actualiza la info del sensor sin recargar | `img/05_ajax_info_sensor.png` |
| Codigo | `src/main/webapp/**/*.xhtml`, `src/main/java/mx/uv/dsw/huerto/web/*Bean.java`, `WEB-INF/web.xml`, `faces-config.xml`, `beans.xml` | repositorio |

## R03.2 Formularios, validaciones y componentes (3 pts)

| Evidencia | Que demuestra | Archivo |
|---|---|---|
| Lectura valida | Postback AJAX, mensaje de exito, fila nueva, formulario limpio | `img/06_lectura_valida_25_5.png` |
| Alertas ALTA y BAJA | Mensaje de advertencia y etiqueta en la fila | `img/07_lectura_38_alerta_alta.png`, `img/08_lectura_10_alerta_baja.png` |
| Limites 15 y 32 | Validas sin alerta | `img/09_limites_15_y_32_sin_alerta.png` |
| Valor vacio, no numerico, 150, 24.555, sin sensor | Errores por campo y globales; se conserva lo capturado; no se redondea | `img/10_valor_vacio.png`, `img/11_valor_no_numerico_conserva_entrada.png`, `img/12_valor_150_rango_fisico.png`, `img/13_valor_24_555_decimales.png`, `img/14_sin_sensor.png` |
| Anotaciones | Valida con rol de sesion, corta, larga (recorte del cliente), lectura inexistente | `img/18_*` a `img/20_*` |
| Sesion | Acceso directo sin sesion, credenciales incorrectas, cierre, expiracion durante AJAX | `img/02_*`, `img/03_*`, `img/21_*`, `img/22_*` |
| Roles | COORDINACION sin formulario de lecturas, anota con su rol | `img/23_*`, `img/24_*` |
| Pruebas unitarias | 21 casos (reglas, limites, anotaciones, autenticacion y permisos) | `txt/02_pruebas_unitarias.txt` |
| Bitacora del recorrido | Cada paso con hora, conteos antes/despues y resultado | `txt/pruebas_jsf.txt`, `txt/pruebas_jsf_resultados.txt` |

## R03.3 Persistencia PostgreSQL (2.5 pts)

| Evidencia | Que demuestra | Archivo |
|---|---|---|
| Esquema y conteos antes | 7 tablas, semilla | `txt/04_postgres_verificacion.txt` |
| Estado despues del recorrido | Lecturas `manual` con observacion `[prueba] P03 ...`, alertas y anotaciones nuevas | `txt/10_postgres_despues.txt` |
| Conteos por caso | En `txt/pruebas_jsf.txt`: cada entrada valida suma 1 y cada invalida deja la base igual | `txt/pruebas_jsf.txt` |
| Transaccion | Con la alerta bloqueada, la lectura tampoco queda | `img/25_transaccion_revertida.png` |
| Base no disponible | Mensaje claro, formulario oculto, recuperacion | `img/26_base_no_disponible.png` |
| Salud | `/health` con version de PostgreSQL 16 | `txt/06_health.txt` |

## R03.4 Experiencia de usuario (2 pts)

| Evidencia | Archivo |
|---|---|
| Navegacion clara con usuario y rol visibles, tarjetas, formulario en rejilla, mensajes en espanol | `img/04_*`, `img/06_*` |
| Unidad, rango y umbral antes de capturar; procedencia y alerta como etiquetas | `img/05_*`, `img/07_*` |
| Filtros por columna, orden, paginador y estado vacio con explicacion | `img/15_filtro_zona_invernadero.png`, `img/16_orden_por_valor.png` |
| Estados de error comprensibles (sesion, base caida, transaccion) | `img/21_*`, `img/22_*`, `img/25_*`, `img/26_*` |
| Estilos con contraste y diseno adaptable | `src/main/webapp/resources/css/huerto.css` |

## R03.5 Evidencia, README y repositorio (1.5 pts)

| Evidencia | Archivo |
|---|---|
| README con requisitos, configuracion, compilacion, despliegue, usuarios de prueba y verificacion | `README.md` |
| Arquitectura y decisiones | `docs/p03/arquitectura.md` |
| Trazabilidad P02 -> P03 -> R03 | `docs/p03/trazabilidad-r03.md` |
| Pruebas de aceptacion con estados | `docs/p03/pruebas-aceptacion.md` |
| Verificacion, limitaciones y contribuciones | `docs/p03/verificacion.md` |
| Bitacora (fallos diagnosticados durante la migracion) | `docs/bitacora.md` |
| Resumen de la verificacion reproducible | `txt/16_resumen.txt`, `txt/00_versiones.txt`, `txt/01_build.txt` |
