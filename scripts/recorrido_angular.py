#!/usr/bin/env python3
"""
recorrido_angular.py - Recorrido del cliente Angular de P04 en un navegador real (Playwright).

Requiere la API en marcha (puerto 8081) y el cliente servido con `npx ng serve` (puerto 4200,
que reenvia /api a la API). Comprueba el flujo principal de punta a punta:
Angular -> proxy -> API Spring Boot -> PostgreSQL, y toma las capturas de la evidencia.

Salidas:
  docs/p04/evidencia/img/*.png
  docs/p04/evidencia/txt/recorrido_angular.txt

Variables: WEB_URL (http://localhost:4200), API_URL (http://localhost:8081), PSQL_CMD,
           CLAVE_OBSERVADOR, CLAVE_COORDINACION (contrasenas ficticias de laboratorio).
"""
import os
import shlex
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parent.parent
IMG = RAIZ / "docs" / "p04" / "evidencia" / "img"
TXT = RAIZ / "docs" / "p04" / "evidencia" / "txt"
IMG.mkdir(parents=True, exist_ok=True)
TXT.mkdir(parents=True, exist_ok=True)
WEB = os.environ.get("WEB_URL", "http://localhost:4200").rstrip("/")
API = os.environ.get("API_URL", "http://localhost:8081").rstrip("/")
PSQL = shlex.split(os.environ.get(
    "PSQL_CMD", "docker exec -i dsw-p02-huerto-db psql -U huerto_app -d huerto_db"))
CLAVES = {
    "observador": os.environ.get("CLAVE_OBSERVADOR", "Observador#2026"),
    "coordinacion": os.environ.get("CLAVE_COORDINACION", "Coordinacion#2026"),
}

salida = open(TXT / "recorrido_angular.txt", "w", encoding="utf-8")
resultados = []


def log(texto=""):
    print(texto)
    salida.write(texto + "\n")


def contar(tabla):
    r = subprocess.run(PSQL + ["-At", "-c", f"SELECT count(*) FROM {tabla}"],
                       capture_output=True, text=True, timeout=30)
    return int(r.stdout.strip())


def caso(nombre, condiciones):
    fallidas = [d for d, bien in condiciones if not bien]
    estado = "VERIFICADO" if not fallidas else "NO_VERIFICADO"
    log(f"{len(resultados) + 1:02d} | {estado:<13} | {nombre}" + (f" | fallo: {'; '.join(fallidas)}" if fallidas else ""))
    resultados.append(estado)


def captura(page, nombre):
    page.screenshot(path=str(IMG / nombre), full_page=True)
    log(f"     captura: docs/p04/evidencia/img/{nombre}")


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
        r = registrar(page, "25.5", "[prueba] P04 Angular lectura valida")
        page.wait_for_selector("#aviso-ok")
        caso("Lectura valida 25.5: 201, mensaje, fila nueva y +1 en PostgreSQL", [
            ("la API respondio 201", r.status == 201),
            ("mensaje de exito", page.is_visible("#aviso-ok")),
            ("sin aviso de alerta", not page.is_visible("#aviso-alerta")),
            ("la fila aparece en el historial", "[prueba] P04 Angular lectura valida" in page.inner_text("#tabla-lecturas")),
            ("formulario limpio", page.input_value("#valor") == ""),
            ("lectura +1", contar("lectura") == antes + 1),
        ])
        captura(page, "04_lectura_valida.png")

        antes_a = contar("alerta")
        r = registrar(page, "38", "[prueba] P04 Angular alerta")
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
        captura(page, "10_token_invalido.png")

        page.set_viewport_size({"width": 1280, "height": 1100})
        page.goto(API + "/swagger-ui.html")
        page.wait_for_selector(".opblock-summary", timeout=30000)
        caso("Documentacion generada por springdoc disponible en /swagger-ui.html", [
            ("lista de operaciones visible", page.locator(".opblock-summary").count() >= 6),
        ])
        captura(page, "11_swagger_ui.png")

        navegador.close()

    bien = resultados.count("VERIFICADO")
    log()
    log(f"RESUMEN: {bien}/{len(resultados)} casos VERIFICADO")
    salida.close()
    return 0 if bien == len(resultados) else 1


if __name__ == "__main__":
    sys.exit(main())
