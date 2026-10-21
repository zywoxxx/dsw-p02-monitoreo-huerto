#!/usr/bin/env python3
"""
pruebas_api.py - Comprobacion del contrato REST (P04 y P05) contra la API en marcha.

Lanza peticiones reales a la API Spring Boot, compara codigo de estado y cuerpo con
docs/p04/openapi.yaml (los cuerpos se validan contra los esquemas del contrato) y
revisa en PostgreSQL que la base cambie solo cuando debe. Cubre salud, acceso,
sensores, lecturas (P04) y zonas, alertas con cambio de estado y anotaciones (P05).

Salidas (EVID_DIR, por omision docs/p05/evidencia/txt):
  pruebas_api.txt             peticion y respuesta de cada caso
  pruebas_api_resultados.txt  VERIFICADO / NO_VERIFICADO por caso
  openapi_generado.json       lo que publica springdoc en /v3/api-docs

Variables:
  API_URL    http://localhost:8081
  PSQL_CMD   docker exec -i dsw-p02-huerto-db psql -U huerto_app -d huerto_db
  ORIGEN_WEB http://localhost:4200
  EVID_DIR   carpeta de la evidencia en texto
  CLAVE_OBSERVADOR / CLAVE_COORDINACION / CLAVE_RESPONSABLE   contrasenas ficticias de laboratorio (ver README)

Las lecturas y anotaciones que crea llevan "[prueba] P05 ..." (las lecturas, origen manual);
scripts/cleanup.sh las retira.
"""
import json
import os
import shlex
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

import yaml
from jsonschema import Draft4Validator, RefResolver

RAIZ = Path(__file__).resolve().parent.parent
TXT = Path(os.environ["EVID_DIR"]) if os.environ.get("EVID_DIR") else RAIZ / "docs" / "p05" / "evidencia" / "txt"
TXT.mkdir(parents=True, exist_ok=True)
API = os.environ.get("API_URL", "http://localhost:8081").rstrip("/")
ORIGEN_WEB = os.environ.get("ORIGEN_WEB", "http://localhost:4200")
PSQL = shlex.split(os.environ.get(
    "PSQL_CMD", "docker exec -i dsw-p02-huerto-db psql -U huerto_app -d huerto_db"))
CLAVES = {
    "observador": os.environ.get("CLAVE_OBSERVADOR", "Observador#2026"),
    "coordinacion": os.environ.get("CLAVE_COORDINACION", "Coordinacion#2026"),
    "responsable": os.environ.get("CLAVE_RESPONSABLE", "Responsable#2026"),
}
SENSOR = 2          # SEN-A-TEMP-01: rango fisico [-10, 60], umbral [15, 32]
ZONA = 1            # Cama A, zona del sensor 2
ZONA_OTRA = 2       # Invernadero 1
SENSOR_PRUEBA_INACTIVO = 5

CONTRATO = yaml.safe_load((RAIZ / "docs" / "p04" / "openapi.yaml").read_text(encoding="utf-8"))
RESOLVER = RefResolver.from_schema(CONTRATO)

bitacora = open(TXT / "pruebas_api.txt", "w", encoding="utf-8")
resultados = []


def log(texto=""):
    print(texto)
    bitacora.write(texto + "\n")


def sql(consulta):
    r = subprocess.run(PSQL + ["-At", "-c", consulta], capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip())
    return r.stdout.strip()


def contar(tabla):
    return int(sql(f"SELECT count(*) FROM {tabla}"))


def estado_alerta(id_alerta):
    """Estado de atencion tal como esta en PostgreSQL: 'atendida|atendida_en es NULL|atendida_por' (p. ej. 't|f|RESPONSABLE')."""
    return sql(f"SELECT atendida, atendida_en IS NULL, coalesce(atendida_por, '') FROM alerta WHERE id = {id_alerta}")


class Respuesta:
    def __init__(self, estado, cabeceras, texto):
        self.estado = estado
        self.cabeceras = cabeceras
        self.texto = texto
        try:
            self.json = json.loads(texto) if texto else None
        except ValueError:
            self.json = None


