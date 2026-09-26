"""
pruebas_jsf.py - Recorrido de aceptacion de P03 con un navegador real (Chromium via Playwright).

Los formularios JSF no se prueban con curl: hay ViewState, cookies de sesion, identificadores de
componentes y respuestas parciales AJAX. Este script hace lo que haria una persona: entra, captura,
lee los mensajes y comprueba en PostgreSQL que la base cambio (o no cambio) como corresponde.

Salida:
  docs/p03/evidencia/img/*.png              capturas de cada estado
  docs/p03/evidencia/txt/pruebas_jsf.txt    bitacora paso a paso
  docs/p03/evidencia/txt/pruebas_jsf_resultados.txt   VERIFICADO / NO_VERIFICADO por caso
Codigo de salida 1 si algun caso queda NO_VERIFICADO.

Variables: BASE_URL (http://localhost:8080/web2), PSQL_CMD (docker exec ... psql ...),
           DOCKER (ruta a docker.exe), SKIP_DB_DOWN=1 y SKIP_TX_TEST=1 para omitir esos casos.
Requisitos: python -m pip install playwright && python -m playwright install chromium
"""
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from playwright.sync_api import TimeoutError as PWTimeout, sync_playwright

ROOT = Path(__file__).resolve().parent.parent
BASE = os.environ.get("BASE_URL", "http://localhost:8080/web2")
PSQL = os.environ.get("PSQL_CMD", "docker exec -i dsw-p02-huerto-db psql -U huerto_app -d huerto_db")
DOCKER = os.environ.get("DOCKER", "docker")
IMG = ROOT / "docs" / "p03" / "evidencia" / "img"
TXT = ROOT / "docs" / "p03" / "evidencia" / "txt"
IMG.mkdir(parents=True, exist_ok=True)
TXT.mkdir(parents=True, exist_ok=True)

USUARIOS = {"observador": "Observador#2026", "responsable": "Responsable#2026", "coordinacion": "Coordinacion#2026"}
SENSOR = "SEN-A-TEMP-01"   # rango fisico [-10, 60], umbral [15, 32]

bitacora = open(TXT / "pruebas_jsf.txt", "w", encoding="utf-8")
resultados = []


def log(msg):
    linea = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(linea)
    bitacora.write(linea + "\n")
    bitacora.flush()


def resultado(nombre, ok, detalle=""):
    estado = "VERIFICADO" if ok else "NO_VERIFICADO"
    resultados.append((estado, nombre, detalle))
    log(f"{estado}: {nombre}" + (f" -> {detalle}" if detalle else ""))


def psql(sql):
    out = subprocess.run(PSQL.split() + ["-Atc", sql], capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip())
    return out.stdout.strip()


def conteos():
    return tuple(int(psql(f"select count(*) from {t}")) for t in ("lectura", "alerta", "anotacion"))


def captura(page, nombre):
    ruta = IMG / f"{nombre}.png"
    page.screenshot(path=str(ruta), full_page=True)
    log(f"captura {ruta.name}")


def mensajes(page):
    page.wait_for_selector("#mensajes", state="attached", timeout=10000)
    return page.inner_text("#mensajes").strip()


def limpiar_mensajes(page):
    """Vacia el contenedor de mensajes para que la siguiente espera lea solo la respuesta nueva."""
    page.evaluate("() => { const m = document.querySelector('#mensajes'); if (m) m.innerHTML = ''; }")


def esperar_mensaje(page, texto, timeout=15000):
    page.wait_for_function(
        "t => { const m = document.querySelector('#mensajes'); return m && m.innerText.includes(t); }",
        arg=texto, timeout=timeout)
    return mensajes(page)


def login(page, usuario):
    page.goto(f"{BASE}/login.xhtml")
    page.fill("[id='formAcceso:usuario']", usuario)
    page.fill("[id='formAcceso:contrasena']", USUARIOS[usuario])
    page.click("[id='formAcceso:btnEntrar']")
    page.wait_for_url("**/app/lecturas.xhtml", timeout=20000)


