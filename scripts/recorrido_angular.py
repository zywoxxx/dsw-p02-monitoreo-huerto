#!/usr/bin/env python3
"""
recorrido_angular.py - Recorrido del cliente Angular (P04 y P05) en un navegador real (Playwright).

Requiere la API en marcha (puerto 8081) y el cliente servido con `npx ng serve` (puerto 4200,
que reenvia /api a la API). Comprueba el flujo principal de punta a punta:
Angular -> proxy -> API Spring Boot -> PostgreSQL, y toma las capturas de la evidencia.
P04: acceso, captura de lecturas, filtros y roles. P05: atencion y reapertura de alertas
(solo RESPONSABLE), registro y filtro de anotaciones con los tres roles.

Salidas:
  IMG_DIR/*.png                  (por omision docs/p05/evidencia/img)
  EVID_DIR/recorrido_angular.txt (por omision docs/p05/evidencia/txt)

Variables: WEB_URL (http://localhost:4200), API_URL (http://localhost:8081), PSQL_CMD, EVID_DIR, IMG_DIR,
           CLAVE_OBSERVADOR, CLAVE_COORDINACION, CLAVE_RESPONSABLE (contrasenas ficticias de laboratorio).
"""
import os
import shlex
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parent.parent
IMG = Path(os.environ["IMG_DIR"]) if os.environ.get("IMG_DIR") else RAIZ / "docs" / "p05" / "evidencia" / "img"
TXT = Path(os.environ["EVID_DIR"]) if os.environ.get("EVID_DIR") else RAIZ / "docs" / "p05" / "evidencia" / "txt"
IMG.mkdir(parents=True, exist_ok=True)
TXT.mkdir(parents=True, exist_ok=True)
WEB = os.environ.get("WEB_URL", "http://localhost:4200").rstrip("/")
API = os.environ.get("API_URL", "http://localhost:8081").rstrip("/")
PSQL = shlex.split(os.environ.get(
    "PSQL_CMD", "docker exec -i dsw-p02-huerto-db psql -U huerto_app -d huerto_db"))
CLAVES = {
    "observador": os.environ.get("CLAVE_OBSERVADOR", "Observador#2026"),
    "coordinacion": os.environ.get("CLAVE_COORDINACION", "Coordinacion#2026"),
    "responsable": os.environ.get("CLAVE_RESPONSABLE", "Responsable#2026"),
}
TEXTO_ANOTACION = "[prueba] P05 anotacion desde Angular"
TEXTO_ANOTACION_COORD = "[prueba] P05 anotacion de coordinacion desde Angular"

salida = open(TXT / "recorrido_angular.txt", "w", encoding="utf-8")
resultados = []


def log(texto=""):
    print(texto)
    salida.write(texto + "\n")


def consultar(consulta):
    r = subprocess.run(PSQL + ["-At", "-c", consulta], capture_output=True, text=True, timeout=30)
    return r.stdout.strip()


def contar(tabla):
    return int(consultar(f"SELECT count(*) FROM {tabla}"))


def ruta_corta(ruta):
    """Ruta relativa al repositorio para la bitacora (o absoluta si la evidencia va fuera de el)."""
    try:
        return ruta.relative_to(RAIZ).as_posix()
    except ValueError:
        return ruta.as_posix()


def caso(nombre, condiciones):
    fallidas = [d for d, bien in condiciones if not bien]
    estado = "VERIFICADO" if not fallidas else "NO_VERIFICADO"
    log(f"{len(resultados) + 1:02d} | {estado:<13} | {nombre}" + (f" | fallo: {'; '.join(fallidas)}" if fallidas else ""))
    resultados.append(estado)


def captura(page, nombre):
    page.screenshot(path=str(IMG / nombre), full_page=True)
    log(f"     captura: {ruta_corta(IMG)}/{nombre}")


def entrar(page, usuario, clave):
    page.goto(WEB + "/acceso")
    page.fill("#usuario", usuario)
    page.fill("#contrasena", clave)
    page.click("#btn-entrar")


def registrar(page, valor, observacion):
    page.select_option("#sensor", label="SEN-A-TEMP-01 - Temperatura ambiente (C) - Cama A")
    page.fill("#valor", valor)
    page.fill("#observacion", observacion)
    with page.expect_response(lambda r: r.url.endswith("/api/lecturas") and r.request.method == "POST") as info:
        page.click("#btn-registrar")
    return info.value


