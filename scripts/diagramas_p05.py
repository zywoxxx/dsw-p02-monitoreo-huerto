"""
diagramas_p05.py - Dibuja los diagramas de P05 como PNG en docs/p05/diagramas/:
  01_componentes.png         componentes con todo el contrato implementado
  02_secuencia_atencion.png  secuencia del cambio de estado (PATCH /api/alertas/{id})
  03_estados_alerta.png      estados de una alerta y quien los cambia
  04_despliegue.png          despliegue local con la migracion de P05
Reutiliza los trazos de diagramas_p04.py. Requiere Pillow.
"""
from pathlib import Path

from diagramas_p04 import (AMBAR, AZUL, BLANCO, F_CAJA, F_MIN, F_MINB, F_MONO, GRIS, GRIS_CLARO, GRIS_MEDIO,
                           ROJO, VERDE, VERDE_CLARO, caja, capa, etiqueta, flecha, lienzo)

OUT = Path(__file__).resolve().parent.parent / "docs" / "p05" / "diagramas"
OUT.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------------ 01 componentes
def componentes():
    img, d = lienzo(1900, 1180, "PR09 Monitoreo de huerto - Componentes de la integracion Web 3.0 (P05)",
                    "Equipo DSW-E01. Las 13 operaciones del contrato estan implementadas; en negrita lo que llego en P05.")
    # --- cliente
    capa(d, 40, 100, 520, 1040, "Cliente: Angular 16.2.12", "SPA en el navegador - carpeta frontend-angular/", AZUL)
    c1 = caja(d, 70, 180, 460, "Vistas (componentes)",
              ["AppComponent: cabecera, usuario, rol y menu", "AccesoComponent: /acceso",
               "LecturasComponent: /lecturas", "AlertasComponent: /alertas (P05)",
               "   filtros, atender / reabrir", "AnotacionesComponent: /anotaciones (P05)",
               "   formulario + lista paginada"], AZUL)
    c2 = caja(d, 70, 445, 460, "Rutas", ["AppRoutingModule: 4 rutas", "sesionGuard: sin sesion -> /acceso"], AZUL)
    c3 = caja(d, 70, 585, 460, "core (servicios)",
              ["ApiService: 9 llamadas sobre /api", "SesionService: token, rol, permisos de vista",
               "TokenInterceptor: Authorization;", "   ante 401 cierra sesion", "modelos.ts: tipos del contrato 0.5.0"], AZUL)
    flecha(d, (300, c1[3]), (300, c2[1]), AZUL)
    flecha(d, (300, c2[3]), (300, c3[1]), AZUL)
    d.rectangle([70, 835, 530, 1005], fill=BLANCO, outline=GRIS_MEDIO)
    d.text((82, 845), "No hace", font=F_MINB, fill=GRIS)
    for i, l in enumerate(["No valida reglas de negocio: muestra los", "errores que devuelve la API (400, 404, 409, 422).",
                           "No decide permisos: oculta botones por", "comodidad; el 403 lo da la API.",
                           "No recorta el texto de la anotacion: deja", "que la API responda el 400 de 301 caracteres."]):
        d.text((82, 871 + 22 * i), l, font=F_MIN, fill=GRIS)

    # --- API
    capa(d, 700, 100, 700, 1040, "API REST: Spring Boot 2.7.18, Java 11", "Proceso propio con Tomcat embebido - carpeta api-spring/", VERDE)
    a1 = caja(d, 730, 180, 640, "Entrada HTTP",
              ["WebConfig: CORS de un origen; GET, POST, PATCH", "TokenFilter: valida el token en /api/** (401)",
               "ApiExceptionHandler: errores -> JSON del contrato"], VERDE)
    a2 = caja(d, 730, 350, 640, "Controladores REST (13 operaciones)",
              ["AuthController       POST /api/auth/login", "HealthController     GET  /api/health",
               "ZonaController       GET  /api/zonas  (P05)", "SensorController     GET  /api/sensores",
               "LecturaController    GET, POST /api/lecturas, GET /{id}",
               "AlertaController     GET /api/alertas, GET /{id},", "                     PATCH /{id}  (P05, cambio de estado)",
               "AnotacionController  GET, POST /api/anotaciones,", "                     GET /{id}  (P05)"], VERDE)
    a3 = caja(d, 730, 640, 640, "Servicios y reglas",
              ["LecturaService: @Transactional lectura + alerta", "AlertaService: @Transactional atender / reabrir (P05)",
               "AnotacionService: zona, lectura y su zona (P05)", "ReglasLectura, ReglasAnotacion: reglas puras",
               "Permisos: CONSULTAR, REGISTRAR_LECTURA, ANOTAR,", "   ATENDER_ALERTA (solo RESPONSABLE)",
               "TokenService, CredencialesService"], VERDE)
    a4 = caja(d, 730, 885, 640, "Repositorios JDBC",
              ["Sensor, Lectura, Zona, Alerta, Anotacion (P05)", "NamedParameterJdbcTemplate + HikariCP",
               "SQL parametrizado, RETURNING id, UPDATE de estado"], VERDE)
    for a, b in ((a1, a2), (a2, a3), (a3, a4)):
        flecha(d, (1050, a[3]), (1050, b[1]), VERDE)
    d.text((742, 1050), "springdoc publica /v3/api-docs y /swagger-ui.html; pruebas_api.py comprueba", font=F_MIN, fill=GRIS_MEDIO)
    d.text((742, 1072), "que todo lo implementado esta en el contrato y que no queda nada pendiente.", font=F_MIN, fill=GRIS_MEDIO)

    # --- base
    capa(d, 1540, 100, 320, 760, "PostgreSQL 16", "Mismo modelo; alerta con atencion", AMBAR)
    caja(d, 1565, 180, 270, "Tablas (7)",
         ["zona", "variable", "sensor", "umbral", "lectura", "alerta  + atendida_en,", "           atendida_por (P05)", "anotacion"], AMBAR)
    caja(d, 1565, 470, 270, "Reglas en la base",
         ["PK, FK, UNIQUE", "CHECK de rangos", "CHECK origen, nivel, autor_rol", "CHECK atencion coherente (P05)"], AMBAR)
    d.text((1565, 660), "sql/01_schema.sql", font=F_MONO, fill=GRIS_MEDIO)
    d.text((1565, 684), "sql/02_seed.sql", font=F_MONO, fill=GRIS_MEDIO)
    d.text((1565, 708), "sql/04_p05_atencion_alerta.sql", font=F_MONO, fill=GRIS_MEDIO)
    d.text((1565, 732), "   (migracion, no destructiva)", font=F_MIN, fill=GRIS_MEDIO)
    d.text((1565, 770), "Datos ficticios de laboratorio.", font=F_MIN, fill=GRIS_MEDIO)
    d.rectangle([1540, 860, 1860, 920], fill=GRIS_CLARO, outline=AMBAR, width=3)
    d.text((1556, 880), "puerto 5436 (contenedor)", font=F_MIN, fill=GRIS_MEDIO)

    # --- conectores
    y = 600
    flecha(d, (560, y), (700, y), GRIS, 3, doble=True)
    etiqueta(d, 572, y - 96, ["HTTP + JSON", "/api/**", "Bearer token"], GRIS, BLANCO, F_MINB, GRIS_MEDIO)
    y2 = 890
    flecha(d, (1400, y2), (1540, y2), GRIS, 3, doble=True)
    etiqueta(d, 1412, y2 - 74, ["JDBC", "SQL"], GRIS, BLANCO, F_MINB, GRIS_MEDIO)

    # --- contrato
    d.rectangle([40, 1030, 560, 1140], fill=VERDE_CLARO, outline=VERDE, width=2)
    d.text((56, 1042), "Contrato: docs/p04/openapi.yaml 0.5.0", font=F_CAJA, fill=VERDE)
    d.text((56, 1070), "13 operaciones, 19 esquemas; escrito antes que el codigo.", font=F_MIN, fill=GRIS)
    d.text((56, 1092), "modelos.ts y los DTO lo siguen; pruebas_api.py valida", font=F_MIN, fill=GRIS)
    d.text((56, 1114), "cada respuesta contra su esquema.", font=F_MIN, fill=GRIS)
    img.save(OUT / "01_componentes.png")