def elegir_sensor(page, codigo):
    page.click("[id='formLectura:sensor']")
    page.click(f"[id='formLectura:sensor_items'] li:has-text('{codigo}')")
    page.wait_for_function(
        "() => document.querySelector('#formLectura\\\\:infoSensor').innerText.includes('umbral operativo')", timeout=10000)


def registrar(page, valor, observacion=None, sensor=SENSOR):
    if sensor:
        elegir_sensor(page, sensor)
    page.fill("[id='formLectura:valor']", valor)
    if observacion is not None:
        page.fill("[id='formLectura:observacion']", observacion)
    limpiar_mensajes(page)
    page.click("[id='formLectura:btnGuardar']")
    page.wait_for_function(
        "() => document.querySelector('#mensajes') && document.querySelector('#mensajes').innerText.trim().length > 0",
        timeout=20000)
    page.wait_for_timeout(400)
    return mensajes(page)


def filas_tabla(page, id_data):
    return page.locator(f"[id='{id_data}'] tr[data-ri]").count()


def elegir_filtro(page, indice, etiqueta):
    """Abre el n-esimo selectOneMenu de filtro del encabezado de la tabla y elige una opcion."""
    menus = page.locator("[id='formTabla:tablaLecturas'] thead .ui-selectonemenu")
    menus.nth(indice).click()
    page.locator(".ui-selectonemenu-items-wrapper:visible li").filter(has_text=etiqueta).first.click()
    page.wait_for_timeout(800)


def main():
    try:
        return recorrido()
    finally:
        escribir_resultados()


def escribir_resultados():
    fallos = sum(1 for e, _, _ in resultados if e != "VERIFICADO")
    with open(TXT / "pruebas_jsf_resultados.txt", "w", encoding="utf-8") as f:
        f.write(f"pruebas_jsf.py - {datetime.now().isoformat(timespec='seconds')} - {BASE}\n")
        for estado, nombre, detalle in resultados:
            f.write(f"{estado:14}| {nombre}" + (f" ({detalle})" if detalle else "") + "\n")
        f.write(f"Fallos: {fallos}\n")
    log(f"Fallos: {fallos}")
    bitacora.flush()


