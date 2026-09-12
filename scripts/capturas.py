"""
capturas.py - Genera las capturas de pantalla del flujo principal (PR09) (rol: evidencia/capturas).

Recorre la aplicacion desplegada con un navegador real (Chromium via Playwright) y guarda
las imagenes en docs/evidencia/img/. Cada captura corresponde a un paso del protocolo
manual descrito en docs/evidencia/INDICE.md.

Requisitos (solo para regenerar capturas; no son parte del WAR):
    python -m pip install playwright
    python -m playwright install chromium
Uso:
    python scripts/capturas.py [BASE_URL]      # por defecto http://localhost:8080/web1
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080/web1"
OUT = Path(__file__).resolve().parent.parent / "docs" / "evidencia" / "img"
OUT.mkdir(parents=True, exist_ok=True)


SENSOR = "SEN-A-TEMP-01"   # temperatura, rango fisico [-10, 60], umbral [15, 32]


def seleccionar_sensor(page, codigo):
    """Selecciona la opcion del sensor por su codigo (no por posicion, que depende del orden)."""
    valor = page.evaluate(
        "c => [...document.querySelectorAll('#sensorId option')].find(o => o.textContent.includes(c)).value",
        codigo,
    )
    page.select_option("#sensorId", value=valor)


def guardar(page, nombre):
    ruta = OUT / f"{nombre}.png"
    page.screenshot(path=str(ruta), full_page=True)
    print(f"[captura] {ruta.name}  <- {page.url}")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 900})

        # 01 GET inicial: catalogo de sensores y lecturas de la semilla
        page.goto(f"{BASE}/lecturas")
        page.wait_for_selector("#tabla-sensores")
        guardar(page, "01_get_inicial_lecturas")

        # 02 Formulario capturado antes de enviar (POST valido)
        seleccionar_sensor(page, SENSOR)
        page.fill("#valor", "27.5")
        page.fill("#observacion", "Lectura manual de prueba (captura)")
        guardar(page, "02_formulario_lectura_valida")

        # 03 Resultado del POST valido: 303 -> GET con mensaje de exito y nueva fila
        page.click("#btn-registrar")
        page.wait_for_selector("#aviso-ok")
        guardar(page, "03_post_valido_resultado")

        # 04 Validacion negativa: valor no numerico -> HTTP 400 con lista de errores
        seleccionar_sensor(page, SENSOR)
        page.fill("#valor", "abc")
        page.click("#btn-registrar")
        page.wait_for_selector("#aviso-error")
        guardar(page, "04_post_invalido_no_numerico")

        # 05 Validacion negativa: valor fuera del rango fisico del tipo de sensor
        seleccionar_sensor(page, SENSOR)
        page.fill("#valor", "150")
        page.click("#btn-registrar")
        page.wait_for_selector("#aviso-error")
        guardar(page, "05_post_invalido_rango_fisico")

        # 06 Validacion negativa: campos vacios (se quita 'required' para que llegue al servidor)
        page.goto(f"{BASE}/lecturas")
        page.evaluate("document.getElementById('sensorId').removeAttribute('required')")
        page.click("#btn-registrar")
        page.wait_for_selector("#aviso-error")
        guardar(page, "06_post_invalido_vacio")

        # 07 POST valido fuera de umbral: se registra y genera alerta ALTA
        seleccionar_sensor(page, SENSOR)
        page.fill("#valor", "38")
        page.fill("#observacion", "Tarde calurosa (captura)")
        page.click("#btn-registrar")
        page.wait_for_selector("#aviso-alerta")
        guardar(page, "07_post_valido_con_alerta")

        # 08 Vista de alertas
        page.goto(f"{BASE}/alertas")
        page.wait_for_selector("#tabla-alertas")
        guardar(page, "08_get_alertas")

        # 09 Ruta de salud (JSON con version de PostgreSQL)
        page.goto(f"{BASE}/health")
        guardar(page, "09_health_json")

        # 10 Pagina de error controlada (404)
        page.goto(f"{BASE}/ruta-inexistente")
        guardar(page, "10_error_404")

        # 11 Zonas y anotaciones (RF01, RF06): GET inicial
        page.goto(f"{BASE}/anotaciones")
        page.wait_for_selector("#tabla-zonas")
        guardar(page, "11_get_zonas_anotaciones")

        # 12 POST anotacion valida por el rol OBSERVADOR
        page.select_option("#zonaId", index=1)
        page.select_option("#autorRol", value="OBSERVADOR")
        page.fill("#texto", "[prueba] Hojas con manchas en la cama A (captura)")
        page.click("#btn-anotar")
        page.wait_for_selector("#aviso-ok")
        guardar(page, "12_post_anotacion_valida")

        # 13 POST anotacion invalida: texto demasiado corto
        page.select_option("#zonaId", index=1)
        page.select_option("#autorRol", value="COORDINACION")
        page.fill("#texto", "ok")
        page.click("#btn-anotar")
        page.wait_for_selector("#aviso-error")
        guardar(page, "13_post_anotacion_invalida")

        browser.close()
    print("Capturas generadas en", OUT)


if __name__ == "__main__":
    main()