# ------------------------------------------------------------------ 02 secuencia del cambio de estado
def secuencia_atencion():
    img, d = lienzo(1900, 1260, "Cambio de estado: el responsable atiende una alerta (PATCH /api/alertas/{id})",
                    "Linea continua: llamada. Linea punteada: respuesta. En rojo, las salidas de error que corta cada paso.")
    nombres = ["Responsable", "Cliente Angular", "TokenFilter", "AlertaController", "AlertaService", "AlertaRepository", "PostgreSQL"]
    detalle = ["(navegador)", "AlertasComponent + ApiService", "", "", "", "", ""]
    xs = [110, 380, 680, 930, 1200, 1480, 1740]
    for x, n, s in zip(xs, nombres, detalle):
        w = max(d.textlength(n, font=F_CAJA), d.textlength(s, font=F_MIN)) + 28
        d.rectangle([x - w / 2, 100, x + w / 2, 156], fill=VERDE, outline=VERDE)
        d.text((x - d.textlength(n, font=F_CAJA) / 2, 106 if s else 117), n, font=F_CAJA, fill=BLANCO)
        if s:
            d.text((x - d.textlength(s, font=F_MIN) / 2, 132), s, font=F_MIN, fill=BLANCO)
        for yy in range(156, 1200, 14):
            d.line([(x, yy), (x, yy + 7)], fill=GRIS_MEDIO, width=1)

    def rotulo(x, y, texto, f, color):
        d.rectangle([x - 3, y, x + d.textlength(texto, font=f) + 3, y + 19], fill=BLANCO)
        d.text((x, y), texto, font=f, fill=color)

    def msj(i, j, y, texto, color=GRIS, respuesta=False, sub=None):
        flecha(d, (xs[i], y), (xs[j], y), color, 2, punteada=respuesta)
        izq = min(xs[i], xs[j]) + 12
        rotulo(izq, y - 25, texto, F_MINB if not respuesta else F_MIN, color)
        if sub:
            rotulo(izq, y + 6, sub, F_MIN, GRIS_MEDIO)

    def corte(i, y, texto):
        flecha(d, (xs[i], y), (xs[1], y), ROJO, 2, punteada=True)
        rotulo(xs[1] + 12, y - 24, texto, F_MIN, ROJO)

    y = 210
    msj(0, 1, y, "1. pulsa \"Marcar atendida\" en una alerta pendiente")
    y += 70
    msj(1, 2, y, "2. PATCH /api/alertas/7", sub="Authorization: Bearer <token>   {\"atendida\": true}")
    y += 70
    corte(2, y, "401 NO_AUTENTICADO: sin token, firma alterada o caducado")
    y += 60
    msj(2, 3, y, "3. token valido: usuario y rol")
    y += 60
    msj(3, 4, y, "4. exigir(ATENDER_ALERTA); cambiarAtencion(7, true, rol)")
    y += 60
    corte(3, y, "403 ROL_SIN_PERMISO: OBSERVADOR y COORDINACION no atienden")
    y += 60
    corte(3, y, "400 VALIDACION: falta atendida o no es booleano")
    y += 60
    msj(4, 5, y, "5. porId(7)")
    msj(5, 6, y + 44, "SELECT alerta + lectura + sensor + zona")
    y += 110
    corte(4, y, "404 NO_ENCONTRADO (no existe)  /  409 CONFLICTO (ya estaba atendida)")
    y += 60
    d.rectangle([xs[4] - 60, y - 20, xs[6] + 90, y + 120], outline=VERDE, width=2)
    rotulo(xs[4] - 50, y - 14, "transaccion", F_MINB, VERDE)
    msj(4, 5, y + 40, "6. marcar(7, true, RESPONSABLE)")
    msj(5, 6, y + 84, "UPDATE alerta SET atendida, atendida_en, atendida_por")
    y += 180
    msj(4, 1, y, "7. 200 OK   cuerpo: Alerta con atendida, atendidaEn y atendidaPor", VERDE, respuesta=True)
    y += 60
    msj(1, 0, y, "8. \"Alerta #7 marcada como atendida\"; la fila cambia de estado", VERDE, respuesta=True)
    y += 60
    msj(1, 2, y, "9. GET /api/alertas?pagina=0", sub="recarga la pagina actual con el estado nuevo")
    d.text((40, 1222), "Reabrir es el mismo camino con {\"atendida\": false}: deja atendida_en y atendida_por en NULL. "
                       "Si PostgreSQL no responde, la respuesta es 503 BASE_NO_DISPONIBLE.", font=F_MIN, fill=GRIS_MEDIO)
    img.save(OUT / "02_secuencia_atencion.png")


