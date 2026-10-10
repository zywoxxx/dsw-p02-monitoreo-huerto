"""
diagramas_p04.py - Dibuja los diagramas de arquitectura de P04 como PNG en docs/p04/diagramas/:
  01_componentes.png   componentes y capas (Angular - API Spring Boot - PostgreSQL)
  02_secuencia.png     secuencia del flujo principal (POST /api/lecturas)
  03_despliegue.png    despliegue local: procesos, puertos y variables
Requiere Pillow: python -m pip install pillow
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent.parent / "docs" / "p04" / "diagramas"
OUT.mkdir(parents=True, exist_ok=True)

VERDE = (47, 107, 58)
VERDE_CLARO = (230, 242, 232)
AZUL = (29, 78, 137)
AZUL_CLARO = (232, 240, 251)
AMBAR = (138, 82, 0)
AMBAR_CLARO = (255, 244, 224)
ROJO = (179, 38, 30)
GRIS = (70, 70, 70)
GRIS_MEDIO = (120, 120, 120)
GRIS_CLARO = (247, 247, 245)
BLANCO = (255, 255, 255)


def fuente(nombre, tam):
    for f in (nombre, "arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(f, tam)
        except OSError:
            continue
    return ImageFont.load_default()


F_TITULO = fuente("arialbd.ttf", 26)
F_CAPA = fuente("arialbd.ttf", 21)
F_CAJA = fuente("arialbd.ttf", 18)
F_TXT = fuente("arial.ttf", 17)
F_MIN = fuente("arial.ttf", 15)
F_MINB = fuente("arialbd.ttf", 15)
F_MONO = fuente("consola.ttf", 15)


def lienzo(ancho, alto, titulo, subtitulo=None):
    img = Image.new("RGB", (ancho, alto), BLANCO)
    d = ImageDraw.Draw(img)
    d.text((40, 24), titulo, font=F_TITULO, fill=GRIS)
    if subtitulo:
        d.text((40, 60), subtitulo, font=F_MIN, fill=GRIS_MEDIO)
    return img, d


def punta(d, p1, p2, color, tam=11):
    """Punta de flecha en p2 viniendo de p1 (solo horizontales o verticales)."""
    x, y = p2
    if p1[1] == p2[1]:
        s = 1 if p2[0] > p1[0] else -1
        d.polygon([(x, y), (x - s * tam, y - tam // 2 - 1), (x - s * tam, y + tam // 2 + 1)], fill=color)
    else:
        s = 1 if p2[1] > p1[1] else -1
        d.polygon([(x, y), (x - tam // 2 - 1, y - s * tam), (x + tam // 2 + 1, y - s * tam)], fill=color)


def flecha(d, p1, p2, color=GRIS, ancho=2, doble=False, punteada=False):
    if punteada:
        x1, y1 = p1
        x2, y2 = p2
        largo = abs(x2 - x1) + abs(y2 - y1)
        pasos = max(1, largo // 14)
        for i in range(pasos):
            a = i / pasos
            b = min(1, a + 0.5 / pasos)
            d.line([(x1 + (x2 - x1) * a, y1 + (y2 - y1) * a), (x1 + (x2 - x1) * b, y1 + (y2 - y1) * b)],
                   fill=color, width=ancho)
    else:
        d.line([p1, p2], fill=color, width=ancho)
    punta(d, p1, p2, color)
    if doble:
        punta(d, p2, p1, color)


def caja(d, x, y, w, titulo, lineas, color=VERDE, fondo=BLANCO, alto_linea=24):
    h = 38 + alto_linea * len(lineas) + 12
    d.rectangle([x, y, x + w, y + h], fill=fondo, outline=color, width=2)
    d.rectangle([x, y, x + w, y + 32], fill=color)
    d.text((x + 10, y + 6), titulo, font=F_CAJA, fill=BLANCO)
    for i, l in enumerate(lineas):
        d.text((x + 12, y + 40 + alto_linea * i), l, font=F_TXT, fill=GRIS)
    return (x, y, x + w, y + h)


def capa(d, x, y, w, h, titulo, detalle, color):
    d.rectangle([x, y, x + w, y + h], fill=GRIS_CLARO, outline=color, width=3)
    d.text((x + 16, y + 12), titulo, font=F_CAPA, fill=color)
    d.text((x + 16, y + 40), detalle, font=F_MIN, fill=GRIS_MEDIO)


def etiqueta(d, x, y, lineas, color=GRIS, fondo=BLANCO, fuente_=F_MIN, borde=None):
    ancho = max(d.textlength(l, font=fuente_) for l in lineas) + 16
    alto = 20 * len(lineas) + 10
    d.rectangle([x, y, x + ancho, y + alto], fill=fondo, outline=borde)
    for i, l in enumerate(lineas):
        d.text((x + 8, y + 5 + 20 * i), l, font=fuente_, fill=color)
    return ancho, alto


# ------------------------------------------------------------------ 01 componentes
def componentes():
    img, d = lienzo(1900, 1180, "PR09 Monitoreo de huerto - Componentes de la arquitectura Web 3.0 (P04)",
                    "Equipo DSW-E01. En verde lo implementado en el esqueleto; en gris lo que solo esta en el contrato.")
    # --- cliente
    capa(d, 40, 100, 520, 900, "Cliente: Angular 16.2.12", "SPA en el navegador - carpeta frontend-angular/", AZUL)
    c1 = caja(d, 70, 180, 460, "Vistas (componentes)",
              ["AppComponent: cabecera, usuario y rol", "AccesoComponent: /acceso",
               "LecturasComponent: /lecturas", "   formulario + historial paginado"], AZUL)
    c2 = caja(d, 70, 370, 460, "Rutas", ["AppRoutingModule", "sesionGuard: sin sesion -> /acceso"], AZUL)
    c3 = caja(d, 70, 510, 460, "core (servicios)",
              ["ApiService: HttpClient sobre /api", "SesionService: token y rol en sessionStorage",
               "TokenInterceptor: agrega Authorization;", "   ante 401 cierra sesion", "modelos.ts: tipos del contrato"], AZUL)
    flecha(d, (300, c1[3]), (300, c2[1]), AZUL)
    flecha(d, (300, c2[3]), (300, c3[1]), AZUL)
    d.rectangle([70, 760, 530, 970], fill=BLANCO, outline=GRIS_MEDIO)
    d.text((82, 770), "No hace", font=F_MINB, fill=GRIS)
    for i, l in enumerate(["No valida reglas de negocio: muestra los", "errores que devuelve la API.",
                           "No decide permisos: oculta el formulario", "por comodidad; el 403 lo da la API.",
                           "No conoce SQL ni la base."]):
        d.text((82, 796 + 22 * i), l, font=F_MIN, fill=GRIS)
    d.text((82, 796 + 22 * 5 + 8), "Pendiente: vistas de alertas y anotaciones", font=F_MIN, fill=GRIS_MEDIO)
    d.text((82, 796 + 22 * 6 + 8), "(siguiente incremento).", font=F_MIN, fill=GRIS_MEDIO)

    # --- API
    capa(d, 700, 100, 700, 1040, "API REST: Spring Boot 2.7.18, Java 11", "Proceso propio con Tomcat embebido - carpeta api-spring/", VERDE)
    a1 = caja(d, 730, 180, 640, "Entrada HTTP",
              ["WebConfig: CORS de un solo origen (CORS_ORIGIN)", "TokenFilter: valida el token en /api/** (401)",
               "ApiExceptionHandler: errores -> JSON del contrato"], VERDE)
    a2 = caja(d, 730, 350, 640, "Controladores REST",
              ["AuthController      POST /api/auth/login", "HealthController    GET  /api/health",
               "SensorController    GET  /api/sensores", "LecturaController   GET, POST /api/lecturas, GET /{id}"], VERDE)
    a3 = caja(d, 730, 545, 640, "Servicios y reglas",
              ["LecturaService: @Transactional lectura + alerta", "ReglasLectura: forma, rango fisico, umbral",
               "Permisos / UsuarioAutenticado: rol -> permiso (403)", "TokenService: emite y valida JWT HS256",
               "CredencialesService: PBKDF2 sobre usuarios.properties"], VERDE)
    a4 = caja(d, 730, 765, 640, "Repositorios JDBC",
              ["SensorRepository, LecturaRepository", "NamedParameterJdbcTemplate + HikariCP", "SQL parametrizado, RETURNING id"], VERDE)
    for a, b in ((a1, a2), (a2, a3), (a3, a4)):
        flecha(d, (1050, a[3]), (1050, b[1]), VERDE)
    d.rectangle([730, 935, 1370, 1115], fill=BLANCO, outline=GRIS_MEDIO)
    d.text((742, 945), "Solo en el contrato (PENDIENTE de implementar)", font=F_MINB, fill=GRIS)
    for i, l in enumerate(["GET /api/zonas", "GET /api/alertas", "GET, POST /api/anotaciones"]):
        d.text((742, 972 + 22 * i), l, font=F_MONO, fill=GRIS_MEDIO)
    d.text((742, 972 + 22 * 3 + 6), "Sus tablas ya existen; faltan controlador, servicio y repositorio.", font=F_MIN, fill=GRIS_MEDIO)
    d.text((742, 972 + 22 * 4 + 6), "springdoc publica /v3/api-docs y /swagger-ui.html desde el codigo.", font=F_MIN, fill=GRIS_MEDIO)

    # --- base
    capa(d, 1540, 100, 320, 700, "PostgreSQL 16", "Mismo modelo de P02 y P03", AMBAR)
    caja(d, 1565, 180, 270, "Tablas (7)",
         ["zona", "variable", "sensor", "umbral", "lectura", "alerta", "anotacion"], AMBAR)
    caja(d, 1565, 445, 270, "Reglas en la base",
         ["PK, FK, UNIQUE", "CHECK de rangos", "CHECK origen, nivel,", "   autor_rol", "indices por instante"], AMBAR)
    d.text((1565, 650), "sql/01_schema.sql", font=F_MONO, fill=GRIS_MEDIO)
    d.text((1565, 674), "sql/02_seed.sql", font=F_MONO, fill=GRIS_MEDIO)
    d.text((1565, 712), "Datos ficticios de laboratorio.", font=F_MIN, fill=GRIS_MEDIO)

    # --- conectores entre capas
    y = 600
    flecha(d, (560, y), (700, y), GRIS, 3, doble=True)
    etiqueta(d, 572, y - 96, ["HTTP + JSON", "/api/**", "Bearer token"], GRIS, BLANCO, F_MINB, GRIS_MEDIO)
    y2 = 830
    flecha(d, (1400, y2), (1540, y2), GRIS, 3, doble=True)
    # la caja de la base termina en 800; se prolonga la linea hasta su borde inferior
    d.rectangle([1540, 800, 1860, 860], fill=GRIS_CLARO, outline=AMBAR, width=3)
    d.text((1556, 820), "puerto 5436 (contenedor)", font=F_MIN, fill=GRIS_MEDIO)
    etiqueta(d, 1412, y2 - 74, ["JDBC", "SQL"], GRIS, BLANCO, F_MINB, GRIS_MEDIO)

    # --- contrato
    d.rectangle([40, 1030, 560, 1140], fill=VERDE_CLARO, outline=VERDE, width=2)
    d.text((56, 1042), "Contrato: docs/p04/openapi.yaml", font=F_CAJA, fill=VERDE)
    d.text((56, 1070), "OpenAPI 3.0.3, escrito antes que el codigo.", font=F_MIN, fill=GRIS)
    d.text((56, 1092), "modelos.ts (cliente) y los DTO (API) lo siguen;", font=F_MIN, fill=GRIS)
    d.text((56, 1114), "scripts/pruebas_api.py valida las respuestas contra el.", font=F_MIN, fill=GRIS)
    flecha(d, (630, 1030), (630, 606), VERDE, 2, punteada=True)
    d.line([(560, 1080), (630, 1080)], fill=VERDE, width=2)
    d.line([(630, 1080), (630, 1030)], fill=VERDE, width=2)
    img.save(OUT / "01_componentes.png")


# ------------------------------------------------------------------ 02 secuencia
def secuencia():
    img, d = lienzo(1900, 1350, "Flujo principal: el observador registra una lectura (POST /api/lecturas)",
                    "Linea continua: llamada. Linea punteada: respuesta. En rojo, las salidas de error que corta cada paso.")
    nombres = ["Observador", "Cliente Angular", "TokenFilter", "LecturaController", "LecturaService", "Repositorios JDBC", "PostgreSQL"]
    detalle = ["(navegador)", "LecturasComponent + ApiService", "", "", "+ ReglasLectura", "", ""]
    xs = [110, 380, 680, 930, 1200, 1480, 1740]
    for x, n, s in zip(xs, nombres, detalle):
        w = max(d.textlength(n, font=F_CAJA), d.textlength(s, font=F_MIN)) + 28
        d.rectangle([x - w / 2, 100, x + w / 2, 156], fill=VERDE, outline=VERDE)
        d.text((x - d.textlength(n, font=F_CAJA) / 2, 106 if s else 117), n, font=F_CAJA, fill=BLANCO)
        if s:
            d.text((x - d.textlength(s, font=F_MIN) / 2, 132), s, font=F_MIN, fill=BLANCO)
        for yy in range(156, 1290, 14):
            d.line([(x, yy), (x, yy + 7)], fill=GRIS_MEDIO, width=1)

    def rotulo(x, y, texto, f, color):
        d.rectangle([x - 3, y, x + d.textlength(texto, font=f) + 3, y + 19], fill=BLANCO)
        d.text((x, y), texto, font=f, fill=color)

    def msj(i, j, y, texto, color=GRIS, respuesta=False, sub=None):
        flecha(d, (xs[i], y), (xs[j], y), color, 2, punteada=respuesta)
        izq = min(xs[i], xs[j]) + 12
        f = F_MINB if not respuesta else F_MIN
        rotulo(izq, y - 25, texto, f, color)
        if sub:
            rotulo(izq, y + 6, sub, F_MIN, GRIS_MEDIO)

    def corte(i, y, texto):
        flecha(d, (xs[i], y), (xs[1], y), ROJO, 2, punteada=True)
        rotulo(xs[1] + 12, y - 24, texto, F_MIN, ROJO)

    y = 210
    msj(0, 1, y, "1. elige sensor, escribe valor y observacion")
    y += 70
    msj(1, 2, y, "2. POST /api/lecturas", sub="Authorization: Bearer <token>   {sensorId, valor, observacion}")
    y += 70
    corte(2, y, "401 NO_AUTENTICADO: sin token, firma alterada o caducado")
    y += 60
    msj(2, 3, y, "3. token valido: usuario y rol")
    y += 60
    msj(3, 4, y, "4. exigir(REGISTRAR_LECTURA); registrar()")
    y += 60
    corte(3, y, "403 ROL_SIN_PERMISO: solo OBSERVADOR captura")
    y += 60
    rotulo(xs[4] + 14, y - 12, "5. validarForma: sensor y valor presentes,", F_MINB, GRIS)
    rotulo(xs[4] + 14, y + 10, "    numerico, <= 2 decimales, observacion <= 200", F_MIN, GRIS)
    y += 70
    corte(4, y, "400 VALIDACION con la lista de campos")
    y += 60
    msj(4, 5, y, "6. sensor porId")
    msj(5, 6, y + 44, "SELECT sensor, variable, umbral")
    y += 110
    corte(4, y, "404 NO_ENCONTRADO (no existe)  /  409 CONFLICTO (inactivo)  /  422 REGLA_DE_NEGOCIO (fuera del rango fisico)")
    y += 60
    d.rectangle([xs[4] - 60, y - 20, xs[6] + 90, y + 190], outline=VERDE, width=2)
    rotulo(xs[4] - 50, y - 14, "transaccion", F_MINB, VERDE)
    msj(4, 5, y + 40, "7. insertarLectura(origen = manual)")
    msj(5, 6, y + 84, "INSERT lectura RETURNING id")
    msj(4, 5, y + 128, "8. si sale del umbral: insertarAlerta")
    msj(5, 6, y + 170, "INSERT alerta (BAJA o ALTA)")
    y += 250
    msj(4, 1, y, "9. 201 Created   Location: /api/lecturas/{id}   cuerpo: Lectura (con alerta si la hubo)", VERDE, respuesta=True)
    y += 60
    msj(1, 0, y, "10. mensaje, aviso de alerta", VERDE, respuesta=True)
    y += 60
    msj(1, 2, y, "11. GET /api/lecturas?pagina=0", sub="recarga el historial; la lectura nueva aparece primero")
    d.text((40, 1310), "Si PostgreSQL no responde, ApiExceptionHandler contesta 503 BASE_NO_DISPONIBLE y la transaccion no deja nada a medias.",
           font=F_MIN, fill=GRIS_MEDIO)
    img.save(OUT / "02_secuencia.png")


# ------------------------------------------------------------------ 03 despliegue
def despliegue():
    img, d = lienzo(1900, 1000, "Despliegue local de P04: procesos, puertos y configuracion",
                    "Todo corre en el equipo de desarrollo (localhost). No se usa infraestructura de terceros.")
    capa(d, 40, 100, 1820, 640, "Equipo de desarrollo (localhost)", "Windows 11 en la verificacion; los comandos son los mismos en Linux", GRIS_MEDIO)
    n1 = caja(d, 70, 200, 330, "Navegador", ["http://localhost:4200", "Angular ya compilado (JS)", "token en sessionStorage"], AZUL, BLANCO)
    n2 = caja(d, 520, 200, 380, "Node 18.20.8  -  puerto 4200", ["npx ng serve", "sirve el cliente Angular", "proxy.conf.json:", "   /api  ->  http://localhost:8081"], AZUL, BLANCO)
    n3 = caja(d, 1020, 200, 400, "JVM Java 11  -  puerto 8081", ["java -jar api-spring.jar", "Spring Boot 2.7.18", "Tomcat embebido 9.0.x", "/api/**, /v3/api-docs, /swagger-ui.html"], VERDE, BLANCO)
    n4 = caja(d, 1540, 200, 290, "Docker  -  puerto 5436", ["imagen postgres:16", "contenedor dsw-p02-huerto-db", "5436 -> 5432", "volumen con los datos"], AMBAR, BLANCO)
    ym = 270
    flecha(d, (n1[2], ym), (n2[0], ym), GRIS, 3, doble=True)
    flecha(d, (n2[2], ym), (n3[0], ym), GRIS, 3, doble=True)
    flecha(d, (n3[2], ym), (n4[0], ym), GRIS, 3, doble=True)
    d.text((n1[2] + 22, ym - 28), "HTTP", font=F_MINB, fill=GRIS)
    d.text((n2[2] + 12, ym - 28), "HTTP /api", font=F_MINB, fill=GRIS)
    d.text((n3[2] + 28, ym - 28), "JDBC", font=F_MINB, fill=GRIS)

    caja(d, 520, 420, 380, "Configuracion del cliente", ["angular.json: puerto y proxy", "sin secretos: el cliente es publico", "package-lock.json fija versiones"], AZUL, BLANCO)
    caja(d, 1020, 420, 400, "Variables de entorno de la API",
         ["DB_URL, DB_USER, DB_PASSWORD", "JWT_SECRET  (si falta: aleatorio por arranque)", "CORS_ORIGIN (http://localhost:4200)", "PORT        (8081)"], VERDE, BLANCO)
    caja(d, 1540, 420, 290, "Configuracion de la base", ["docker/docker-compose.yml", "sql/01_schema.sql", "sql/02_seed.sql"], AMBAR, BLANCO)
    d.text((70, 430), "Por que un proxy en desarrollo:", font=F_MINB, fill=GRIS)
    for i, l in enumerate(["el navegador solo habla con :4200,", "asi que no hay peticiones entre", "origenes. CORS queda configurado", "para cuando el cliente se sirva", "desde otro origen."]):
        d.text((70, 456 + 22 * i), l, font=F_MIN, fill=GRIS)
    d.text((70, 640), "P02 y P03 (WAR en Tomcat 9, puerto 8080) siguen en el repositorio y no comparten proceso con P04; los tres usan la misma base.",
           font=F_MIN, fill=GRIS_MEDIO)
    d.text((70, 664), "En application.properties no hay credenciales: solo referencias ${...} a las variables.", font=F_MIN, fill=GRIS_MEDIO)

    d.rectangle([40, 770, 1860, 960], fill=VERDE_CLARO, outline=VERDE, width=2)
    d.text((60, 782), "Construccion y verificacion", font=F_CAJA, fill=VERDE)
    pasos = [
        ("mvn -f api-spring/pom.xml clean package", "api-spring/target/api-spring.jar (16 pruebas)"),
        ("cd frontend-angular && npm ci && npx ng build", "frontend-angular/dist/frontend-angular (estaticos)"),
        ("./scripts/verify-module.sh M04", "compila, valida el contrato, levanta la API, prueba y apaga"),
        ("./scripts/cleanup.sh", "retira las lecturas de prueba y las carpetas generadas"),
    ]
    for i, (orden, efecto) in enumerate(pasos):
        d.text((60, 818 + 32 * i), orden, font=F_MONO, fill=GRIS)
        d.text((560, 818 + 32 * i), "->  " + efecto, font=F_MONO, fill=GRIS)
    img.save(OUT / "03_despliegue.png")


if __name__ == "__main__":
    componentes()
    secuencia()
    despliegue()
    print("Diagramas en", OUT.relative_to(OUT.parent.parent.parent))