def pedir(metodo, ruta, cuerpo=None, token=None, cabeceras=None, crudo=None):
    datos = None
    h = {"Accept": "application/json"}
    if cuerpo is not None:
        datos = json.dumps(cuerpo).encode("utf-8")
        h["Content-Type"] = "application/json"
    if crudo is not None:
        datos = crudo.encode("utf-8")
        h["Content-Type"] = "application/json"
    if token:
        h["Authorization"] = "Bearer " + token
    h.update(cabeceras or {})
    peticion = urllib.request.Request(API + ruta, data=datos, method=metodo, headers=h)
    try:
        with urllib.request.urlopen(peticion, timeout=15) as r:
            resp = Respuesta(r.status, r.headers, r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        resp = Respuesta(e.code, e.headers, e.read().decode("utf-8"))
    enviado = crudo if crudo is not None else (json.dumps(cuerpo, ensure_ascii=False) if cuerpo is not None else "")
    if "contrasena" in enviado:
        enviado = '{"usuario": "%s", "contrasena": "<oculta>"}' % (cuerpo or {}).get("usuario", "")
    log(f"  > {metodo} {ruta}" + ("  [Bearer ...]" if token else "") + (f"  {enviado}" if enviado else ""))
    mostrado = resp.texto
    if resp.json and isinstance(resp.json, dict) and "token" in resp.json:
        copia = dict(resp.json)
        copia["token"] = copia["token"][:12] + "...(recortado)"
        mostrado = json.dumps(copia, ensure_ascii=False)
    if len(mostrado) > 600:
        mostrado = mostrado[:600] + " ...(recortado)"
    log(f"  < {resp.estado} {mostrado}")
    return resp


def cumple(esquema, dato):
    """Lista de incumplimientos del dato frente a un esquema del contrato (vacia si cumple)."""
    validador = Draft4Validator({"$ref": "#/components/schemas/" + esquema}, resolver=RESOLVER)
    return [f"{'/'.join(str(p) for p in e.path) or '(raiz)'}: {e.message}" for e in validador.iter_errors(dato)]


def caso(numero, titulo, condiciones):
    """condiciones: lista de (descripcion, booleano)."""
    fallidas = [d for d, bien in condiciones if not bien]
    estado = "VERIFICADO" if not fallidas else "NO_VERIFICADO"
    detalle = "" if not fallidas else "  <- fallo: " + "; ".join(fallidas)
    log(f"  = {estado}{detalle}")
    log()
    resultados.append((numero, titulo, estado, "; ".join(fallidas)))


def titulo(numero, texto):
    log(f"[{numero:02d}] {texto}")


def es_error(resp, estado, codigo):
    return [
        (f"estado {estado} (llego {resp.estado})", resp.estado == estado),
        (f"codigo {codigo}", bool(resp.json) and resp.json.get("codigo") == codigo),
        ("cuerpo cumple el esquema Error", bool(resp.json) and not cumple("Error", resp.json)),
    ]


def campo_en_errores(resp, campo):
    return any(e.get("campo") == campo for e in ((resp.json or {}).get("errores") or []))


def login(usuario):
    return pedir("POST", "/api/auth/login", {"usuario": usuario, "contrasena": CLAVES[usuario]})


def main():
    log(f"pruebas_api.py - {datetime.now().isoformat(timespec='seconds')} - {API}")
    log(f"Contrato: docs/p04/openapi.yaml (OpenAPI {CONTRATO['openapi']}, version {CONTRATO['info']['version']})")
    log()
    n = 0

    n += 1; titulo(n, "GET /api/health sin token")
    r = pedir("GET", "/api/health")
    caso(n, "Salud publica: 200, base UP", [
        ("estado 200", r.estado == 200),
        ("db UP", bool(r.json) and r.json.get("db") == "UP"),
        ("cumple el esquema Salud", bool(r.json) and not cumple("Salud", r.json)),
    ])

    n += 1; titulo(n, "POST /api/auth/login con credenciales correctas (observador)")
    r = login("observador")
    token = (r.json or {}).get("token", "")
    caso(n, "Login correcto: 200 con token y rol OBSERVADOR", [
        ("estado 200", r.estado == 200),
        ("rol OBSERVADOR", bool(r.json) and r.json.get("rol") == "OBSERVADOR"),
        ("token con tres partes", token.count(".") == 2),
        ("cumple el esquema Sesion", bool(r.json) and not cumple("Sesion", r.json)),
    ])

    n += 1; titulo(n, "POST /api/auth/login con contrasena incorrecta")
    r = pedir("POST", "/api/auth/login", {"usuario": "observador", "contrasena": "no-es-la-contrasena"})
    caso(n, "Login incorrecto: 401 sin token", es_error(r, 401, "NO_AUTENTICADO") + [
        ("sin token en la respuesta", "token" not in (r.json or {})),
    ])

    n += 1; titulo(n, "POST /api/auth/login sin contrasena")
    r = pedir("POST", "/api/auth/login", {"usuario": "observador"})
    caso(n, "Login incompleto: 400", es_error(r, 400, "VALIDACION"))

    n += 1; titulo(n, "GET /api/sensores sin token")
    r = pedir("GET", "/api/sensores")
    caso(n, "Recurso protegido sin token: 401", es_error(r, 401, "NO_AUTENTICADO") + [
        ("cabecera WWW-Authenticate: Bearer", "Bearer" in (r.cabeceras.get("WWW-Authenticate") or "")),
    ])

    n += 1; titulo(n, "GET /api/sensores con un token alterado")
    alterado = token[:-3] + ("AAA" if not token.endswith("AAA") else "BBB")
    r = pedir("GET", "/api/sensores", token=alterado)
    caso(n, "Token con firma alterada: 401", es_error(r, 401, "NO_AUTENTICADO"))

    n += 1; titulo(n, "GET /api/sensores con token")
    r = pedir("GET", "/api/sensores", token=token)
    lista = r.json if isinstance(r.json, list) else []
    caso(n, "Catalogo de sensores: 200 con rango fisico y umbral", [
        ("estado 200", r.estado == 200),
        ("hay sensores", len(lista) > 0),
        ("cada elemento cumple el esquema Sensor", all(not cumple("Sensor", s) for s in lista)),
        ("SEN-A-TEMP-01 con umbral 15-32",
         any(s["codigo"] == "SEN-A-TEMP-01" and s.get("umbralMinimo") == 15 and s.get("umbralMaximo") == 32 for s in lista)),
    ])

    n += 1; titulo(n, "GET /api/sensores?zonaId=abc")
    r = pedir("GET", "/api/sensores?zonaId=abc", token=token)
    caso(n, "Parametro de consulta no numerico: 400", es_error(r, 400, "VALIDACION"))

    n += 1; titulo(n, "GET /api/lecturas?tamano=3")
    r = pedir("GET", "/api/lecturas?tamano=3", token=token)
    total_bd = contar("lectura")
    caso(n, "Historial paginado: 200 y total igual al de PostgreSQL", [
        ("estado 200", r.estado == 200),
        ("cumple el esquema PaginaLecturas", bool(r.json) and not cumple("PaginaLecturas", r.json)),
        ("a lo mas 3 elementos", bool(r.json) and len(r.json.get("contenido", [])) <= 3),
        (f"total = {total_bd}", bool(r.json) and r.json.get("total") == total_bd),
    ])

    n += 1; titulo(n, "GET /api/lecturas?origen=simulado")
    r = pedir("GET", "/api/lecturas?origen=simulado&tamano=100", token=token)
    contenido = (r.json or {}).get("contenido", [])
    caso(n, "Filtro por procedencia: solo lecturas simuladas", [
        ("estado 200", r.estado == 200),
        ("todas con origen simulado", len(contenido) > 0 and all(l["origen"] == "simulado" for l in contenido)),
    ])

    n += 1; titulo(n, "GET /api/lecturas?origen=inventado")
    r = pedir("GET", "/api/lecturas?origen=inventado", token=token)
    caso(n, "Procedencia desconocida: 400", es_error(r, 400, "VALIDACION"))

    n += 1; titulo(n, "POST /api/lecturas valor 25.5 (dentro del umbral)")
    antes_l, antes_a = contar("lectura"), contar("alerta")
    r = pedir("POST", "/api/lecturas",
              {"sensorId": SENSOR, "valor": 25.5, "observacion": "[prueba] P05 lectura valida"}, token=token)
    creada = (r.json or {}).get("id")
    ubicacion = r.cabeceras.get("Location") or ""
    caso(n, "Lectura valida: 201, Location, procedencia manual, sin alerta, +1 lectura", [
        ("estado 201", r.estado == 201),
        ("cumple el esquema Lectura", bool(r.json) and not cumple("Lectura", r.json)),
        ("Location apunta a la lectura creada", ubicacion.endswith(f"/api/lecturas/{creada}")),
        ("origen manual", bool(r.json) and r.json.get("origen") == "manual"),
        ("sin alerta", bool(r.json) and "alerta" not in r.json),
        ("lectura +1", contar("lectura") == antes_l + 1),
        ("alerta sin cambio", contar("alerta") == antes_a),
    ])

    n += 1; titulo(n, f"GET /api/lecturas/{creada}")
    r = pedir("GET", f"/api/lecturas/{creada}", token=token)
    caso(n, "La lectura creada se recupera por su identificador", [
        ("estado 200", r.estado == 200),
        ("mismo id", bool(r.json) and r.json.get("id") == creada),
        ("valor 25.5", bool(r.json) and float(r.json.get("valor", 0)) == 25.5),
    ])

    n += 1; titulo(n, "POST /api/lecturas valor 38 (sobre el umbral)")
    antes_l, antes_a = contar("lectura"), contar("alerta")
    r = pedir("POST", "/api/lecturas",
              {"sensorId": SENSOR, "valor": 38, "observacion": "[prueba] P05 alerta alta"}, token=token)
    lectura_38 = (r.json or {}).get("id") or 0
    id_alerta = int(sql(f"SELECT coalesce(max(id), 0) FROM alerta WHERE lectura_id = {lectura_38}"))
    caso(n, "Lectura sobre el umbral: 201 con alerta ALTA, +1 lectura y +1 alerta", [
        ("estado 201", r.estado == 201),
        ("alerta ALTA", bool(r.json) and (r.json.get("alerta") or {}).get("nivel") == "ALTA"),
        ("cumple el esquema Lectura", bool(r.json) and not cumple("Lectura", r.json)),
        ("lectura +1", contar("lectura") == antes_l + 1),
        ("alerta +1", contar("alerta") == antes_a + 1),
        ("la alerta de esa lectura existe en PostgreSQL", id_alerta > 0),
    ])

    n += 1; titulo(n, "POST /api/lecturas valor 10 (bajo el umbral)")
    antes_a = contar("alerta")
    r = pedir("POST", "/api/lecturas",
              {"sensorId": SENSOR, "valor": 10, "observacion": "[prueba] P05 alerta baja"}, token=token)
    caso(n, "Lectura bajo el umbral: 201 con alerta BAJA", [
        ("estado 201", r.estado == 201),
        ("alerta BAJA", bool(r.json) and (r.json.get("alerta") or {}).get("nivel") == "BAJA"),
        ("alerta +1", contar("alerta") == antes_a + 1),
    ])

    n += 1; titulo(n, "POST /api/lecturas valores 15 y 32 (limites del umbral)")
    antes_a = contar("alerta")
    r1 = pedir("POST", "/api/lecturas",
               {"sensorId": SENSOR, "valor": 15, "observacion": "[prueba] P05 limite inferior"}, token=token)
    r2 = pedir("POST", "/api/lecturas",
               {"sensorId": SENSOR, "valor": 32, "observacion": "[prueba] P05 limite superior"}, token=token)
    caso(n, "Limites inclusivos: 15 y 32 se guardan sin alerta", [
        ("ambas 201", r1.estado == 201 and r2.estado == 201),
        ("sin alerta", "alerta" not in (r1.json or {}) and "alerta" not in (r2.json or {})),
        ("alerta sin cambio", contar("alerta") == antes_a),
    ])

    negativos = [
        ("valor no numerico \"abc\"", '{"sensorId": %d, "valor": "abc"}' % SENSOR, 400, "VALIDACION"),
        ("valor con tres decimales 24.555", '{"sensorId": %d, "valor": 24.555}' % SENSOR, 400, "VALIDACION"),
        ("sin valor", '{"sensorId": %d}' % SENSOR, 400, "VALIDACION"),
        ("sin sensor", '{"valor": 25}', 400, "VALIDACION"),
        ("JSON mal formado", '{"sensorId": 2, "valor": ', 400, "VALIDACION"),
        ("observacion de 201 caracteres",
         json.dumps({"sensorId": SENSOR, "valor": 25, "observacion": "x" * 201}), 400, "VALIDACION"),
        ("valor 150, fuera del rango fisico", '{"sensorId": %d, "valor": 150}' % SENSOR, 422, "REGLA_DE_NEGOCIO"),
        ("sensor 999, no existe", '{"sensorId": 999, "valor": 25}', 404, "NO_ENCONTRADO"),
    ]
    for nombre, cuerpo, estado, codigo in negativos:
        n += 1; titulo(n, f"POST /api/lecturas {nombre}")
        antes_l, antes_a = contar("lectura"), contar("alerta")
        r = pedir("POST", "/api/lecturas", crudo=cuerpo, token=token)
        caso(n, f"Rechazo: {nombre} -> {estado} {codigo}, la base no cambia", es_error(r, estado, codigo) + [
            ("lectura sin cambio", contar("lectura") == antes_l),
            ("alerta sin cambio", contar("alerta") == antes_a),
        ])

    n += 1; titulo(n, "POST /api/lecturas sobre un sensor inactivo")
    estaba_activo = sql(f"SELECT activo FROM sensor WHERE id = {SENSOR_PRUEBA_INACTIVO}") == "t"
    try:
        sql(f"UPDATE sensor SET activo = false WHERE id = {SENSOR_PRUEBA_INACTIVO}")
        log(f"  (el sensor {SENSOR_PRUEBA_INACTIVO} se desactiva solo durante este caso)")
        antes_l = contar("lectura")
        r = pedir("POST", "/api/lecturas", {"sensorId": SENSOR_PRUEBA_INACTIVO, "valor": 5000}, token=token)
        condiciones = es_error(r, 409, "CONFLICTO") + [("lectura sin cambio", contar("lectura") == antes_l)]
    finally:
        sql(f"UPDATE sensor SET activo = {'true' if estaba_activo else 'false'} WHERE id = {SENSOR_PRUEBA_INACTIVO}")
    condiciones.append(("el sensor vuelve a su estado original",
                        (sql(f"SELECT activo FROM sensor WHERE id = {SENSOR_PRUEBA_INACTIVO}") == "t") == estaba_activo))
    caso(n, "Sensor inactivo: 409 y la base no cambia", condiciones)

    n += 1; titulo(n, "POST /api/lecturas sin token")
    antes_l = contar("lectura")
    r = pedir("POST", "/api/lecturas", {"sensorId": SENSOR, "valor": 25})
    caso(n, "Registrar sin token: 401 y la base no cambia", es_error(r, 401, "NO_AUTENTICADO") + [
        ("lectura sin cambio", contar("lectura") == antes_l),
    ])

    n += 1; titulo(n, "POST /api/lecturas con el rol COORDINACION")
    r = login("coordinacion")
    token_coord = (r.json or {}).get("token", "")
    antes_l = contar("lectura")
    r = pedir("POST", "/api/lecturas", {"sensorId": SENSOR, "valor": 25}, token=token_coord)
    r_lee = pedir("GET", "/api/lecturas?tamano=1", token=token_coord)
    caso(n, "Rol sin permiso de captura: 403 al registrar, 200 al consultar", es_error(r, 403, "ROL_SIN_PERMISO") + [
        ("lectura sin cambio", contar("lectura") == antes_l),
        ("consulta permitida (200)", r_lee.estado == 200),
    ])

    n += 1; titulo(n, "GET /api/lecturas/999999")
    r = pedir("GET", "/api/lecturas/999999", token=token)
    caso(n, "Lectura inexistente: 404", es_error(r, 404, "NO_ENCONTRADO"))

    n += 1; titulo(n, "OPTIONS /api/lecturas (preflight CORS)")
    pre = {"Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "authorization,content-type"}
    r_ok = pedir("OPTIONS", "/api/lecturas", cabeceras=dict(pre, Origin=ORIGEN_WEB))
    r_no = pedir("OPTIONS", "/api/lecturas", cabeceras=dict(pre, Origin="http://sitio-ajeno.example"))
    log(f"  Access-Control-Allow-Origin para {ORIGEN_WEB}: {r_ok.cabeceras.get('Access-Control-Allow-Origin')}")
    log(f"  Access-Control-Allow-Origin para sitio ajeno: {r_no.cabeceras.get('Access-Control-Allow-Origin')}")
    caso(n, "CORS: solo se admite el origen del cliente Angular", [
        ("preflight del cliente 200", r_ok.estado == 200),
        ("origen del cliente permitido", r_ok.cabeceras.get("Access-Control-Allow-Origin") == ORIGEN_WEB),
        ("origen ajeno rechazado (403)", r_no.estado == 403),
        ("origen ajeno sin cabecera de permiso", r_no.cabeceras.get("Access-Control-Allow-Origin") is None),
    ])

    # ---------------------------------------------------------------- P05: zonas, alertas y anotaciones
    n += 1; titulo(n, "GET /api/zonas sin token")
    r = pedir("GET", "/api/zonas")
    caso(n, "Catalogo de zonas sin token: 401", es_error(r, 401, "NO_AUTENTICADO"))

    n += 1; titulo(n, "GET /api/zonas con token")
    r = pedir("GET", "/api/zonas", token=token)
    zonas = r.json if isinstance(r.json, list) else []
    caso(n, "Catalogo de zonas: 200 con las dos zonas ordenadas por nombre", [
        ("estado 200", r.estado == 200),
        ("cada elemento cumple el esquema Zona", len(zonas) > 0 and all(not cumple("Zona", z) for z in zonas)),
        ("Cama A e Invernadero 1, en ese orden", [z.get("nombre") for z in zonas] == ["Cama A", "Invernadero 1"]),
    ])

    n += 1; titulo(n, "GET /api/alertas?tamano=5")
    r = pedir("GET", "/api/alertas?tamano=5", token=token)
    total_bd = contar("alerta")
    caso(n, "Alertas paginadas: 200 y total igual al de PostgreSQL", [
        ("estado 200", r.estado == 200),
        ("cumple el esquema PaginaAlertas", bool(r.json) and not cumple("PaginaAlertas", r.json)),
        ("a lo mas 5 elementos", bool(r.json) and len(r.json.get("contenido", [])) <= 5),
        (f"total = {total_bd}", bool(r.json) and r.json.get("total") == total_bd),
    ])

    n += 1; titulo(n, "GET /api/alertas?nivel=ALTA&tamano=100")
    r = pedir("GET", "/api/alertas?nivel=ALTA&tamano=100", token=token)
    contenido = (r.json or {}).get("contenido", [])
    caso(n, "Filtro por nivel: solo alertas ALTA", [
        ("estado 200", r.estado == 200),
        ("todas con nivel ALTA", len(contenido) > 0 and all(a["nivel"] == "ALTA" for a in contenido)),
    ])

    n += 1; titulo(n, "GET /api/alertas?nivel=MEDIA")
    r = pedir("GET", "/api/alertas?nivel=MEDIA", token=token)
    caso(n, "Nivel desconocido: 400", es_error(r, 400, "VALIDACION"))

    n += 1; titulo(n, "GET /api/alertas?atendida=false&tamano=100")
    r = pedir("GET", "/api/alertas?atendida=false&tamano=100", token=token)
    contenido = (r.json or {}).get("contenido", [])
    caso(n, "Filtro por estado: solo alertas pendientes", [
        ("estado 200", r.estado == 200),
        ("todas con atendida false", len(contenido) > 0 and all(a["atendida"] is False for a in contenido)),
    ])

    n += 1; titulo(n, "GET /api/alertas?atendida=quiza")
    r = pedir("GET", "/api/alertas?atendida=quiza", token=token)
    caso(n, "Parametro booleano no valido: 400", es_error(r, 400, "VALIDACION"))

    n += 1; titulo(n, f"GET /api/alertas/{id_alerta} (la alerta de la lectura 38)")
    r = pedir("GET", f"/api/alertas/{id_alerta}", token=token)
    caso(n, "La alerta creada por la lectura 38 se recupera pendiente", [
        ("estado 200", r.estado == 200),
        ("cumple el esquema Alerta", bool(r.json) and not cumple("Alerta", r.json)),
        (f"lecturaId = {lectura_38}", bool(r.json) and r.json.get("lecturaId") == lectura_38),
        ("atendida false", bool(r.json) and r.json.get("atendida") is False),
        ("sin atendidaEn ni atendidaPor", bool(r.json) and "atendidaEn" not in r.json and "atendidaPor" not in r.json),
    ])

    n += 1; titulo(n, "GET /api/alertas/999999")
    r = pedir("GET", "/api/alertas/999999", token=token)
    caso(n, "Alerta inexistente: 404", es_error(r, 404, "NO_ENCONTRADO"))

    n += 1; titulo(n, f"PATCH /api/alertas/{id_alerta} con el rol OBSERVADOR")
    antes = estado_alerta(id_alerta)
    r = pedir("PATCH", f"/api/alertas/{id_alerta}", {"atendida": True}, token=token)
    caso(n, "OBSERVADOR no atiende alertas: 403 y la base no cambia", es_error(r, 403, "ROL_SIN_PERMISO") + [
        ("alerta sin cambio", estado_alerta(id_alerta) == antes),
    ])

    n += 1; titulo(n, f"PATCH /api/alertas/{id_alerta} con el rol COORDINACION")
    r = pedir("PATCH", f"/api/alertas/{id_alerta}", {"atendida": True}, token=token_coord)
    caso(n, "COORDINACION no atiende alertas: 403 y la base no cambia", es_error(r, 403, "ROL_SIN_PERMISO") + [
        ("alerta sin cambio", estado_alerta(id_alerta) == antes),
    ])

    n += 1; titulo(n, f"PATCH /api/alertas/{id_alerta} {{atendida: true}} con el rol RESPONSABLE")
    r = login("responsable")
    token_resp = (r.json or {}).get("token", "")
    r = pedir("PATCH", f"/api/alertas/{id_alerta}", {"atendida": True}, token=token_resp)
    caso(n, "RESPONSABLE atiende la alerta: 200, rol e instante los pone el servidor, PostgreSQL actualizado", [
        ("estado 200", r.estado == 200),
        ("cumple el esquema Alerta", bool(r.json) and not cumple("Alerta", r.json)),
        ("atendida true", bool(r.json) and r.json.get("atendida") is True),
        ("atendidaPor RESPONSABLE", bool(r.json) and r.json.get("atendidaPor") == "RESPONSABLE"),
        ("atendidaEn presente", bool(r.json) and bool(r.json.get("atendidaEn"))),
        ("en PostgreSQL atendida = true, atendida_en con valor y atendida_por = RESPONSABLE",
         estado_alerta(id_alerta) == "t|f|RESPONSABLE"),
    ])

    n += 1; titulo(n, f"PATCH /api/alertas/{id_alerta} {{atendida: true}} otra vez")
    antes = estado_alerta(id_alerta)
    r = pedir("PATCH", f"/api/alertas/{id_alerta}", {"atendida": True}, token=token_resp)
    caso(n, "Repetir el mismo estado: 409 CONFLICTO y la base no cambia", es_error(r, 409, "CONFLICTO") + [
        ("alerta sin cambio", estado_alerta(id_alerta) == antes),
    ])

    n += 1; titulo(n, f"PATCH /api/alertas/{id_alerta} con cuerpo {{}}")
    r = pedir("PATCH", f"/api/alertas/{id_alerta}", crudo="{}", token=token_resp)
    caso(n, "Sin el campo atendida: 400 VALIDACION senalando el campo, la base no cambia",
         es_error(r, 400, "VALIDACION") + [
             ("errores[] senala el campo atendida", campo_en_errores(r, "atendida")),
             ("alerta sin cambio", estado_alerta(id_alerta) == antes),
         ])

    n += 1; titulo(n, f"PATCH /api/alertas/{id_alerta} con atendida \"si\"")
    r = pedir("PATCH", f"/api/alertas/{id_alerta}", crudo='{"atendida": "si"}', token=token_resp)
    caso(n, "atendida no booleano: 400 y la base no cambia", es_error(r, 400, "VALIDACION") + [
        ("alerta sin cambio", estado_alerta(id_alerta) == antes),
    ])

    n += 1; titulo(n, "PATCH /api/alertas/999999")
    r = pedir("PATCH", "/api/alertas/999999", {"atendida": True}, token=token_resp)
    caso(n, "Atender una alerta inexistente: 404", es_error(r, 404, "NO_ENCONTRADO"))

    n += 1; titulo(n, f"PATCH /api/alertas/{id_alerta} sin token")
    r = pedir("PATCH", f"/api/alertas/{id_alerta}", {"atendida": False})
    caso(n, "Cambiar el estado sin token: 401 y la base no cambia", es_error(r, 401, "NO_AUTENTICADO") + [
        ("alerta sin cambio", estado_alerta(id_alerta) == antes),
    ])

    n += 1; titulo(n, f"PATCH /api/alertas/{id_alerta} {{atendida: false}} (reabrir)")
    r = pedir("PATCH", f"/api/alertas/{id_alerta}", {"atendida": False}, token=token_resp)
    caso(n, "Reabrir la alerta: 200 sin atendidaEn ni atendidaPor; ambas columnas NULL en PostgreSQL", [
        ("estado 200", r.estado == 200),
        ("cumple el esquema Alerta", bool(r.json) and not cumple("Alerta", r.json)),
        ("atendida false", bool(r.json) and r.json.get("atendida") is False),
        ("sin atendidaEn ni atendidaPor", bool(r.json) and "atendidaEn" not in r.json and "atendidaPor" not in r.json),
        ("en PostgreSQL atendida = false y columnas NULL", estado_alerta(id_alerta) == "f|t|"),
    ])

    n += 1; titulo(n, "GET /api/anotaciones?tamano=5")
    r = pedir("GET", "/api/anotaciones?tamano=5", token=token)
    total_bd = contar("anotacion")
    caso(n, "Anotaciones paginadas: 200 y total igual al de PostgreSQL", [
        ("estado 200", r.estado == 200),
        ("cumple el esquema PaginaAnotaciones", bool(r.json) and not cumple("PaginaAnotaciones", r.json)),
        ("a lo mas 5 elementos", bool(r.json) and len(r.json.get("contenido", [])) <= 5),
        (f"total = {total_bd}", bool(r.json) and r.json.get("total") == total_bd),
    ])

    n += 1; titulo(n, "GET /api/anotaciones?zonaId=abc")
    r = pedir("GET", "/api/anotaciones?zonaId=abc", token=token)
    caso(n, "Parametro de consulta no numerico: 400", es_error(r, 400, "VALIDACION"))

    n += 1; titulo(n, "POST /api/anotaciones con el rol COORDINACION (solo zona)")
    antes_n = contar("anotacion")
    r = pedir("POST", "/api/anotaciones",
              {"zonaId": ZONA, "texto": "[prueba] P05 anotacion de coordinacion"}, token=token_coord)
    anotacion = (r.json or {}).get("id")
    ubicacion = r.cabeceras.get("Location") or ""
    caso(n, "Anotacion de zona: 201, Location, firmada con el rol del token, +1 anotacion", [
        ("estado 201", r.estado == 201),
        ("cumple el esquema Anotacion", bool(r.json) and not cumple("Anotacion", r.json)),
        ("Location apunta a la anotacion creada", ubicacion.endswith(f"/api/anotaciones/{anotacion}")),
        ("autorRol COORDINACION", bool(r.json) and r.json.get("autorRol") == "COORDINACION"),
        ("zona Cama A", bool(r.json) and r.json.get("zona") == "Cama A"),
        ("sin lecturaId", bool(r.json) and "lecturaId" not in r.json),
        ("anotacion +1", contar("anotacion") == antes_n + 1),
    ])

    n += 1; titulo(n, f"POST /api/anotaciones con el rol OBSERVADOR sobre la lectura {creada}")
    antes_n = contar("anotacion")
    r = pedir("POST", "/api/anotaciones",
              {"zonaId": ZONA, "lecturaId": creada, "texto": "[prueba] P05 anotacion sobre una lectura"}, token=token)
    caso(n, "Anotacion sobre una lectura de la zona: 201 con lecturaId y rol OBSERVADOR", [
        ("estado 201", r.estado == 201),
        ("cumple el esquema Anotacion", bool(r.json) and not cumple("Anotacion", r.json)),
        ("autorRol OBSERVADOR", bool(r.json) and r.json.get("autorRol") == "OBSERVADOR"),
        (f"lecturaId = {creada}", bool(r.json) and r.json.get("lecturaId") == creada),
        ("anotacion +1", contar("anotacion") == antes_n + 1),
    ])

    n += 1; titulo(n, f"GET /api/anotaciones/{anotacion}")
    r = pedir("GET", f"/api/anotaciones/{anotacion}", token=token)
    caso(n, "La anotacion creada se recupera por su identificador", [
        ("estado 200", r.estado == 200),
        ("cumple el esquema Anotacion", bool(r.json) and not cumple("Anotacion", r.json)),
        ("mismo id", bool(r.json) and r.json.get("id") == anotacion),
    ])

    n += 1; titulo(n, "GET /api/anotaciones/999999")
    r = pedir("GET", "/api/anotaciones/999999", token=token)
    caso(n, "Anotacion inexistente: 404", es_error(r, 404, "NO_ENCONTRADO"))

    negativos = [
        ("texto \"ok\" (2 caracteres)", {"zonaId": ZONA, "texto": "ok"}, 400, "VALIDACION", "texto"),
        ("texto de 301 caracteres", {"zonaId": ZONA, "texto": "[prueba] P05 " + "x" * 288}, 400, "VALIDACION", "texto"),
        ("texto \"   ab   \" (recortado quedan 2)", {"zonaId": ZONA, "texto": "   ab   "}, 400, "VALIDACION", "texto"),
        ("sin zonaId", {"texto": "[prueba] P05 sin zona"}, 400, "VALIDACION", "zonaId"),
        ("sin texto", {"zonaId": ZONA}, 400, "VALIDACION", "texto"),
        ("lecturaId -3", {"zonaId": ZONA, "lecturaId": -3, "texto": "[prueba] P05 lectura negativa"},
         400, "VALIDACION", "lecturaId"),
        ("zonaId 999, no existe", {"zonaId": 999, "texto": "[prueba] P05 zona inexistente"}, 404, "NO_ENCONTRADO", None),
        ("lecturaId 999999, no existe", {"zonaId": ZONA, "lecturaId": 999999, "texto": "[prueba] P05 lectura inexistente"},
         404, "NO_ENCONTRADO", None),
        (f"zonaId {ZONA_OTRA} con la lectura {creada}, que es de la zona {ZONA}",
         {"zonaId": ZONA_OTRA, "lecturaId": creada, "texto": "[prueba] P05 lectura de otra zona"},
         422, "REGLA_DE_NEGOCIO", None),
    ]
    for nombre, cuerpo, estado, codigo, campo in negativos:
        n += 1; titulo(n, f"POST /api/anotaciones {nombre}")
        antes_n = contar("anotacion")
        r = pedir("POST", "/api/anotaciones", cuerpo, token=token)
        condiciones = es_error(r, estado, codigo)
        if campo:
            condiciones.append((f"errores[] senala el campo {campo}", campo_en_errores(r, campo)))
        caso(n, f"Rechazo: {nombre} -> {estado} {codigo}, la base no cambia", condiciones + [
            ("anotacion sin cambio", contar("anotacion") == antes_n),
        ])

    n += 1; titulo(n, "POST /api/anotaciones sin token")
    antes_n = contar("anotacion")
    r = pedir("POST", "/api/anotaciones", {"zonaId": ZONA, "texto": "[prueba] P05 sin token"})
    caso(n, "Anotar sin token: 401 y la base no cambia", es_error(r, 401, "NO_AUTENTICADO") + [
        ("anotacion sin cambio", contar("anotacion") == antes_n),
    ])

    n += 1; titulo(n, "GET /v3/api-docs (OpenAPI generado por springdoc) frente al contrato escrito")
    r = pedir("GET", "/v3/api-docs")
    generado = r.json or {}
    metodos = ("get", "post", "put", "patch", "delete")
    en_codigo = {(ruta, m) for ruta, ops in generado.get("paths", {}).items() for m in ops if m in metodos}
    en_contrato = {(ruta, m) for ruta, ops in CONTRATO["paths"].items() for m in ops if m in metodos}
    sobran = sorted(en_codigo - en_contrato)
    pendientes = sorted(en_contrato - en_codigo)
    log("  Operaciones implementadas: " + ", ".join(f"{m.upper()} {ruta}" for ruta, m in sorted(en_codigo)))
    log("  En el contrato y sin implementar: "
        + (", ".join(f"{m.upper()} {ruta}" for ruta, m in pendientes) or "ninguna"))
    (TXT / "openapi_generado.json").write_text(json.dumps(generado, indent=2, ensure_ascii=False), encoding="utf-8")
    caso(n, "Todo lo implementado esta en el contrato y no hay operaciones del contrato sin implementar", [
        ("estado 200", r.estado == 200),
        ("hay operaciones implementadas", len(en_codigo) > 0),
        (f"ninguna operacion fuera del contrato {sobran}", not sobran),
        (f"ninguna operacion del contrato sin implementar {pendientes}", not pendientes),
    ])

    verificados = sum(1 for r in resultados if r[2] == "VERIFICADO")
    with open(TXT / "pruebas_api_resultados.txt", "w", encoding="utf-8") as f:
        f.write(f"pruebas_api.py - {datetime.now().isoformat(timespec='seconds')} - {API}\n")
        f.write(f"Casos: {len(resultados)}  VERIFICADO: {verificados}  NO_VERIFICADO: {len(resultados) - verificados}\n\n")
        for numero, nombre, estado, detalle in resultados:
            f.write(f"{numero:02d} | {estado:<13} | {nombre}" + (f" | {detalle}" if detalle else "") + "\n")
    log(f"RESUMEN: {verificados}/{len(resultados)} casos VERIFICADO")
    bitacora.close()
    return 0 if verificados == len(resultados) else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # la API o la base no responden
        log(f"ERROR: {e}")
        bitacora.close()
        sys.exit(2)