# ------------------------------------------------------------------ 03 estados de la alerta
def estados_alerta():
    img, d = lienzo(1400, 620, "Estados de una alerta y quien los cambia",
                    "Una alerta nace cuando una lectura sale del umbral. Solo cambia de estado por la API, con el rol RESPONSABLE.")
    # nacimiento
    d.ellipse([70, 290, 100, 320], fill=GRIS)
    flecha(d, (100, 305), (250, 305), GRIS, 3)
    d.text((60, 160), "Nace con POST /api/lecturas (OBSERVADOR)", font=F_MINB, fill=GRIS)
    d.text((60, 182), "cuando el valor sale del umbral operativo", font=F_MIN, fill=GRIS_MEDIO)
    # pendiente
    d.rounded_rectangle([250, 230, 560, 380], radius=24, fill=(232, 240, 251), outline=AZUL, width=3)
    d.text((290, 255), "PENDIENTE", font=F_CAJA, fill=AZUL)
    for i, l in enumerate(["atendida = false", "atendida_en = NULL", "atendida_por = NULL"]):
        d.text((290, 290 + 24 * i), l, font=F_MONO, fill=GRIS)
    # atendida
    d.rounded_rectangle([840, 230, 1180, 380], radius=24, fill=VERDE_CLARO, outline=VERDE, width=3)
    d.text((880, 255), "ATENDIDA", font=F_CAJA, fill=VERDE)
    for i, l in enumerate(["atendida = true", "atendida_en = now()", "atendida_por = RESPONSABLE"]):
        d.text((880, 290 + 24 * i), l, font=F_MONO, fill=GRIS)
    # transiciones
    flecha(d, (560, 275), (840, 275), VERDE, 3)
    d.text((580, 212), "PATCH {atendida: true}  ->  200", font=F_MINB, fill=VERDE)
    d.text((580, 234), "solo RESPONSABLE", font=F_MIN, fill=GRIS_MEDIO)
    d.text((580, 254), "(permiso ATENDER_ALERTA)", font=F_MIN, fill=GRIS_MEDIO)
    flecha(d, (840, 345), (560, 345), AMBAR, 3)
    d.text((580, 352), "PATCH {atendida: false}  ->  200  (reabrir)", font=F_MINB, fill=AMBAR)
    # auto-transiciones rechazadas
    d.arc([330, 380, 480, 470], 0, 180, fill=ROJO, width=2)
    d.text((300, 475), "PATCH {atendida: false}  ->  409 CONFLICTO", font=F_MIN, fill=ROJO)
    d.text((300, 497), "\"La alerta N ya estaba pendiente.\"", font=F_MIN, fill=ROJO)
    d.arc([930, 380, 1080, 470], 0, 180, fill=ROJO, width=2)
    d.text((880, 475), "PATCH {atendida: true}  ->  409 CONFLICTO", font=F_MIN, fill=ROJO)
    d.text((880, 497), "\"La alerta N ya estaba atendida.\"", font=F_MIN, fill=ROJO)
    # otros errores
    for i, l in enumerate(["Desde cualquier estado: 401 sin token, 403 con OBSERVADOR o COORDINACION,",
                           "400 si el cuerpo no trae un booleano, 404 si la alerta no existe, 503 si PostgreSQL no responde.",
                           "La restriccion ck_alerta_atencion impide en la base un estado a medias (atendida sin instante o sin rol)."]):
        d.text((60, 540 + 22 * i), l, font=F_MIN, fill=GRIS_MEDIO)
    img.save(OUT / "03_estados_alerta.png")