def seleccionar_zona(page, nombre):
    """Elige en #zona la opcion cuyo texto empieza por el nombre (las opciones muestran 'nombre - cultivo')."""
    valor = page.eval_on_selector(
        "#zona", "(s, nombre) => [...s.options].find(o => o.text.trim().startsWith(nombre)).value", nombre)
    page.select_option("#zona", valor)


def zona_elegida(page):
    return page.eval_on_selector("#zona", "s => s.options[s.selectedIndex].text.trim()")


def anotar(page, texto, lectura=""):
    """Envia el formulario de anotacion (la zona ya seleccionada) y devuelve la respuesta de la API."""
    page.fill("#lectura-id", lectura)
    page.fill("#texto", texto)
    with page.expect_response(lambda r: r.url.endswith("/api/anotaciones") and r.request.method == "POST") as info:
        page.click("#btn-anotar")
    return info.value


def cambiar_atencion(page, fila, boton):
    """Pulsa .btn-atender o .btn-reabrir de la fila y devuelve la respuesta del PATCH."""
    with page.expect_response(lambda r: "/api/alertas/" in r.url and r.request.method == "PATCH") as info:
        page.click(f"{fila} {boton}")
    return info.value


def main():
    log(f"recorrido_angular.py - {datetime.now().isoformat(timespec='seconds')} - cliente {WEB} - API {API}")
    log()
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        contexto = navegador.new_context(viewport={"width": 1280, "height": 800}, locale="es-MX")
        page = contexto.new_page()
        peticiones = []
        page.on("request", lambda r: peticiones.append((r.method, r.url, r.headers.get("authorization", ""))))

        page.goto(WEB + "/lecturas")
        page.wait_for_selector("#form-acceso")
        caso("Sin sesion, /lecturas lleva a la pantalla de acceso", [
            ("la URL termina en /acceso", "/acceso" in page.url),
        ])
        captura(page, "01_acceso.png")

        entrar(page, "observador", "contrasena-equivocada")
        page.wait_for_selector("#aviso-error")
        caso("Acceso con contrasena incorrecta: mensaje de error y sin sesion", [
            ("mensaje visible", "incorrectos" in page.inner_text("#aviso-error")),
            ("sigue en /acceso", "/acceso" in page.url),
            ("sin sesion guardada", page.evaluate("sessionStorage.getItem('huerto.sesion')") is None),
        ])
        captura(page, "02_acceso_rechazado.png")

        entrar(page, "observador", CLAVES["observador"])
        page.wait_for_selector("#tabla-lecturas")
        caso("Acceso del observador: formulario de captura e historial desde la API", [
            ("usuario y rol en la cabecera", "OBSERVADOR" in page.inner_text("#usuario-sesion")),
            ("formulario visible", page.is_visible("#form-lectura")),
            ("el catalogo de sensores llego", page.locator("#sensor option").count() > 1),
            ("las peticiones a /api llevan el token",
             any("/api/sensores" in u and a.startswith("Bearer ") for _, u, a in peticiones)),
            ("la peticion sale al mismo origen (proxy)",
             any(u.startswith(WEB + "/api/") for _, u, _ in peticiones)),
        ])
        captura(page, "03_lecturas_observador.png")

        antes = contar("lectura")
        r = registrar(page, "25.5", "[prueba] P05 Angular lectura valida")
        page.wait_for_selector("#aviso-ok")
        page.locator("#tabla-lecturas", has_text="[prueba] P05 Angular lectura valida").wait_for()   # el historial recarga despues del 201
        caso("Lectura valida 25.5: 201, mensaje, fila nueva y +1 en PostgreSQL", [
            ("la API respondio 201", r.status == 201),
            ("mensaje de exito", page.is_visible("#aviso-ok")),
            ("sin aviso de alerta", not page.is_visible("#aviso-alerta")),
            ("la fila aparece en el historial", "[prueba] P05 Angular lectura valida" in page.inner_text("#tabla-lecturas")),
            ("formulario limpio", page.input_value("#valor") == ""),
            ("lectura +1", contar("lectura") == antes + 1),
        ])
        captura(page, "04_lectura_valida.png")

        antes_a = contar("alerta")
        r = registrar(page, "38", "[prueba] P05 Angular alerta")
        page.wait_for_selector("#aviso-alerta")
        caso("Lectura 38 fuera del umbral: 201 con alerta ALTA visible y +1 alerta", [
            ("la API respondio 201", r.status == 201),
            ("aviso de alerta", "ALTA" in page.inner_text("#aviso-alerta")),
            ("alerta +1", contar("alerta") == antes_a + 1),
        ])
        captura(page, "05_lectura_con_alerta.png")

        antes = contar("lectura")
        r = registrar(page, "abc", "[prueba] se conserva lo escrito")
        page.wait_for_selector("#aviso-error")
        caso("Valor no numerico: 400, mensaje por campo, se conserva lo escrito, la base no cambia", [
            ("la API respondio 400", r.status == 400),
            ("codigo VALIDACION en pantalla", "VALIDACION" in page.inner_text("#aviso-error")),
            ("el valor escrito se conserva", page.input_value("#valor") == "abc"),
            ("la observacion se conserva", page.input_value("#observacion") == "[prueba] se conserva lo escrito"),
            ("lectura sin cambio", contar("lectura") == antes),
        ])
        captura(page, "06_valor_no_numerico.png")

        r = registrar(page, "150", "[prueba] rango fisico")
        page.wait_for_selector("#aviso-error")
        caso("Valor 150 fuera del rango fisico: 422 y la base no cambia", [
            ("la API respondio 422", r.status == 422),
            ("codigo REGLA_DE_NEGOCIO en pantalla", "REGLA_DE_NEGOCIO" in page.inner_text("#aviso-error")),
            ("lectura sin cambio", contar("lectura") == antes),
        ])
        captura(page, "07_fuera_de_rango_fisico.png")

        page.select_option("#filtro-origen", "simulado")
        page.wait_for_function(
            "() => [...document.querySelectorAll('#tabla-lecturas tbody tr td:nth-child(6)')]"
            ".every(td => td.innerText.trim() === 'simulado')")
        caso("Filtro por procedencia: el historial solo muestra lecturas simuladas", [
            ("hay filas", page.locator("#tabla-lecturas tbody tr").count() > 0),
        ])
        captura(page, "08_filtro_simulado.png")

        page.click("#btn-salir")
        page.wait_for_selector("#form-acceso")
        caso("Salir borra la sesion del navegador", [
            ("sin sesion guardada", page.evaluate("sessionStorage.getItem('huerto.sesion')") is None),
        ])

        entrar(page, "coordinacion", CLAVES["coordinacion"])
        page.wait_for_selector("#tabla-lecturas")
        caso("Rol COORDINACION: consulta el historial pero no ve el formulario de captura", [
            ("rol en la cabecera", "COORDINACION" in page.inner_text("#usuario-sesion")),
            ("sin formulario", page.locator("#form-lectura").count() == 0),
            ("aviso del rol", page.is_visible("#aviso-rol")),
        ])
        captura(page, "09_lecturas_coordinacion.png")

        # ------------------------------------------------ P05: alertas y anotaciones con el RESPONSABLE
        page.click("#btn-salir")
        page.wait_for_selector("#form-acceso")
        entrar(page, "responsable", CLAVES["responsable"])
        page.wait_for_selector("#usuario-sesion")
        page.goto(WEB + "/alertas")
        page.wait_for_selector("#tabla-alertas")
        id_alerta = int(consultar(
            "SELECT coalesce(max(a.id), 0) FROM alerta a JOIN lectura l ON l.id = a.lectura_id "
            "WHERE l.observacion = '[prueba] P05 Angular alerta'"))
        fila = f'#tabla-alertas tr[data-id="{id_alerta}"]'
        with page.expect_response(lambda r: "/api/alertas?" in r.url and "atendida=false" in r.url):
            page.select_option("#filtro-atendida", "false")
        page.wait_for_selector(fila)
        caso("Rol RESPONSABLE en /alertas: la alerta ALTA del recorrido aparece pendiente con boton de atender", [
            ("rol en la cabecera", "RESPONSABLE" in page.inner_text("#usuario-sesion")),
            ("fila con SEN-A-TEMP-01, 38 y ALTA", all(t in page.inner_text(fila) for t in ("SEN-A-TEMP-01", "38", "ALTA"))),
            ("etiqueta pendiente", page.locator(f"{fila} .etiqueta-pendiente").count() == 1),
            ("boton Marcar atendida", page.locator(f"{fila} .btn-atender").count() == 1),
        ])

        r = cambiar_atencion(page, fila, ".btn-atender")
        page.wait_for_selector("#aviso-ok")
        mensaje = page.inner_text("#aviso-ok")
        page.select_option("#filtro-atendida", index=0)   # Todas: con el filtro de pendientes la fila atendida ya no sale
        page.wait_for_selector(f"{fila} .etiqueta-atendida")
        caso("Marcar atendida: PATCH 200, mensaje, etiqueta con el rol y atendida = true en PostgreSQL", [
            ("la API respondio 200", r.status == 200),
            ("mensaje de exito", "atendida" in mensaje),
            ("etiqueta atendida por RESPONSABLE", "RESPONSABLE" in page.inner_text(f"{fila} .etiqueta-atendida")),
            ("boton Reabrir", page.locator(f"{fila} .btn-reabrir").count() == 1),
            ("atendida = true en PostgreSQL", consultar(f"SELECT atendida FROM alerta WHERE id = {id_alerta}") == "t"),
        ])
        captura(page, "12_alerta_atendida.png")

        r = cambiar_atencion(page, fila, ".btn-reabrir")
        page.wait_for_selector(f"{fila} .etiqueta-pendiente")
        caso("Reabrir: PATCH 200 y la alerta vuelve a pendiente en pantalla y en PostgreSQL", [
            ("la API respondio 200", r.status == 200),
            ("mensaje de reapertura", "reabierta" in page.inner_text("#aviso-ok")),
            ("boton Marcar atendida de nuevo", page.locator(f"{fila} .btn-atender").count() == 1),
            ("atendida = false en PostgreSQL", consultar(f"SELECT atendida FROM alerta WHERE id = {id_alerta}") == "f"),
        ])
        captura(page, "13_alerta_reabierta.png")

        page.goto(WEB + "/anotaciones")
        page.wait_for_selector("#form-anotacion")
        seleccionar_zona(page, "Cama A")
        antes_n = contar("anotacion")
        r = anotar(page, "ok")
        page.wait_for_selector("#aviso-error")
        caso("Anotacion con texto \"ok\": 400 VALIDACION en pantalla, lo capturado se conserva, la base no cambia", [
            ("la API respondio 400", r.status == 400),
            ("codigo VALIDACION en pantalla", "VALIDACION" in page.inner_text("#aviso-error")),
            ("el texto se conserva", page.input_value("#texto") == "ok"),
            ("la zona se conserva", zona_elegida(page).startswith("Cama A")),
            ("anotacion sin cambio", contar("anotacion") == antes_n),
        ])
        captura(page, "14_anotacion_texto_corto.png")

        largo = "[prueba] P05 " + "x" * 288
        r = anotar(page, largo)
        page.locator("#contador-texto", has_text="301/300").wait_for()
        caso("Anotacion de 301 caracteres: el cliente no recorta (sin maxlength) y la API responde 400", [
            ("la API respondio 400", r.status == 400),
            ("contador 301/300 marcado como error", "error-campo" in (page.get_attribute("#contador-texto", "class") or "")),
            ("codigo VALIDACION en pantalla", "VALIDACION" in page.inner_text("#aviso-error")),
            ("el texto se conserva", page.input_value("#texto") == largo),
            ("anotacion sin cambio", contar("anotacion") == antes_n),
        ])
        captura(page, "15_anotacion_texto_largo.png")

        r = anotar(page, "[prueba] P05 anotacion con lectura inexistente", "999999")
        page.locator("#aviso-error", has_text="NO_ENCONTRADO").wait_for()
        caso("Lectura relacionada 999999: 404 NO_ENCONTRADO en pantalla y lo capturado se conserva", [
            ("la API respondio 404", r.status == 404),
            ("la lectura capturada se conserva", page.input_value("#lectura-id") == "999999"),
            ("anotacion sin cambio", contar("anotacion") == antes_n),
        ])
        captura(page, "16_anotacion_lectura_inexistente.png")

        r = anotar(page, TEXTO_ANOTACION)
        id_anotacion = (r.json() or {}).get("id") if r.ok else 0
        fila = f'#tabla-anotaciones tr[data-id="{id_anotacion}"]'
        page.wait_for_selector("#aviso-ok")
        page.wait_for_selector(fila)
        caso("Anotacion valida sin lectura: 201, mensaje, fila nueva firmada por RESPONSABLE y +1 en PostgreSQL", [
            ("la API respondio 201", r.status == 201),
            ("mensaje de exito", "registrada" in page.inner_text("#aviso-ok")),
            ("la fila muestra el texto", TEXTO_ANOTACION in page.inner_text(fila)),
            ("fila firmada por RESPONSABLE", page.locator(f"{fila} .etiqueta-rol-RESPONSABLE").count() == 1),
            ("texto y lectura limpios", page.input_value("#texto") == "" and page.input_value("#lectura-id") == ""),
            ("la zona se conserva", zona_elegida(page).startswith("Cama A")),
            ("anotacion +1", contar("anotacion") == antes_n + 1),
        ])
        captura(page, "17_anotacion_valida.png")

        with page.expect_response(lambda r: "/api/anotaciones?" in r.url and "zonaId=" in r.url):
            page.select_option("#filtro-zona", label="Invernadero 1")
        page.locator(fila).wait_for(state="detached")
        caso("Filtro por zona Invernadero 1: la anotacion de Cama A no aparece", [
            ("la fila nueva no esta en la lista", page.locator(fila).count() == 0),
            ("sin filas de Cama A", "Cama A" not in (page.inner_text("#tabla-anotaciones") if page.is_visible("#tabla-anotaciones") else "")),
        ])
        captura(page, "18_anotaciones_filtro_zona.png")
        page.click("#btn-salir")
        page.wait_for_selector("#form-acceso")

        # ------------------------------------------------ P05: COORDINACION y OBSERVADOR solo consultan alertas
        entrar(page, "coordinacion", CLAVES["coordinacion"])
        page.wait_for_selector("#usuario-sesion")
        page.goto(WEB + "/alertas")
        page.wait_for_selector("#tabla-alertas")
        caso("Rol COORDINACION en /alertas: consulta sin botones de atender y con el aviso del rol", [
            ("rol en la cabecera", "COORDINACION" in page.inner_text("#usuario-sesion")),
            ("sin botones de atender ni reabrir", page.locator(".btn-atender, .btn-reabrir").count() == 0),
            ("aviso del rol", page.is_visible("#aviso-rol-alertas") and "responsable" in page.inner_text("#aviso-rol-alertas")),
        ])
        captura(page, "19_alertas_coordinacion.png")

        page.goto(WEB + "/anotaciones")
        page.wait_for_selector("#form-anotacion")
        seleccionar_zona(page, "Cama A")
        antes_n = contar("anotacion")
        r = anotar(page, TEXTO_ANOTACION_COORD)
        id_anotacion = (r.json() or {}).get("id") if r.ok else 0
        fila = f'#tabla-anotaciones tr[data-id="{id_anotacion}"]'
        page.wait_for_selector(fila)
        caso("Rol COORDINACION anota: 201 y la fila queda firmada con COORDINACION", [
            ("la API respondio 201", r.status == 201),
            ("la fila muestra el texto", TEXTO_ANOTACION_COORD in page.inner_text(fila)),
            ("fila firmada por COORDINACION", page.locator(f"{fila} .etiqueta-rol-COORDINACION").count() == 1),
            ("anotacion +1", contar("anotacion") == antes_n + 1),
        ])
        captura(page, "20_anotacion_coordinacion.png")
        page.click("#btn-salir")
        page.wait_for_selector("#form-acceso")

        entrar(page, "observador", CLAVES["observador"])
        page.wait_for_selector("#usuario-sesion")
        page.goto(WEB + "/alertas")
        page.wait_for_selector("#tabla-alertas")
        caso("Rol OBSERVADOR en /alertas: consulta sin botones de atender", [
            ("rol en la cabecera", "OBSERVADOR" in page.inner_text("#usuario-sesion")),
            ("sin botones de atender ni reabrir", page.locator(".btn-atender, .btn-reabrir").count() == 0),
            ("aviso del rol", page.is_visible("#aviso-rol-alertas")),
        ])

        page.evaluate("""() => {
            const s = JSON.parse(sessionStorage.getItem('huerto.sesion'));
            s.token = s.token.slice(0, -4) + 'AAAA';
            sessionStorage.setItem('huerto.sesion', JSON.stringify(s));
        }""")
        page.goto(WEB + "/lecturas")
        page.wait_for_selector("#aviso-expirada")
        caso("Token alterado en el navegador: la API responde 401 y el cliente vuelve al acceso", [
            ("aviso de sesion no valida", page.is_visible("#aviso-expirada")),
            ("sesion borrada", page.evaluate("sessionStorage.getItem('huerto.sesion')") is None),
        ])
        captura(page, "21_token_invalido.png")

        page.set_viewport_size({"width": 1280, "height": 1100})
        page.goto(API + "/swagger-ui.html")
        page.wait_for_selector(".opblock-summary", timeout=30000)
        caso("Documentacion generada por springdoc disponible en /swagger-ui.html", [
            ("las 13 operaciones del contrato visibles", page.locator(".opblock-summary").count() >= 13),
        ])
        captura(page, "22_swagger_ui.png")

        navegador.close()

    bien = resultados.count("VERIFICADO")
    log()
    log(f"RESUMEN: {bien}/{len(resultados)} casos VERIFICADO")
    salida.close()
    return 0 if bien == len(resultados) else 1


if __name__ == "__main__":
    sys.exit(main())