def recorrido():
    log(f"Inicio de pruebas P03 contra {BASE}")
    log(f"Version de PostgreSQL: {psql('select version()')[:40]}")
    inicial = conteos()
    log(f"Conteos iniciales lectura/alerta/anotacion: {inicial}")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1280, "height": 900}, locale="es-MX")
        page = ctx.new_page()

        # 1. Arranque: index redirige al acceso y la pagina carga recursos de PrimeFaces
        page.goto(f"{BASE}/")
        page.wait_for_url("**/login.xhtml", timeout=15000)
        html = page.content()
        ok = "primefaces" in html.lower() and page.locator("[id='formAcceso:btnEntrar']").count() == 1
        captura(page, "01_acceso")
        resultado("1 Arranque JSF: index -> login.xhtml con recursos PrimeFaces", ok)

        # 2. Acceso directo sin sesion
        r = page.goto(f"{BASE}/app/lecturas.xhtml")
        ok = "login.xhtml" in page.url and "expirada=1" in page.url
        captura(page, "02_acceso_directo_sin_sesion")
        resultado("11a Acceso directo a /app sin sesion redirige al acceso", ok, page.url)

        # 3. Credenciales incorrectas
        page.fill("[id='formAcceso:usuario']", "observador")
        page.fill("[id='formAcceso:contrasena']", "incorrecta")
        page.click("[id='formAcceso:btnEntrar']")
        page.wait_for_selector("#mensajes .ui-messages-error", timeout=15000)
        ok = "incorrectos" in mensajes(page)
        captura(page, "03_acceso_credenciales_incorrectas")
        resultado("11b Credenciales incorrectas se rechazan con mensaje", ok)

        # 4. Sesion valida como observador
        login(page, "observador")
        ok = "observador" in page.inner_text(".usuario") and "OBSERVADOR" in page.inner_text(".usuario")
        page.locator("[id='formCatalogo'] .ui-panel-titlebar-icon").first.click()
        page.wait_for_timeout(600)
        filas_sensores = filas_tabla(page, "formCatalogo:tablaSensores_data")
        filas_hist = filas_tabla(page, "formTabla:tablaLecturas_data")
        captura(page, "04_lecturas_inicial_observador")
        resultado("11c Sesion valida: cabecera con usuario y rol; catalogo e historial cargados",
                  ok and filas_sensores >= 5 and filas_hist >= 1, f"sensores={filas_sensores} lecturas={filas_hist}")

        # 5. AJAX: al elegir sensor se muestra unidad, rango y umbral
        elegir_sensor(page, SENSOR)
        info = page.inner_text("[id='formLectura:infoSensor']")
        ok = "[15.00, 32.00]" in info and "[-10.00, 60.00]" in info and "C" in info
        captura(page, "05_ajax_info_sensor")
        resultado("1b AJAX parcial: info del sensor (unidad, rango fisico, umbral) sin recargar", ok, info[:80])

        # 6. Lectura valida sin alerta
        antes = conteos()
        m = registrar(page, "25.5", "[prueba] P03 lectura valida", sensor=None)
        despues = conteos()
        fila = page.locator("[id='formTabla:tablaLecturas_data'] tr[data-ri]").first.inner_text()
        ok = ("registrada" in m and "Alerta" not in m and despues[0] == antes[0] + 1 and despues[1] == antes[1]
              and "25.50" in fila and "manual" in fila and page.input_value("[id='formLectura:valor']") == "")
        captura(page, "06_lectura_valida_25_5")
        resultado("2 Lectura valida 25.5: mensaje, fila nueva con procedencia manual, formulario limpio, +1 en lectura",
                  ok, f"conteos {antes}->{despues}")

        # 7. Reenvio: recargar la pagina tras guardar no duplica
        page.reload()
        page.wait_for_selector("[id='formTabla:tablaLecturas_data']")
        tras_reload = conteos()
        resultado("15 Recargar la pagina despues de guardar no reenvia el formulario", tras_reload == despues,
                  f"conteos {tras_reload}")

        # 8. Alerta ALTA
        antes = conteos()
        m = registrar(page, "38", "[prueba] P03 alerta alta")
        despues = conteos()
        fila = page.locator("[id='formTabla:tablaLecturas_data'] tr[data-ri]").first.inner_text()
        ok = "ALTA" in m and despues[0] == antes[0] + 1 and despues[1] == antes[1] + 1 and "ALTA" in fila
        captura(page, "07_lectura_38_alerta_alta")
        resultado("3a Lectura 38: valida, genera alerta ALTA (+1 lectura, +1 alerta)", ok, f"{antes}->{despues}")

        # 9. Alerta BAJA
        antes = conteos()
        m = registrar(page, "10", "[prueba] P03 alerta baja")
        despues = conteos()
        ok = "BAJA" in m and despues[0] == antes[0] + 1 and despues[1] == antes[1] + 1
        captura(page, "08_lectura_10_alerta_baja")
        resultado("3b Lectura 10: valida, genera alerta BAJA", ok, f"{antes}->{despues}")

        # 10. Limites exactos del umbral: 15 y 32 sin alerta
        antes = conteos()
        m1 = registrar(page, "15", "[prueba] P03 limite inferior")
        m2 = registrar(page, "32", "[prueba] P03 limite superior")
        despues = conteos()
        ok = ("registrada" in m1 and "registrada" in m2 and "Alerta" not in m1 and "Alerta" not in m2
              and despues[0] == antes[0] + 2 and despues[1] == antes[1])
        captura(page, "09_limites_15_y_32_sin_alerta")
        resultado("4 Valores exactamente en el umbral (15 y 32): validos y sin alerta", ok, f"{antes}->{despues}")

        # 11. Campo vacio
        antes = conteos()
        m = registrar(page, "", None)
        ok = "obligatorio" in m and conteos() == antes
        captura(page, "10_valor_vacio")
        resultado("5a Valor vacio: rechazado con mensaje y sin cambios en la base", ok)

        # 12. No numerico y conservacion de lo capturado
        m = registrar(page, "abc", "[prueba] se conserva la observacion")
        conserva = (page.input_value("[id='formLectura:valor']") == "abc"
                    and "se conserva" in page.input_value("[id='formLectura:observacion']"))
        ok = "numerico" in m and conteos() == antes and conserva
        captura(page, "11_valor_no_numerico_conserva_entrada")
        resultado("5b Entrada no numerica: rechazada, sin cambios y se conserva lo capturado", ok, f"conserva={conserva}")

        # 13. Fuera del rango fisico
        m = registrar(page, "150", "[prueba] rango fisico")
        ok = "rango fisico" in m and conteos() == antes
        captura(page, "12_valor_150_rango_fisico")
        resultado("6 Valor fisicamente imposible (150 C): rechazado sin tocar PostgreSQL", ok)

        # 14. Tres decimales sin redondeo
        m = registrar(page, "24.555", "[prueba] decimales")
        ok = "decimales" in m and conteos() == antes
        captura(page, "13_valor_24_555_decimales")
        resultado("7 Tres decimales (24.555): rechazado, no se redondea a 24.56", ok)

        # 15. Sin sensor seleccionado
        page.reload()
        page.wait_for_selector("[id='formLectura:valor']")
        page.fill("[id='formLectura:valor']", "20")
        limpiar_mensajes(page)
        page.click("[id='formLectura:btnGuardar']")
        m = esperar_mensaje(page, "sensor")
        ok = "seleccionar un sensor" in m and conteos() == antes
        captura(page, "14_sin_sensor")
        resultado("8 Sin sensor seleccionado: rechazado (sensor inexistente/inactivo solo por prueba unitaria)", ok)

        # 16. Filtros, orden y paginacion
        page.reload()
        page.wait_for_selector("[id='formTabla:tablaLecturas_data']")
        total = filas_tabla(page, "formTabla:tablaLecturas_data")
        elegir_filtro(page, 1, "Invernadero 1")          # filtro de zona (indice 0 = variable, 1 = zona)
        filtradas = filas_tabla(page, "formTabla:tablaLecturas_data")
        texto_tabla = page.inner_text("[id='formTabla:tablaLecturas']")
        paginador = page.locator("[id='formTabla:tablaLecturas'] .ui-paginator").count() > 0
        captura(page, "15_filtro_zona_invernadero")
        ok = paginador and filtradas < total and ("Invernadero 1" in texto_tabla or "ninguna coincide" in texto_tabla)
        resultado("10 Filtro por zona reduce el historial y el paginador esta presente", ok,
                  f"total={total} filtradas={filtradas}")
        elegir_filtro(page, 1, "Todas")
        page.locator("[id='formTabla:tablaLecturas'] th:has-text('Valor')").click()
        page.wait_for_timeout(800)
        captura(page, "16_orden_por_valor")

        # 17. Alertas
        page.click("nav a:has-text('Alertas')")
        page.wait_for_selector("[id='formAlertas:tablaAlertas_data']")
        t = page.inner_text("[id='formAlertas:tablaAlertas']")
        captura(page, "17_alertas")
        resultado("3c Vista de alertas muestra ALTA y BAJA generadas", "ALTA" in t and "BAJA" in t)

        # 18. Anotaciones: valida, corta, larga, lectura inexistente
        page.click("nav a:has-text('anotaciones')")
        page.wait_for_selector("[id='formAnotacion:texto']")
        antes = conteos()
        page.click("[id='formAnotacion:zona']")
        page.click("[id='formAnotacion:zona_items'] li:has-text('Cama A')")
        page.fill("[id='formAnotacion:texto']", "[prueba] Hojas con manchas en la cama A (P03)")
        limpiar_mensajes(page)
        page.click("[id='formAnotacion:btnAnotar']")
        m = esperar_mensaje(page, "registrada")
        fila = page.locator("[id='formAnotaciones:tablaAnotaciones_data'] tr[data-ri]").first.inner_text()
        ok = "OBSERVADOR" in m and "OBSERVADOR" in fila and conteos()[2] == antes[2] + 1
        captura(page, "18_anotacion_valida_observador")
        resultado("9a Anotacion valida firmada con el rol de la sesion (OBSERVADOR)", ok)

        antes = conteos()
        page.fill("[id='formAnotacion:texto']", "ok")
        limpiar_mensajes(page)
        page.click("[id='formAnotacion:btnAnotar']")
        m = esperar_mensaje(page, "caracteres")
        ok = "al menos 3" in m and conteos() == antes
        captura(page, "19_anotacion_corta")
        resultado("9b Anotacion demasiado corta rechazada", ok)

        # PrimeFaces recorta en el cliente a 300 (maxlength del widget) aunque se inyecten 301 en el DOM;
        # se comprueba ese recorte y que lo persistido mide 300. La regla del servidor (>300 -> rechazo)
        # queda cubierta por AnotacionValidatorTest.textoInvalido, que no pasa por el navegador.
        page.evaluate("document.querySelector(\"[id='formAnotacion:texto']\").value = '[prueba] ' + 'x'.repeat(292)")
        limpiar_mensajes(page)
        page.click("[id='formAnotacion:btnAnotar']")
        m = esperar_mensaje(page, "registrada")
        longitud = int(psql("select length(texto) from anotacion order by id desc limit 1"))
        ok = longitud == 300 and conteos()[2] == antes[2] + 1
        antes = conteos()
        resultado("9c Texto de 301: PrimeFaces lo recorta a 300 en el cliente (persistido=300); la regla >300 del servidor se prueba con JUnit",
                  ok, f"longitud persistida={longitud}")

        page.fill("[id='formAnotacion:texto']", "[prueba] referencia a lectura inexistente")
        page.fill("[id='formAnotacion:lectura']", "999999")
        limpiar_mensajes(page)
        page.click("[id='formAnotacion:btnAnotar']")
        m = esperar_mensaje(page, "no existe")
        ok = "no existe" in m and conteos() == antes
        captura(page, "20_anotacion_lectura_inexistente")
        resultado("9d Anotacion ligada a lectura inexistente rechazada", ok)

        # 19. Cierre de sesion y acceso posterior
        page.click("[id='formSalir:btnSalir']")
        page.wait_for_url("**/login.xhtml*", timeout=15000)
        ok_salida = "salida=1" in page.url
        page.goto(f"{BASE}/app/lecturas.xhtml")
        ok = ok_salida and "expirada=1" in page.url
        captura(page, "21_sesion_cerrada")
        resultado("11d Cerrar sesion invalida la sesion; /app vuelve a pedir acceso", ok)

        # 20. Sesion expirada durante un envio AJAX
        login(page, "observador")
        elegir_sensor(page, SENSOR)
        page.fill("[id='formLectura:valor']", "20")
        ctx.clear_cookies()   # simula la caducidad de la sesion del lado del servidor
        antes = conteos()
        page.click("[id='formLectura:btnGuardar']")
        try:
            page.wait_for_url("**/login.xhtml*", timeout=15000)
            ok = "expirada=1" in page.url and conteos() == antes
        except PWTimeout:
            ok = False
        captura(page, "22_sesion_expirada_en_ajax")
        resultado("11e Sesion expirada durante un POST AJAX: redirige al acceso y no guarda", ok, page.url)

        # 21. Rol sin permiso para registrar lecturas
        login(page, "coordinacion")
        sin_form = page.locator("[id='formLectura']").count() == 0
        aviso = page.inner_text(".aviso-info") if page.locator(".aviso-info").count() else ""
        captura(page, "23_coordinacion_sin_formulario")
        page.click("nav a:has-text('anotaciones')")
        page.wait_for_selector("[id='formAnotacion:texto']")
        page.click("[id='formAnotacion:zona']")
        page.click("[id='formAnotacion:zona_items'] li:has-text('Invernadero 1')")
        page.fill("[id='formAnotacion:texto']", "[prueba] revision de coordinacion (P03)")
        limpiar_mensajes(page)
        page.click("[id='formAnotacion:btnAnotar']")
        m = esperar_mensaje(page, "registrada")
        fila = page.locator("[id='formAnotaciones:tablaAnotaciones_data'] tr[data-ri]").first.inner_text()
        captura(page, "24_coordinacion_anota")
        resultado("12 Rol COORDINACION: sin formulario de lecturas (aviso) pero anota con su rol",
                  sin_form and "COORDINACION" in aviso and "COORDINACION" in fila)
        page.click("[id='formSalir:btnSalir']")
        page.wait_for_url("**/login.xhtml*", timeout=15000)

        # 22. Fallo de transaccion: la alerta no puede insertarse -> la lectura tampoco queda
        if os.environ.get("SKIP_TX_TEST") != "1":
            login(page, "observador")
            antes = conteos()
            psql("ALTER TABLE alerta ADD CONSTRAINT tmp_p03_sin_alta CHECK (nivel <> 'ALTA') NOT VALID")
            try:
                m = registrar(page, "40", "[prueba] transaccion revertida")
            finally:
                psql("ALTER TABLE alerta DROP CONSTRAINT tmp_p03_sin_alta")
            despues = conteos()
            ok = "persistencia" in m.lower() and despues == antes
            captura(page, "25_transaccion_revertida")
            resultado("14 Fallo al insertar la alerta revierte la lectura (sin inserciones parciales)", ok,
                      f"{antes}->{despues}")
            page.click("[id='formSalir:btnSalir']")
            page.wait_for_url("**/login.xhtml*", timeout=15000)
        else:
            log("PENDIENTE: prueba de transaccion omitida (SKIP_TX_TEST=1)")

        # 23. Base de datos no disponible (se detiene el contenedor y se vuelve a arrancar al final)
        if os.environ.get("SKIP_DB_DOWN") != "1":
            ok = False
            detalle = ""
            try:
                login(page, "observador")
                subprocess.run([DOCKER, "stop", "dsw-p02-huerto-db"], capture_output=True)
                page.goto(f"{BASE}/app/lecturas.xhtml", timeout=90000)
                page.wait_for_selector("#mensajes .ui-messages-error", timeout=60000)
                m = mensajes(page)
                ok = "no disponible" in m and page.locator("[id='formLectura']").count() == 0
                captura(page, "26_base_no_disponible")
            except Exception as e:  # se registra como NO_VERIFICADO y se continua
                detalle = str(e).splitlines()[0][:100]
            finally:
                subprocess.run([DOCKER, "start", "dsw-p02-huerto-db"], capture_output=True)
                for _ in range(30):
                    try:
                        psql("select 1")
                        break
                    except RuntimeError:
                        time.sleep(2)
            resultado("13 Base de datos no disponible: mensaje claro y formulario oculto; se recupera al volver", ok, detalle)
        else:
            log("PENDIENTE: prueba de base caida omitida (SKIP_DB_DOWN=1)")

        browser.close()

    final = conteos()
    log(f"Conteos finales lectura/alerta/anotacion: {final}")
    return 1 if any(e != "VERIFICADO" for e, _, _ in resultados) else 0


if __name__ == "__main__":
    sys.exit(main())