# ------------------------------------------------------------------ 04 despliegue
def despliegue():
    img, d = lienzo(1900, 1000, "Despliegue local de P05: procesos, puertos y configuracion",
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
    caja(d, 1540, 420, 290, "Configuracion de la base", ["docker/docker-compose.yml", "sql/01_schema.sql (limpia)", "sql/02_seed.sql", "sql/04_p05_... (existente)"], AMBAR, BLANCO)
    d.text((70, 430), "Base existente de P04:", font=F_MINB, fill=GRIS)
    for i, l in enumerate(["sql/04_p05_atencion_alerta.sql agrega", "las dos columnas de atencion sin", "borrar nada; se puede correr dos", "veces. verify-module.sh M05 lo", "aplica antes de arrancar la API."]):
        d.text((70, 456 + 22 * i), l, font=F_MIN, fill=GRIS)
    d.text((70, 640), "P02 y P03 (WAR en Tomcat 9, puerto 8080) siguen en el repositorio y no comparten proceso con P04/P05; todos usan la misma base.",
           font=F_MIN, fill=GRIS_MEDIO)
    d.text((70, 664), "En application.properties no hay credenciales: solo referencias ${...} a las variables.", font=F_MIN, fill=GRIS_MEDIO)

    d.rectangle([40, 770, 1860, 960], fill=VERDE_CLARO, outline=VERDE, width=2)
    d.text((60, 782), "Construccion y verificacion", font=F_CAJA, fill=VERDE)
    pasos = [
        ("mvn -f api-spring/pom.xml clean package", "api-spring/target/api-spring.jar con sus pruebas JUnit"),
        ("cd frontend-angular && npm ci && npx ng build", "frontend-angular/dist/frontend-angular (estaticos)"),
        ("./scripts/verify-module.sh M05", "compila, valida el contrato, migra, levanta la API y el cliente, prueba y apaga"),
        ("./scripts/cleanup.sh", "retira los datos de prueba y las carpetas generadas"),
    ]
    for i, (orden, efecto) in enumerate(pasos):
        d.text((60, 818 + 32 * i), orden, font=F_MONO, fill=GRIS)
        d.text((560, 818 + 32 * i), "->  " + efecto, font=F_MONO, fill=GRIS)
    img.save(OUT / "04_despliegue.png")


if __name__ == "__main__":
    componentes()
    secuencia_atencion()
    estados_alerta()
    despliegue()
    print("Diagramas en", OUT.relative_to(OUT.parent.parent.parent))
