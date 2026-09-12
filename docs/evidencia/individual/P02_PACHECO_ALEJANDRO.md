# Evidencia individual P02 - P02_PACHECO_ALEJANDRO

| Campo | Valor |
|---|---|
| Integrante | Alejandro Pacheco Luna |
| Usuario GitHub | `zywoxxx` |
| Responsabilidad en el equipo | Evidencia y documentacion (capturas, protocolo de pruebas, README, indice R02), compartida con Ariadna Trejo Alvarez |
| Proyecto | PR09 - Monitoreo de huerto o ambiente (C11), seleccionado en F02 |
| Actividad | P02 - Aplicacion Web 1.0 con JSP, Tomcat y PostgreSQL |

## 1. Contribucion concreta

- Diseno del **protocolo de pruebas HTTP** (GET inicial, POST valido, POST invalido x3, POST con alerta, GET con persistencia, GET alertas, GET/POST anotaciones) y su automatizacion en `scripts/verify-module.sh`, que deja cada respuesta cruda en `docs/evidencia/txt/` y termina con 18/18 VERIFICADO.
- Automatizacion de las **13 capturas de pantalla** con un navegador real (`scripts/capturas.py`), de modo que cada imagen corresponde a una fila verificable en PostgreSQL (`txt/17_postgres_estado_final.txt`).
- Redaccion del **indice de evidencia** (`docs/evidencia/INDICE.md`) que relaciona cada archivo con un criterio de R02, la **bitacora** con los fallos diagnosticados y el **reporte de verificacion** con estados VERIFICADO / NO_VERIFICADO / PENDIENTE.
- Revision de la ficha PR09 (C11) contra el codigo y registro del desajuste inicial (entidades, numeracion de RF y roles funcionales) en la bitacora (#13).
- Anonimizacion de rutas locales en la evidencia (`scripts/anonimizar_evidencia.py`) para cumplir la restriccion "sin rutas privadas".

## 2. Decisiones que puedo explicar (M02 / C11)

1. **Por que la evidencia es texto + captura y no solo captura.** M02 advierte que una captura sin comando, contexto ni salida no es evidencia. Cada captura tiene su equivalente en texto con el codigo HTTP (`txt/08_post_valido.txt` muestra `HTTP/1.1 303` y `Location: /web1/lecturas?creada=N`), y el estado de la base se consulta con `psql` despues del recorrido.
2. **Por que el POST valido responde 303 y no 200.** Patron POST-Redirect-GET: evita reenvios duplicados al refrescar y hace que "GET con persistencia" sea una peticion independiente que prueba que el dato esta en PostgreSQL y no en memoria.
3. **Por que hay dos validaciones negativas distintas.** "150 C" se rechaza por rango fisico de la variable (400, no se guarda, CA02); "38 C" se acepta pero genera alerta por umbral (303 + fila en `alerta`, CA01). Asi se demuestra que las reglas viven en clases Java (`LecturaValidator`, `LecturaService`), no en la JSP.
4. **Como se controla el riesgo principal de la ficha** ("presentar simulacion como medicion real"): la columna `lectura.origen` etiqueta `manual`/`simulado` con `CHECK`, la etiqueta se ve en el historial y las capturas muestran la semilla como `simulado` y las lecturas del observador como `manual`.
5. **Que protege la evidencia.** No contiene credenciales (solo variables `DB_*` de laboratorio), ni datos reales, ni rutas de usuario (se sustituyen por `<REPO>`, `<HOME>`).

## 3. Un fallo que diagnostique

La primera corrida de `verify-module.sh` dio 10 NO_VERIFICADO: el script copiaba el WAR y consultaba `/lecturas` antes de que Tomcat terminara de replegar y desplegar el contexto (autoDeploy tarda unos segundos), lo que produjo un 404 y un 500 transitorios. La correccion fue esperar a que `/health` devolviera 404 tras retirar el WAR y 200 tras copiarlo. Esta registrado en `docs/bitacora.md` (#8) y no se borro la evidencia del fallo. Un segundo hallazgo (#13): el modelo inicial no coincidia con las entidades de la ficha PR09; se alineo antes de generar la evidencia final.

## 4. Alternativa y limitacion

- **Alternativa:** capturar manualmente con el navegador. Se descarto porque no es repetible y no deja rastro del comando; el script permite regenerar las 13 capturas en segundos tras cualquier cambio.
- **Limitacion:** las capturas se generaron en Windows; la ejecucion en Linux con `setenv.sh` queda NO_VERIFICADA. El script de capturas necesita Python y Playwright, que no forman parte del WAR.

## 5. Autoevaluacion (P02)

- [x] Mi evidencia corresponde a P02, M02 y R02 (ver `docs/evidencia/INDICE.md`).
- [x] Otra persona puede reconstruir el resultado con `README.md` + `scripts/verify-module.sh`.
- [x] Inclui comprobaciones positivas (POST 25.5 / 38, anotacion OBSERVADOR) y negativas (abc, vacio, 150, sensor 999, rol ADMIN, BD detenida).
- [x] No inclui secretos, datos reales ni rutas privadas.
- [x] Puedo explicar decisiones, errores y mi contribucion individual.
