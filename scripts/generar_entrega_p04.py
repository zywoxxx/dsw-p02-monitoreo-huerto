"""
generar_entrega_p04.py - Arma los documentos de entrega de P04:
  docs/entrega/P04_EQUIPO_01.docx          (equipo)
  docs/entrega/P04_PACHECO_ALEJANDRO.docx  (justificacion individual)
con los diagramas de docs/p04/diagramas/ y la evidencia de docs/p04/evidencia/.
Requiere python-docx y Pillow. Uso: python scripts/generar_entrega_p04.py
"""
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
DIAG = ROOT / "docs" / "p04" / "diagramas"
IMG = ROOT / "docs" / "p04" / "evidencia" / "img"
TXT = ROOT / "docs" / "p04" / "evidencia" / "txt"
ER = ROOT / "docs" / "evidencia" / "img" / "00_modelo_er.png"
ENTREGA = ROOT / "docs" / "entrega"
ENTREGA.mkdir(parents=True, exist_ok=True)
RECORTES = ENTREGA / ".recortes"

VERDE = RGBColor(0x2F, 0x6B, 0x3A)
GRIS = RGBColor(0x55, 0x55, 0x55)
FECHA = "Orizaba, Ver., 9 de octubre de 2026"


class Doc:
    """Documento con el formato de las entregas anteriores (P02, P03)."""

    def __init__(self, cabecera):
        self.doc = Document()
        self.nfig = 0
        d = self.doc
        st = d.styles["Normal"]
        st.font.name = "Calibri"
        st.font.size = Pt(11)
        st.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
        st.paragraph_format.space_after = Pt(6)
        st.paragraph_format.line_spacing = 1.15
        for nivel, tam in ((1, 16), (2, 13), (3, 11.5)):
            h_ = d.styles[f"Heading {nivel}"]
            h_.font.name = "Calibri"
            h_.font.size = Pt(tam)
            h_.font.bold = True
            h_.font.color.rgb = VERDE
            h_.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
            h_.paragraph_format.space_before = Pt(14 if nivel == 1 else 10)
            h_.paragraph_format.space_after = Pt(4)
        sec = d.sections[0]
        self._vertical(sec)
        hp = sec.header.paragraphs[0]
        hp.text = cabecera
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        for r in hp.runs:
            r.font.size = Pt(8.5)
            r.font.color.rgb = GRIS
        fp = sec.footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = fp.add_run()
        for tag, txt in (("begin", None), (None, "PAGE"), ("end", None)):
            if tag:
                el = OxmlElement("w:fldChar")
                el.set(qn("w:fldCharType"), tag)
                run._r.append(el)
            else:
                it = OxmlElement("w:instrText")
                it.set(qn("xml:space"), "preserve")
                it.text = txt
                run._r.append(it)
        run.font.size = Pt(9)
        run.font.color.rgb = GRIS

    @staticmethod
    def _vertical(sec):
        sec.orientation = WD_ORIENT.PORTRAIT
        sec.page_width, sec.page_height = Cm(21.59), Cm(27.94)
        sec.left_margin = sec.right_margin = Cm(2.5)
        sec.top_margin = sec.bottom_margin = Cm(2.2)

    @staticmethod
    def _horizontal(sec):
        sec.orientation = WD_ORIENT.LANDSCAPE
        sec.page_width, sec.page_height = Cm(27.94), Cm(21.59)
        sec.left_margin = sec.right_margin = Cm(1.8)
        sec.top_margin = sec.bottom_margin = Cm(1.8)

    # ---- texto
    def p(self, texto, negrita=False, cursiva=False, tam=None, alinear=None, color=None, despues=None):
        par = self.doc.add_paragraph()
        r = par.add_run(texto)
        r.bold = negrita
        r.italic = cursiva
        if tam:
            r.font.size = Pt(tam)
        if color:
            r.font.color.rgb = color
        if alinear:
            par.alignment = alinear
        if despues is not None:
            par.paragraph_format.space_after = Pt(despues)
        return par

    def h(self, texto, nivel=1):
        return self.doc.add_heading(texto, level=nivel)

    def salto(self):
        self.doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    def vinetas(self, items):
        for it in items:
            par = self.doc.add_paragraph(style="List Bullet")
            par.add_run(it)
            par.paragraph_format.space_after = Pt(2)

    # ---- tablas
    @staticmethod
    def sombrear(celda, hexcolor):
        tcPr = celda._tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), hexcolor)
        tcPr.append(shd)

    def tabla(self, encabezados, filas, anchos=None, tam=9.5):
        t = self.doc.add_table(rows=1, cols=len(encabezados))
        t.style = "Table Grid"
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        for i, e in enumerate(encabezados):
            c = t.rows[0].cells[i]
            c.text = ""
            r = c.paragraphs[0].add_run(e)
            r.bold = True
            r.font.size = Pt(tam)
            self.sombrear(c, "E6F2E8")
        for fila in filas:
            cells = t.add_row().cells
            for i, v in enumerate(fila):
                cells[i].text = ""
                r = cells[i].paragraphs[0].add_run(str(v))
                r.font.size = Pt(tam)
        for j, fila in enumerate(t.rows):
            trPr = fila._tr.get_or_add_trPr()
            trPr.append(OxmlElement("w:cantSplit"))
            if j == 0:
                trPr.append(OxmlElement("w:tblHeader"))
        if anchos:
            for fila in t.rows:
                for i, a in enumerate(anchos):
                    fila.cells[i].width = Cm(a)
        self.doc.add_paragraph().paragraph_format.space_after = Pt(2)

    def codigo(self, texto, tam=8.5):
        lineas = texto.rstrip("\n").split("\n")
        t = self.doc.add_table(rows=1, cols=1)
        t.style = "Table Grid"
        c = t.rows[0].cells[0]
        self.sombrear(c, "F4F4F2")
        c.text = ""
        par = c.paragraphs[0]
        for i, ln in enumerate(lineas):
            r = par.add_run(ln)
            r.font.name = "Consolas"
            r._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")
            r.font.size = Pt(tam)
            if i < len(lineas) - 1:
                r.add_break()
        par.paragraph_format.space_after = Pt(0)
        self.doc.add_paragraph().paragraph_format.space_after = Pt(2)

    # ---- figuras
    @staticmethod
    def recortar(ruta):
        """Quita el fondo vacio de abajo de una captura de pagina completa."""
        im = Image.open(ruta).convert("RGB")
        w, hh = im.size
        px = im.load()
        fondo = px[w - 1, hh - 1]
        y = hh - 1
        while y > 40:
            if not all(abs(px[x, y][c] - fondo[c]) < 8 for x in range(0, w, 6) for c in range(3)):
                break
            y -= 1
        y = min(hh, y + 28)
        if y >= hh - 5:
            return ruta
        RECORTES.mkdir(exist_ok=True)
        salida = RECORTES / ruta.name
        im.crop((0, 0, w, y)).save(salida)
        return salida

    def _pie(self, pie):
        self.nfig += 1
        c = self.doc.add_paragraph()
        c.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = c.add_run(f"Figura {self.nfig}. {pie}")
        r.italic = True
        r.font.size = Pt(9.5)
        r.font.color.rgb = GRIS
        c.paragraph_format.space_after = Pt(10)

    def figura(self, ruta, pie, ancho_cm=16.5, recortar=True):
        if not ruta.exists():
            self.p(f"[falta la imagen {ruta.name}]", cursiva=True, color=GRIS)
            return
        if recortar:
            ruta = self.recortar(ruta)
        par = self.doc.add_paragraph()
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        par.paragraph_format.space_after = Pt(2)
        par.add_run().add_picture(str(ruta), width=Cm(ancho_cm))
        self._pie(pie)

    def figura_apaisada(self, ruta, pie, alto_max=15.8, ancho_max=24.2):
        """Una pagina horizontal para un diagrama ancho; despues vuelve a vertical."""
        sh = self.doc.add_section(WD_SECTION.NEW_PAGE)
        self._horizontal(sh)
        im = Image.open(ruta)
        w, hh = im.size
        ancho = min(ancho_max, alto_max * w / hh)
        par = self.doc.add_paragraph()
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        par.paragraph_format.space_after = Pt(2)
        par.add_run().add_picture(str(ruta), width=Cm(ancho))
        self._pie(pie)
        sv = self.doc.add_section(WD_SECTION.NEW_PAGE)
        self._vertical(sv)

    def leer(self, nombre, desde=None, hasta=None, filtro=None, max_lineas=None):
        ruta = TXT / nombre
        if not ruta.exists():
            return f"[no se encontro {nombre}]"
        lineas = ruta.read_text(encoding="utf-8", errors="replace").splitlines()
        lineas = lineas[desde:hasta]
        if filtro:
            lineas = [l for l in lineas if filtro(l)]
        if max_lineas:
            lineas = lineas[:max_lineas]
        return "\n".join(l.rstrip() for l in lineas)

    def portada(self, titulo, subtitulo, autores, repositorio=True):
        for _ in range(5):
            self.doc.add_paragraph()
        self.p("Universidad Veracruzana", negrita=True, tam=14, alinear=WD_ALIGN_PARAGRAPH.CENTER, color=VERDE, despues=0)
        self.p("Desarrollo de Sistemas Web (DSW-19559)", tam=12, alinear=WD_ALIGN_PARAGRAPH.CENTER, despues=30)
        self.p(titulo, negrita=True, tam=20, alinear=WD_ALIGN_PARAGRAPH.CENTER, despues=6)
        self.p(subtitulo, tam=14, alinear=WD_ALIGN_PARAGRAPH.CENTER, despues=0)
        self.p("Monitoreo de huerto o ambiente", tam=14, cursiva=True, alinear=WD_ALIGN_PARAGRAPH.CENTER, despues=40)
        self.p("Equipo DSW-E01", negrita=True, tam=13, alinear=WD_ALIGN_PARAGRAPH.CENTER, despues=4)
        for nombre in autores:
            self.p(nombre, tam=12, alinear=WD_ALIGN_PARAGRAPH.CENTER, despues=0)
        for _ in range(3):
            self.doc.add_paragraph()
        self.p("Facilitador: Dr. Gabriel Rodríguez Vásquez", tam=11, alinear=WD_ALIGN_PARAGRAPH.CENTER, despues=0)
        if repositorio:
            self.p("Repositorio: github.com/zywoxxx/dsw-p02-monitoreo-huerto", tam=11, alinear=WD_ALIGN_PARAGRAPH.CENTER, despues=0)
        self.p(FECHA, tam=11, alinear=WD_ALIGN_PARAGRAPH.CENTER)
        self.salto()

    def guardar(self, ruta):
        self.doc.save(ruta)
        print("documento generado en", ruta)


# =====================================================================
#  Documento del equipo
# =====================================================================
def equipo():
    d = Doc("DSW-19559 · P04 · Equipo DSW-E01 · PR09 Monitoreo de huerto o ambiente")
    d.portada("P04. Arquitectura Web 3.0 con Angular, Spring Boot Java 11 y PostgreSQL",
              "Tercer incremento del proyecto PR09",
              ("Alejandro Pacheco Luna", "Juan Pablo Kuri Ricardez", "Ariadna Trejo Álvarez", "Pedro García Padilla"))

    d.h("Contenido")
    for linea in ("1. Qué entregamos", "2. De dónde partimos y qué conservamos", "3. Componentes y responsabilidades",
                  "4. El flujo principal de punta a punta", "5. Por qué Angular y Spring Boot: decisiones y alternativas",
                  "6. Modelo de datos en PostgreSQL", "7. Endpoints y contratos", "8. Seguridad básica",
                  "9. Despliegue y configuración", "10. La estructura compila y corre", "11. Trazabilidad RF → componente",
                  "12. Pruebas y evidencia", "13. Problemas que tuvimos", "14. Relación con la rúbrica R04",
                  "15. Aportación individual", "16. Limitaciones y pendientes", "Anexo. Comandos"):
        d.p(linea, despues=1)
    d.salto()

    # 1
    d.h("1. Qué entregamos")
    d.p("Este documento acompaña al repositorio del equipo y describe el tercer incremento del PR09. En P02 el flujo "
        "principal corría con JSP y Servlets; en P03 lo pasamos a JSF con PrimeFaces. En P04 ya no se trata de cambiar "
        "cómo se pintan las pantallas, sino de separar la aplicación en dos piezas que se hablan por HTTP con JSON: un "
        "cliente Angular que corre en el navegador y una API REST hecha con Spring Boot sobre Java 11. La base de datos "
        "PostgreSQL es la misma de los dos incrementos anteriores y no cambió ni una columna.")
    d.p("La consigna pedía diseñar la arquitectura, documentar componentes, contratos, entidades, seguridad y despliegue, "
        "y entregar una estructura inicial compilable con trazabilidad RF-componente. Entregamos eso y, además, el flujo "
        "principal funcionando de punta a punta, porque era la única forma de comprobar que el contrato que escribimos "
        "se puede cumplir. Lo que no implementamos está marcado como pendiente, no escondido.")
    d.tabla(["Elemento", "Dónde está"], [
        ("Documento de arquitectura con diagramas y decisiones justificadas", "docs/p04/arquitectura.md y docs/p04/diagramas/"),
        ("Modelo PostgreSQL y su relación con los recursos de la API", "docs/p04/modelo-datos.md, sql/01_schema.sql"),
        ("Contrato OpenAPI 3.0.3 y catálogo de endpoints", "docs/p04/openapi.yaml, docs/p04/endpoints.md"),
        ("Esqueleto del backend Spring Boot (Java 11)", "api-spring/"),
        ("Esqueleto del frontend Angular 16", "frontend-angular/"),
        ("Trazabilidad RF → componente → prueba", "docs/p04/trazabilidad-rf.md"),
        ("Verificación, estados y limitaciones", "docs/p04/verificacion.md"),
        ("Evidencia (salidas de comandos y capturas) e índice frente a R04", "docs/p04/evidencia/"),
        ("Registro individual de aportación y decisiones", "docs/p04/individual/ (entrega aparte: P04_APELLIDO_NOMBRE)"),
        ("Bitácora con los fallos que encontramos y cómo los corregimos", "docs/bitacora.md, entradas 25 a 33"),
    ], anchos=[8.5, 8])

    # 2
    d.h("2. De dónde partimos y qué conservamos")
    d.p("El commit de partida es bf78beb, el cierre de P03. De ahí tomamos sin cambios la base de datos (siete tablas), "
        "los datos ficticios, los tres roles con sus permisos y las reglas del huerto: sensor existente y activo, valor "
        "numérico con máximo dos decimales y sin redondeo, rechazo de lo que sale del rango físico, alerta BAJA o ALTA "
        "cuando el valor sale del umbral operativo con los límites incluidos, y lectura más alerta en una sola transacción. "
        "El SQL de los repositorios también viene de P02; solo cambió la forma de ejecutarlo.")
    d.p("Las aplicaciones de P02 y P03 siguen en el repositorio y siguen funcionando contra la misma base. No las tocamos. "
        "La API usa el puerto 8081 justamente para no chocar con el Tomcat del 8080.")
    d.p("No agregamos funciones que el acta no tenga. Zonas, alertas y anotaciones existen en la base y en el contrato, "
        "pero en este incremento no tienen código; el simulador IoT corresponde a Web 4.0.")

    # 3
    d.h("3. Componentes y responsabilidades")
    d.p("La figura 1 muestra las tres capas y lo que hay dentro de cada una. Lo que está en verde ya corre; la caja gris "
        "de abajo lista lo que solo existe en el contrato.")
    d.figura_apaisada(DIAG / "01_componentes.png", "Diagrama de componentes: cliente Angular, API Spring Boot y PostgreSQL.")
    d.h("3.1 Cliente Angular", 2)
    d.tabla(["Componente", "Qué hace", "Qué no hace"], [
        ("AppComponent", "Cabecera con usuario y rol, botón de salir, navegación", "—"),
        ("AccesoComponent (/acceso)", "Pide usuario y contraseña, llama a POST /api/auth/login y abre la sesión", "No compara contraseñas; no conoce la lista de usuarios"),
        ("LecturasComponent (/lecturas)", "Formulario de captura, historial paginado con filtro por procedencia, mensajes de éxito, alerta y error", "No decide si un valor es válido: envía lo capturado y muestra lo que responde la API"),
        ("sesionGuard", "Impide entrar a /lecturas sin sesión", "No es la seguridad real; la API responde 401 de todos modos"),
        ("ApiService", "Único lugar que conoce las rutas de la API", "—"),
        ("SesionService", "Guarda token, usuario, rol y caducidad en sessionStorage; descarta sesiones vencidas", "No guarda la contraseña"),
        ("TokenInterceptor", "Agrega Authorization: Bearer a cada llamada; ante un 401 cierra la sesión y regresa al acceso", "—"),
    ], anchos=[3.8, 7.2, 5.5], tam=9)
    d.h("3.2 API Spring Boot", 2)
    d.tabla(["Componente", "Qué hace"], [
        ("WebConfig", "CORS para /api/** con un solo origen permitido; metadatos de OpenAPI"),
        ("TokenFilter", "Exige token válido en /api/**, salvo /api/health, /api/auth/login y las peticiones OPTIONS; responde 401 con el cuerpo de error del contrato"),
        ("AuthController", "POST /api/auth/login: valida que vengan los dos campos (400), comprueba credenciales (401) y emite el token"),
        ("HealthController", "GET /api/health: 200 si llega a PostgreSQL, 503 si no"),
        ("SensorController, SensorRepository", "GET /api/sensores: catálogo con zona, variable, unidad, rango físico y umbral"),
        ("LecturaController", "GET y POST /api/lecturas, GET /api/lecturas/{id}; exige el permiso antes de llamar al servicio"),
        ("LecturaService", "Orquesta el registro: forma, existencia y estado del sensor, rango físico, inserción de lectura y alerta en una transacción"),
        ("ReglasLectura", "Las reglas puras, sin Spring ni base: obligatorios, dos decimales, rango físico, nivel y texto de la alerta"),
        ("Permisos, UsuarioAutenticado", "Tabla rol → permisos tomada del acta; exigir() lanza 403"),
        ("TokenService, CredencialesService", "Emite y valida el token (JWT HS256); compara la contraseña contra el hash PBKDF2 de usuarios.properties"),
        ("LecturaRepository", "SQL parametrizado con NamedParameterJdbcTemplate; no tiene reglas"),
        ("ApiExceptionHandler", "Traduce cualquier excepción al cuerpo Error del contrato; nunca manda trazas"),
    ], anchos=[5, 11.5], tam=9)
    d.h("3.3 PostgreSQL", 2)
    d.p("Guarda los datos y hace cumplir lo que no debe depender del código: claves, unicidad, rangos (CHECK), valores "
        "permitidos de origen, nivel y autor_rol. Como tres aplicaciones escriben en las mismas tablas, estas restricciones "
        "son las que garantizan que un dato quede bien aunque entre por otro camino.")

    # 4
    d.h("4. El flujo principal de punta a punta")
    d.p("El observador elige un sensor, escribe un valor y una observación, y el sistema guarda la lectura y, si hace "
        "falta, la alerta. La figura 2 sigue esa petición desde el navegador hasta PostgreSQL y marca en rojo dónde se "
        "corta cada caso inválido.")
    d.figura_apaisada(DIAG / "02_secuencia.png", "Secuencia de POST /api/lecturas con sus salidas de error.")
    d.p("El orden de las comprobaciones no es casual: primero identidad (401), luego permiso (403), después la forma de "
        "los datos (400), luego lo que requiere consultar la base (404, 409, 422) y al final la escritura. Así una petición "
        "sin permiso no llega a tocar PostgreSQL y una mal formada no abre una transacción.")

    # 5
    d.h("5. Por qué Angular y Spring Boot: decisiones y alternativas")
    d.p("Angular y Spring Boot con Java 11 los fija la experiencia educativa, así que la pregunta real no era \"cuál "
        "framework\" sino cómo usarlos. Estas son las decisiones donde sí había alternativa, qué revisamos y qué cuesta "
        "lo que elegimos.")
    d.tabla(["#", "Decisión", "Alternativas que revisamos", "Por qué nos quedamos con esta"], [
        ("D1", "Angular 16.2.12 con módulos (NgModule)", "Componentes standalone; React o Vue; seguir con JSF",
         "Los módulos son lo que genera el CLI 16 por omisión y lo que usa el material del curso; standalone funciona pero nos obligaba a aprender dos cosas a la vez. JSF mezcla vista y servidor, que es justo lo que P04 separa."),
        ("D2", "Spring Boot 2.7.18", "Spring Boot 3; servlets con JSON a mano; JAX-RS en el Tomcat de P03",
         "Spring Boot 3 exige Java 17 y jakarta; el curso fija Java 11 y 2.7.18 es la última versión de la línea que lo soporta. Con servlets habríamos escrito a mano lo que Spring MVC ya resuelve (JSON, errores, pruebas con MockMvc)."),
        ("D3", "Spring JDBC (NamedParameterJdbcTemplate)", "Spring Data JPA con Hibernate; JDBC puro como en P02 y P03",
         "El SQL ya estaba escrito y probado; con Spring JDBC lo reutilizamos y vemos qué consulta se ejecuta. JPA pedía mapear siete entidades y cuidar que Hibernate no tocara un esquema que comparten tres aplicaciones. Frente al JDBC puro ganamos el pool y @Transactional. Costo: los RowMapper se escriben a mano."),
        ("D4", "Token firmado (JWT HS256) sin estado en el servidor", "Sesión con cookie como en P03; Spring Security con OAuth2; Basic en cada petición",
         "Con cliente y API en orígenes distintos, la cookie obliga a resolver SameSite y CSRF; el token en la cabecera evita ambos. Spring Security es lo correcto en producción, pero para tres usuarios fijos agrega una cadena de filtros que aquí no hace falta; preferimos un filtro de 64 líneas que se lee completo. Costo: un token no se puede revocar antes de sus 30 minutos."),
        ("D5", "Contrato primero: openapi.yaml a mano; springdoc como comprobación", "Generar el contrato desde el código; generar el código desde el contrato",
         "Escribirlo antes nos obligó a decidir códigos de estado y cuerpos de error sin mirar la implementación, y dejó definidos los recursos que todavía no programamos. La prueba 30 compara lo que publica el código contra el contrato. Costo: dos documentos que mantener alineados; por eso la comparación está automatizada."),
        ("D6", "Un repositorio, dos carpetas", "Dos repositorios; empaquetar Angular dentro del jar",
         "Somos cuatro y la entrega es una; un repositorio mantiene juntos contrato, cliente, API y evidencia. Meter Angular en el jar simplifica el despliegue pero esconde la separación que la práctica pide mostrar."),
        ("D7", "422 para valor fuera del rango físico y 400 para datos mal formados", "Responder 400 a todo, como en P02",
         "El cliente necesita distinguir \"lo que enviaste no se puede leer\" de \"se leyó, pero el huerto no puede tener 150 °C\". Son causas distintas y el mensaje también."),
        ("D8", "Proxy de desarrollo (/api → 8081) y CORS de un solo origen", "Llamar directo al 8081 desde el navegador; allowedOrigins(\"*\")",
         "Con el proxy el navegador habla con un solo origen y el cliente no lleva la URL de la API escrita. CORS queda configurado y probado para cuando se sirvan por separado. El comodín dejaría que cualquier página llamara a la API."),
        ("D9", "El valor viaja como número JSON y la API lo lee como BigDecimal", "Enviarlo como texto; usar double",
         "double convierte 24.555 en una aproximación y la regla \"máximo dos decimales, sin redondear\" deja de ser comprobable. Con BigDecimal la escala es exacta."),
    ], anchos=[0.9, 3.6, 4, 8], tam=8.5)
    d.p("Cada integrante desarrolla una de estas decisiones con más detalle en su justificación individual.")

    # 6
    d.h("6. Modelo de datos en PostgreSQL")
    d.p("El modelo es el de P02 y P03: siete tablas creadas por sql/01_schema.sql. En P04 no se agregó, quitó ni "
        "modificó ninguna columna. Lo nuevo es cómo se convierte cada tabla en un recurso de la API.")
    d.figura(ER, "Modelo entidad-relación (sin cambios desde P02).", ancho_cm=16.5, recortar=False)
    d.tabla(["Tabla", "Columnas", "Restricciones"], [
        ("zona", "id, nombre, cultivo, ubicacion, creada_en", "PK; nombre único; ubicacion obligatoria"),
        ("variable", "id, clave, nombre, unidad, valor_minimo, valor_maximo", "PK; clave única; CHECK (valor_minimo < valor_maximo)"),
        ("sensor", "id, zona_id, variable_id, codigo, activo, instalado_en", "PK; FK a zona y variable; codigo único"),
        ("umbral", "id, sensor_id, minimo, maximo", "PK; FK única a sensor; CHECK (minimo < maximo)"),
        ("lectura", "id, sensor_id, valor, origen, observacion, registrado_en", "PK; FK a sensor; CHECK origen IN ('manual','simulado'); índice (sensor_id, registrado_en DESC)"),
        ("alerta", "id, lectura_id, nivel, mensaje, atendida, creada_en", "PK; FK única a lectura; CHECK nivel IN ('BAJA','ALTA')"),
        ("anotacion", "id, zona_id, lectura_id, autor_rol, texto, creada_en", "PK; FK a zona; FK opcional a lectura; CHECK autor_rol con los tres roles; texto mínimo 3"),
    ], anchos=[2.2, 6.3, 8], tam=9)
    d.h("6.1 De tabla a recurso", 2)
    d.p("La API no expone las tablas una por una. Un recurso junta lo que el cliente necesita en una sola respuesta, para "
        "que Angular no haga tres llamadas y cruce identificadores.")
    d.tabla(["Recurso del contrato", "Tablas", "Campo JSON ← columna"], [
        ("Sensor", "sensor + zona + variable + umbral (LEFT JOIN)", "codigo ← sensor.codigo; zona ← zona.nombre; variable, unidad ← variable; rangoFisicoMinimo/Maximo ← variable.valor_minimo/valor_maximo; umbralMinimo/Maximo ← umbral"),
        ("Lectura", "lectura + sensor + zona + variable + alerta (LEFT JOIN)", "valor, origen, observacion, registradoEn ← lectura; sensorCodigo, zona, variable, unidad ← joins; alerta{nivel, mensaje} ← alerta"),
        ("NuevaLectura (entrada)", "lectura", "sensorId → sensor_id; valor → valor; observacion → observacion. origen no se acepta: la API escribe manual; registrado_en lo pone PostgreSQL"),
        ("Zona, Alerta, Anotacion", "solo contrato", "directo más joins; autorRol sale del token"),
    ], anchos=[3.3, 5, 8.2], tam=9)
    d.p("Convenciones: columnas en snake_case, campos JSON en camelCase; NUMERIC(10,2) viaja como número con dos "
        "decimales y en Java es BigDecimal; TIMESTAMPTZ viaja en ISO-8601 UTC y el cliente lo muestra en hora local.")
    d.h("6.2 Dónde vive cada regla", 2)
    d.tabla(["Regla", "En la API", "En PostgreSQL"], [
        ("Sensor obligatorio y existente", "ReglasLectura, LecturaService (400, 404)", "FK lectura.sensor_id"),
        ("Sensor activo", "LecturaService (409)", "—"),
        ("Máximo dos decimales", "ReglasLectura (400)", "NUMERIC(10,2) redondearía; por eso se valida antes"),
        ("Dentro del rango físico", "ReglasLectura (422)", "el rango está en variable; la comparación la hace la API"),
        ("Alerta si sale del umbral, límites incluidos", "ReglasLectura.nivelAlerta", "CHECK nivel; una alerta por lectura (UNIQUE)"),
        ("Lectura y alerta juntas o ninguna", "@Transactional en LecturaService", "transacción"),
        ("Procedencia", "la API escribe manual", "CHECK origen"),
        ("Observación de hasta 200", "ReglasLectura (400)", "VARCHAR(200)"),
    ], anchos=[5, 5.5, 6], tam=9)

    # 7
    d.h("7. Endpoints y contratos")
    d.p("El contrato formal es docs/p04/openapi.yaml (OpenAPI 3.0.3, versión 0.4.0), validado con openapi-spec-validator. "
        "Aquí va el resumen; los ejemplos están copiados de las respuestas reales que quedaron en la evidencia.")
    d.tabla(["#", "Método y ruta", "Para qué", "Quién", "Éxito", "Errores", "Estado"], [
        ("1", "GET /api/health", "Saber si la API llega a PostgreSQL", "público", "200", "503", "implementado"),
        ("2", "POST /api/auth/login", "Cambiar credenciales por un token", "público", "200", "400, 401", "implementado"),
        ("3", "GET /api/sensores", "Catálogo con rango y umbral", "3 roles", "200", "400, 401", "implementado"),
        ("4", "GET /api/lecturas", "Historial paginado y filtrado", "3 roles", "200", "400, 401", "implementado"),
        ("5", "GET /api/lecturas/{id}", "Una lectura", "3 roles", "200", "401, 404", "implementado"),
        ("6", "POST /api/lecturas", "Registrar lectura manual", "OBSERVADOR", "201", "400, 401, 403, 404, 409, 422, 503", "implementado"),
        ("7", "GET /api/zonas", "Zonas", "3 roles", "200", "401", "solo contrato"),
        ("8", "GET /api/alertas", "Alertas", "3 roles", "200", "400, 401", "solo contrato"),
        ("9", "GET /api/anotaciones", "Anotaciones", "3 roles", "200", "401", "solo contrato"),
        ("10", "POST /api/anotaciones", "Registrar anotación", "3 roles", "201", "400, 401, 404", "solo contrato"),
    ], anchos=[0.7, 3.6, 4, 2, 1.2, 3.3, 1.9], tam=8.5)
    d.h("7.1 Reglas comunes", 2)
    d.p("Salvo las rutas 1 y 2, toda petición lleva Authorization: Bearer <token>. Sin token, con la firma alterada o "
        "caducado, la respuesta es 401 con la cabecera WWW-Authenticate. Todos los errores tienen la misma forma:")
    d.codigo('{\n  "codigo": "VALIDACION",\n  "mensaje": "La peticion tiene datos invalidos; no se guardo nada.",\n'
             '  "errores": [ { "campo": "valor", "mensaje": "El valor admite como maximo 2 decimales; no se redondea." } ],\n'
             '  "instante": "2026-09-29T12:27:52.5797281-06:00"\n}')
    d.tabla(["Estado", "codigo", "Cuándo"], [
        ("400", "VALIDACION", "JSON mal formado, campo obligatorio ausente, tipo incorrecto, más de dos decimales, texto demasiado largo, parámetro inválido"),
        ("401", "NO_AUTENTICADO", "Falta el token, no es válido o caducó; credenciales incorrectas"),
        ("403", "ROL_SIN_PERMISO", "El rol del token no puede hacer la operación"),
        ("404", "NO_ENCONTRADO", "El recurso pedido o referido no existe"),
        ("409", "CONFLICTO", "El recurso existe pero su estado no admite la operación (sensor inactivo)"),
        ("422", "REGLA_DE_NEGOCIO", "Datos bien formados que violan una regla del dominio (rango físico)"),
        ("503", "BASE_NO_DISPONIBLE", "PostgreSQL no responde"),
    ], anchos=[1.5, 3.5, 11.5], tam=9)
    d.h("7.2 POST /api/lecturas, el contrato que más importa", 2)
    d.tabla(["Campo de entrada", "Tipo", "Obligatorio", "Regla"], [
        ("sensorId", "entero", "sí", "debe existir y estar activo"),
        ("valor", "número", "sí", "máximo dos decimales; dentro del rango físico de la variable"),
        ("observacion", "texto", "no", "hasta 200 caracteres"),
    ], anchos=[3.5, 2, 2.5, 8.5], tam=9)
    d.p("No se aceptan origen ni registradoEn: la API escribe manual y PostgreSQL pone el instante. Entrada y respuesta "
        "reales de la prueba 12:")
    d.codigo('> POST /api/lecturas   Authorization: Bearer ...\n'
             '  {"sensorId": 2, "valor": 25.5, "observacion": "[prueba] P04 lectura valida"}\n'
             '< 201 Created   Location: /api/lecturas/62\n'
             '  {"id":62,"sensorId":2,"sensorCodigo":"SEN-A-TEMP-01","variable":"Temperatura ambiente","zona":"Cama A",\n'
             '   "valor":25.50,"unidad":"C","origen":"manual","observacion":"[prueba] P04 lectura valida",\n'
             '   "registradoEn":"2026-09-29T18:27:50.587461Z"}')
    d.p("Con 38 la respuesta también es 201, pero trae el objeto alerta con nivel ALTA y el mensaje \"Temperatura "
        "ambiente en Cama A: 38 C por encima del maximo 32.00 C.\". Los límites del umbral cuentan como dentro: 15 y 32 "
        "no generan alerta.")
    d.tabla(["Entrada", "Respuesta", "Cambio en la base"], [
        ("valor 25.5", "201 sin alerta", "+1 lectura"),
        ("valor 38 / 10", "201 con alerta ALTA / BAJA", "+1 lectura, +1 alerta"),
        ("valor 15 / 32", "201 sin alerta", "+1 lectura"),
        ("valor \"abc\", 24.555, sin valor, sin sensor, JSON roto, observación de 201", "400 VALIDACION", "ninguno"),
        ("valor 150", "422 REGLA_DE_NEGOCIO, \"fuera del rango fisico ... [-10.00, 60.00]\"", "ninguno"),
        ("sensorId 999", "404 NO_ENCONTRADO", "ninguno"),
        ("sensor inactivo", "409 CONFLICTO", "ninguno"),
        ("sin token", "401 NO_AUTENTICADO", "ninguno"),
        ("token de COORDINACION o RESPONSABLE", "403 ROL_SIN_PERMISO", "ninguno"),
    ], anchos=[7, 6, 3.5], tam=9)
    d.p("springdoc publica en /v3/api-docs el OpenAPI que deduce del código. No es el de referencia porque solo conoce "
        "lo implementado y nombra los esquemas según las clases Java; sirve como comprobación: la prueba 30 revisa que "
        "toda operación del código esté en openapi.yaml y que lo que falte sea solo lo marcado como pendiente.")

    # 8
    d.h("8. Seguridad básica")
    d.tabla(["Tema", "Qué se hizo"], [
        ("Autenticación", "Usuario y contraseña contra hash PBKDF2-HMAC-SHA256 (120 000 iteraciones, sal por usuario); comparación en tiempo constante"),
        ("Token", "JWT HS256 con usuario, rol y caducidad de 30 minutos. El secreto llega por JWT_SECRET; con menos de 32 caracteres la API no arranca; si falta se genera uno aleatorio por arranque"),
        ("Autorización", "El rol sale del token, nunca del cuerpo. POST /api/lecturas exige REGISTRAR_LECTURA (solo OBSERVADOR)"),
        ("CORS", "Un solo origen (CORS_ORIGIN), métodos GET, POST y OPTIONS, cabeceras Authorization, Content-Type y Accept"),
        ("Inyección SQL", "Todas las consultas usan parámetros con nombre"),
        ("Validación", "En el servidor siempre; el cliente solo ayuda"),
        ("Errores", "Cuerpo uniforme sin trazas ni nombres de clases; /api/health publica solo \"PostgreSQL 16.15\""),
        ("Secretos", "application.properties solo tiene referencias ${...}; el repositorio no guarda contraseñas reales (lo revisa verify-module.sh M04)"),
        ("CSRF", "No aplica: el token viaja en una cabecera que el navegador no envía solo"),
    ], anchos=[3, 13.5], tam=9)
    d.p("Límites que conocemos: el token vive en sessionStorage, así que un script inyectado en la página podría leerlo "
        "(Angular escapa las salidas por omisión y no usamos innerHTML); no hay HTTPS porque todo corre en localhost; no "
        "hay límite de intentos de acceso. Los usuarios y contraseñas son ficticios, de laboratorio.")

    # 9
    d.h("9. Despliegue y configuración")
    d.figura_apaisada(DIAG / "03_despliegue.png", "Despliegue local: procesos, puertos y variables.")
    d.tabla(["Variable", "Para qué", "Valor por omisión"], [
        ("DB_URL", "URL JDBC de PostgreSQL", "ninguno; sin ella la API no arranca"),
        ("DB_USER, DB_PASSWORD", "Credenciales de la base", "ninguno"),
        ("JWT_SECRET", "Secreto de firma del token", "aleatorio por arranque"),
        ("CORS_ORIGIN", "Origen permitido del cliente", "http://localhost:4200"),
        ("PORT", "Puerto de la API", "8081"),
    ], anchos=[4, 6.5, 6], tam=9)
    d.p("En desarrollo el navegador solo habla con el 4200: ng serve reenvía /api al 8081 (proxy.conf.json), así que no "
        "hay peticiones entre orígenes. CORS queda configurado para cuando el cliente se sirva desde otro lado.")

    # 10
    d.h("10. La estructura compila y corre")
    d.codigo("dsw-p02-monitoreo-huerto/\n"
             "├── api-spring/                       Spring Boot 2.7.18, Java 11\n"
             "│   ├── pom.xml                       web, jdbc, postgresql 42.7.2, springdoc 1.7.0, test\n"
             "│   └── src/main/java/mx/uv/dsw/huerto/api/\n"
             "│       ├── config/      WebConfig\n"
             "│       ├── seguridad/   TokenFilter, TokenService, CredencialesService, AuthController, Permisos\n"
             "│       ├── error/       ApiError, ApiException, ApiExceptionHandler\n"
             "│       ├── salud/       HealthController\n"
             "│       ├── sensores/    Sensor, SensorRepository, SensorController\n"
             "│       └── lecturas/    LecturaRequest, Lectura, Pagina, ReglasLectura, LecturaRepository,\n"
             "│                        LecturaService, LecturaController\n"
             "├── frontend-angular/                 Angular 16.2.12, Node 18.20.8\n"
             "│   ├── proxy.conf.json               /api -> http://localhost:8081\n"
             "│   └── src/app/\n"
             "│       ├── core/        modelos.ts, api.service.ts, sesion.service.ts, token.interceptor.ts, sesion.guard.ts\n"
             "│       ├── acceso/      acceso.component\n"
             "│       └── lecturas/    lecturas.component\n"
             "├── docs/p04/                         openapi.yaml, arquitectura, modelo, endpoints, trazabilidad, verificación\n"
             "└── scripts/                          verify-m04.sh, pruebas_api.py, recorrido_angular.py, prueba_base_detenida.sh")
    d.p("Resultado de la última compilación, la del 9 de octubre (evidencia 01_build_api.txt y 05_build_frontend.txt):")
    d.codigo(d.leer("01_build_api.txt", filtro=lambda l: "Tests run:" in l and "in mx" not in l or "BUILD SUCCESS" in l)
             + "\n" + d.leer("05_build_frontend.txt", filtro=lambda l: "Initial Total" in l or "Build at" in l))
    d.p("Las 16 pruebas del backend cubren las reglas (ReglasLecturaTest), el token (TokenServiceTest: emisión, "
        "caducidad, firma alterada, secreto corto) y el controlador con MockMvc (LecturaControllerTest: 401, 200, 201 "
        "con Location, 403, 400, 404, 409, 422 y 503). Las 5 del cliente cubren la sesión por rol, la sesión caducada y "
        "el cuerpo que envía ApiService.")

    # 11
    d.h("11. Trazabilidad RF → componente")
    d.tabla(["RF", "Requisito", "Operación", "Componentes (cliente / API / base)", "Prueba", "Estado"], [
        ("RF01", "Zonas", "GET /api/zonas; la zona viaja dentro de Sensor y Lectura", "columna Zona / repositorios (join con zona) / zona", "contrato 07, 09", "dentro de sensores y lecturas: VERIFICADO; /api/zonas: PENDIENTE"),
        ("RF02", "Variables con unidad y rango físico", "GET /api/sensores", "ficha del sensor / SensorController, SensorRepository / variable", "contrato 07; navegador 03", "VERIFICADO"),
        ("RF03", "Registrar lecturas", "POST /api/lecturas", "LecturasComponent, ApiService / LecturaController, LecturaService, ReglasLectura, LecturaRepository / lectura", "contrato 12, 17 a 26; navegador 04, 06, 07; JUnit", "VERIFICADO"),
        ("RF04", "Umbrales", "GET /api/sensores (umbralMinimo, umbralMaximo)", "ficha del sensor / SensorRepository, ReglasLectura.nivelAlerta / umbral", "contrato 07, 16; JUnit", "VERIFICADO"),
        ("RF05", "Historial", "GET /api/lecturas, GET /api/lecturas/{id}", "tabla, filtro y paginador / LecturaService.listar, LecturaRepository / lectura e índice", "contrato 09 a 11, 13, 28; navegador 08", "VERIFICADO"),
        ("RF06a", "Alerta automática", "objeto alerta en POST /api/lecturas; GET /api/alertas", "aviso y etiqueta / LecturaService (transacción), insertarAlerta / alerta", "contrato 14 a 16; navegador 05", "generación: VERIFICADO; /api/alertas: PENDIENTE"),
        ("RF06b", "Anotaciones por rol", "GET y POST /api/anotaciones", "— / — / anotacion (ya existe)", "—", "PENDIENTE"),
        ("RF07", "Modelo relacionado", "todas", "— / repositorios / 7 tablas con FK, UNIQUE y CHECK", "03_consultas_verificacion.sql antes y después", "VERIFICADO"),
        ("RF08", "API Web 3.0", "openapi.yaml completo", "ApiService, TokenInterceptor / api-spring/ / —", "verify-module.sh M04", "6 de 10 operaciones VERIFICADO; 4 PENDIENTE"),
        ("RF09", "Fuente IoT simulada", "origen=simulado en GET /api/lecturas", "filtro de procedencia / LecturaRepository / lectura.origen", "contrato 10; navegador 08", "consulta VERIFICADO; el simulador no es parte de P04"),
        ("RNF01", "Ruta de salud", "GET /api/health", "— / HealthController / —", "contrato 01; base detenida", "VERIFICADO (200 y 503)"),
        ("RNF02", "Autorización por rol", "todas", "sesionGuard, TokenInterceptor / TokenFilter, Permisos, UsuarioAutenticado / —", "contrato 05, 06, 26, 27; navegador 01, 10, 11", "VERIFICADO"),
    ], anchos=[1.2, 2.3, 3.2, 4.6, 2.8, 2.4], tam=8)
    d.p("La matriz completa, con la lectura inversa (de componente a requisito) y la continuidad P02 → P03 → P04, está en "
        "docs/p04/trazabilidad-rf.md.")

    # 12
    d.h("12. Pruebas y evidencia")
    d.p("Todo se regenera con un comando: ./scripts/verify-module.sh M04 compila la API y el cliente, corre sus pruebas, "
        "valida openapi.yaml, arranca la API, ejecuta los 30 casos del contrato, sirve el cliente, hace el recorrido en "
        "navegador, consulta PostgreSQL antes y después, y apaga todo. Lo corrimos completo el 29 de septiembre, cuando "
        "cerramos el código, y otra vez el 9 de octubre antes de entregar; las dos veces terminó con RESULTADO: "
        "VERIFICADO, sin fallos. Las salidas que siguen son de la corrida final.")
    d.codigo(d.leer("13_resumen.txt"))
    d.h("12.1 Contrato contra la API en marcha (30 casos)", 2)
    d.p("Cada caso no solo revisa el código de estado: valida el cuerpo contra el esquema del contrato y, en los casos "
        "negativos, cuenta filas en PostgreSQL antes y después para comprobar que no se guardó nada.")
    d.codigo(d.leer("pruebas_api_resultados.txt"), tam=8)
    d.h("12.2 Recorrido del cliente en navegador (12 casos)", 2)
    d.p("Las capturas se tomaron con Playwright contra el cliente servido por ng serve, que reenvía /api a la API real.")
    d.figura(IMG / "03_lecturas_observador.png", "El observador entra: formulario de captura e historial que llegan de la API.")
    d.figura(IMG / "05_lectura_con_alerta.png", "Lectura de 38 °C: la API responde 201 con alerta ALTA y el cliente la muestra.")
    d.figura(IMG / "06_valor_no_numerico.png", "Valor \"abc\": 400 con el error por campo; lo escrito se conserva.")
    d.figura(IMG / "07_fuera_de_rango_fisico.png", "Valor 150: 422 con el rango físico; la base no cambia.")
    d.figura(IMG / "09_lecturas_coordinacion.png", "Coordinación consulta el historial pero no tiene formulario de captura.")
    d.figura(IMG / "10_token_invalido.png", "Token alterado en el navegador: la API responde 401 y el cliente regresa al acceso.")
    d.figura(IMG / "11_swagger_ui.png", "Operaciones que springdoc deduce del código, en /swagger-ui.html.", ancho_cm=15)
    d.h("12.3 Base de datos detenida", 2)
    d.p("Con docker stop sobre el contenedor del proyecto (sin borrar nada), la salud responde 503, la consulta y el "
        "registro responden 503 BASE_NO_DISPONIBLE, el login sigue funcionando porque no usa la base, y al volver el "
        "contenedor la API se recupera sin reiniciarla. No quedó ninguna lectura a medias.")
    d.codigo(d.leer("14_base_detenida.txt", filtro=lambda l: l.startswith("---") or l.startswith("{") or l.startswith("[estado") or l.startswith("lecturas con")), tam=8)

    # 13
    d.h("13. Problemas que tuvimos")
    d.tabla(["Qué pasó", "Cómo apareció", "Qué hicimos"], [
        ("El login sin contraseña respondía 401 y el contrato dice 400", "caso 04 de pruebas_api.py", "AuthController valida primero que vengan los dos campos"),
        ("Con la base detenida, POST /api/lecturas respondía 500 en lugar de 503", "prueba_base_detenida.sh", "Con @Transactional, si no hay conexión la excepción es CannotCreateTransactionException, que no es DataAccessException. El manejador atiende también TransactionException y se agregó la prueba baseNoDisponible"),
        ("/api/health publicaba la versión completa de PostgreSQL, con sistema operativo y compilador", "revisión de la respuesta", "Se recorta a \"PostgreSQL 16.15\""),
        ("El registro de arranque de Spring Boot escribía el nombre del equipo y el usuario del sistema en la evidencia", "revisión de 09_api_arranque.txt", "spring.main.log-startup-info=false y el anonimizador sustituye ambos datos"),
        ("Las pruebas de Angular no arrancaban: el navegador no se conectaba a Karma", "ng test agotaba el tiempo tres veces", "Chromium reciente separa el modo sin ventana en chrome-headless-shell; el script usa ese ejecutable"),
        ("Un caso del recorrido fallaba por la propia prueba", "caso 03 de recorrido_angular.py", "Buscaba una URL que terminara en /api/sensores y el cliente envía ?activo=true"),
    ], anchos=[5.5, 4, 7], tam=9)
    d.p("Los seis están en docs/bitacora.md con hora, comando y resultado tal cual salió.")

    # 14
    d.h("14. Relación con la rúbrica R04")
    d.tabla(["Criterio", "Pts", "Dónde está"], [
        ("Diagrama de arquitectura", "3", "Figuras 1 a 3 (componentes, secuencia, despliegue) y sección 3; docs/p04/arquitectura.md"),
        ("Justificación Angular/Spring Boot (decisiones y alternativas)", "2.5", "Sección 5, decisiones D1 a D9; versiones en 00_versiones.txt"),
        ("Modelo PostgreSQL", "2", "Sección 6; docs/p04/modelo-datos.md; sql/01_schema.sql; 08_postgres_antes.txt y 12_postgres_despues.txt"),
        ("Endpoints y contratos", "2.5", "Sección 7; docs/p04/openapi.yaml (10 operaciones, 16 esquemas); 30 casos en pruebas_api.txt"),
        ("Aportación individual (bitácora, commits o explicación propia)", "2", "P04_APELLIDO_NOMBRE de cada integrante; docs/bitacora.md entradas 25 a 33; git log"),
    ], anchos=[5.5, 1.2, 9.8], tam=9)
    d.p("El índice que relaciona cada archivo de evidencia con su criterio está en docs/p04/evidencia/INDICE.md.")

    # 15
    d.h("15. Aportación individual")
    d.p("La justificación individual se entrega aparte, con el nombre P04_APELLIDO_NOMBRE. Cada integrante escribe la "
        "suya: qué aportó, con el lugar del repositorio donde se ve, y una decisión técnica justificada con al menos una "
        "alternativa. Nadie escribe el registro de otra persona. Los commits de P04 en el repositorio están a nombre de la "
        "cuenta que hizo la integración (zywoxxx). El reparto acordado en el acta sigue siendo el mismo: desarrollo web "
        "(Juan Pablo Kuri Ricardez), datos (Pedro García Padilla), evidencia y documentación (Alejandro Pacheco Luna y "
        "Ariadna Trejo Álvarez).")

    # 16
    d.h("16. Limitaciones y pendientes")
    d.tabla(["Asunto", "Estado", "Nota"], [
        ("GET /api/zonas, GET /api/alertas, GET y POST /api/anotaciones y sus vistas", "PENDIENTE", "Definidos en el contrato; sin código"),
        ("Caducidad real del token a los 30 minutos", "NO_VERIFICADO", "Probada con reloj fijo en JUnit; no se esperó media hora"),
        ("Rol RESPONSABLE contra la API", "NO_VERIFICADO", "Se probó COORDINACION; ambos tienen los mismos permisos"),
        ("Petición CORS real desde otro origen en el navegador", "NO_VERIFICADO", "Se probó el preflight con peticiones directas"),
        ("Servir el resultado de ng build; despliegue en Linux", "NO_VERIFICADO", "Solo ng serve en Windows 11"),
        ("Reproducción por otro integrante en máquina limpia", "PENDIENTE", "CA05"),
        ("Confirmación del facilitador en F02", "PENDIENTE", "No se afirma que esté confirmada"),
    ], anchos=[7, 3, 6.5], tam=9)
    d.p("Otras limitaciones: un token emitido no se puede revocar; se pierde al cerrar la pestaña; no hay límite de "
        "intentos; los usuarios están en un archivo dentro del jar; springdoc nombra los esquemas según las clases Java, "
        "así que se comparan rutas y métodos, no nombres; las lecturas de prueba quedan en la base hasta correr cleanup.sh.")

    d.h("Anexo. Comandos")
    d.codigo("docker compose -f docker/docker-compose.yml up -d        # la misma base de P02 y P03\n"
             "cd frontend-angular && npm ci && cd ..                   # una vez\n"
             "python -m pip install pyyaml openapi-spec-validator jsonschema playwright && python -m playwright install chromium\n"
             "\n"
             "# API (terminal 1)\n"
             "export DB_URL=jdbc:postgresql://localhost:5436/huerto_db DB_USER=huerto_app DB_PASSWORD=huerto_dev\n"
             "mvn -f api-spring/pom.xml clean package && java -jar api-spring/target/api-spring.jar\n"
             "\n"
             "# Cliente (terminal 2)\n"
             "cd frontend-angular && npx ng serve                      # http://localhost:4200\n"
             "\n"
             "# Verificación y limpieza (con la API y el cliente detenidos)\n"
             "./scripts/verify-module.sh M04\n"
             "./scripts/prueba_base_detenida.sh\n"
             "./scripts/cleanup.sh")
    d.guardar(ENTREGA / "P04_EQUIPO_01.docx")


# =====================================================================
#  Documento individual
# =====================================================================
def individual():
    d = Doc("DSW-19559 · P04 · Justificación individual · Alejandro Pacheco Luna")
    d.portada("P04. Registro individual de aportación y decisiones técnicas",
              "Tercer incremento del proyecto PR09", ("Alejandro Pacheco Luna (zywoxxx)",))

    d.h("1. Datos")
    d.tabla(["", ""], [
        ("Estudiante", "Alejandro Pacheco Luna"), ("Cuenta de GitHub", "zywoxxx"), ("Equipo", "DSW-E01"),
        ("Proyecto", "PR09 - Monitoreo de huerto o ambiente"),
        ("Actividad", "P04 - Arquitectura Web 3.0 (rúbrica R04, criterio de aportación individual)"),
        ("Responsabilidad en el acta", "Evidencia y documentación"),
        ("Repositorio", "github.com/zywoxxx/dsw-p02-monitoreo-huerto"),
    ], anchos=[5, 11.5])

    d.h("2. Qué aporté")
    d.p("Mi parte en el acta es evidencia y documentación, y en este incremento también hice la integración en el "
        "repositorio. Lo que sigue se puede revisar en los commits de P04, que están a nombre de mi cuenta.")
    d.tabla(["Aportación", "Dónde se ve"], [
        ("Contrato de la API escrito antes que el código, con las diez operaciones y el cuerpo común de error", "docs/p04/openapi.yaml"),
        ("Esqueleto de la API integrado, con el flujo principal funcionando", "api-spring/"),
        ("Esqueleto del cliente integrado, con acceso, captura e historial", "frontend-angular/"),
        ("Pruebas del contrato contra la API en marcha, validando cada respuesta contra su esquema", "scripts/pruebas_api.py; evidencia/txt/pruebas_api.txt"),
        ("Recorrido del cliente en navegador y capturas", "scripts/recorrido_angular.py; evidencia/img/"),
        ("Módulo M04 del verificador y prueba con la base detenida", "scripts/verify-m04.sh; scripts/prueba_base_detenida.sh"),
        ("Diagramas de componentes, secuencia y despliegue", "scripts/diagramas_p04.py; docs/p04/diagramas/"),
        ("Documentos de arquitectura, modelo, endpoints, trazabilidad, verificación e índice de evidencia", "docs/p04/*.md"),
    ], anchos=[9.5, 7])

    d.h("3. La decisión que justifico: Spring JDBC en lugar de JPA")
    d.p("Es la decisión D3 del documento de arquitectura del equipo. La desarrollo aquí porque es la que más afecta a lo "
        "que ya teníamos hecho en P02 y P03.")
    d.h("3.1 El problema", 2)
    d.p("La API necesita leer sensores y lecturas y escribir una lectura con su alerta. La base ya existe: son siete "
        "tablas creadas por sql/01_schema.sql, con datos, y las usan también las aplicaciones de P02 y P03. Había que "
        "decidir cómo llega Spring Boot a esas tablas.")
    d.h("3.2 Las opciones", 2)
    d.tabla(["Criterio", "JDBC puro (como P02 y P03)", "Spring JDBC (NamedParameterJdbcTemplate)", "Spring Data JPA (Hibernate)"], [
        ("SQL", "escrito a mano", "escrito a mano", "lo genera Hibernate; se puede escribir con @Query"),
        ("Conexiones", "abrir y cerrar en cada método", "las administra Spring con un pool (HikariCP)", "igual"),
        ("Transacciones", "setAutoCommit(false), commit, rollback", "@Transactional", "@Transactional"),
        ("Código por tabla", "consulta + recorrer el ResultSet", "consulta + RowMapper", "clase @Entity + interfaz de repositorio"),
        ("Relación con el esquema", "ninguna: usa lo que haya", "ninguna: usa lo que haya", "mapea clases a tablas; mal configurado puede intentar crear o alterar tablas"),
        ("Reutiliza el SQL de P02 y P03", "sí", "sí, casi sin cambios", "no"),
        ("Qué hay que aprender", "nada nuevo", "poco", "entidades, relaciones, carga perezosa, estados de una entidad"),
    ], anchos=[3.2, 4, 4.5, 4.8], tam=9)
    d.h("3.3 Por qué Spring JDBC", 2)
    d.vinetas([
        "El SQL ya estaba probado. Las consultas del historial y la inserción con RETURNING id venían de P02. Con Spring "
        "JDBC pasaron a la API cambiando los ? por parámetros con nombre.",
        "Las respuestas de la API no son tablas. El esquema Lectura del contrato junta cinco tablas (lectura, sensor, "
        "zona, variable, alerta). Con SQL es un SELECT con joins y un RowMapper. Con JPA habría que mapear las cinco "
        "entidades con sus relaciones y luego convertirlas a otro objeto para la respuesta.",
        "La base es compartida. Tres aplicaciones escriben en las mismas tablas. Prefiero que ninguna herramienta tenga "
        "la posibilidad de modificar el esquema; con JDBC eso no puede pasar, y además dejamos spring.sql.init.mode=never.",
        "Frente al JDBC puro, quita lo repetitivo. En P03 cada repositorio abría su conexión y la transacción de lectura "
        "más alerta se manejaba a mano. Ahora la transacción es una anotación en LecturaService.registrar y el pool "
        "evita abrir una conexión por petición, que era una limitación anotada en P03.",
    ])
    d.h("3.4 Lo que cuesta", 2)
    d.vinetas([
        "Los RowMapper se escriben a mano; si se agrega una columna hay que tocar la consulta y el mapeo.",
        "No hay paginación automática: LecturaRepository tiene una consulta para los datos y otra para el total.",
        "Si el modelo creciera mucho, o hubiera muchas pantallas de alta y edición, JPA ahorraría más de lo que cuesta. "
        "Con siete tablas y dos recursos implementados no es el caso.",
    ])
    d.h("3.5 Cómo se comprobó que funciona", 2)
    d.tabla(["Comprobación", "Evidencia"], [
        ("Una lectura válida suma exactamente una fila", "casos 12 y 16 de pruebas_api.txt (conteo antes y después)"),
        ("Una lectura fuera de umbral suma una fila en lectura y una en alerta", "casos 14 y 15"),
        ("Una lectura rechazada no deja nada", "casos 17 a 25"),
        ("Con la base detenida no se guarda nada y la API responde 503", "txt/14_base_detenida.txt"),
        ("El jar lleva spring-jdbc y el driver de PostgreSQL, y no lleva Hibernate", "txt/03_jar_contenido.txt"),
    ], anchos=[8.5, 8])

    d.h("4. Un error que me tocó diagnosticar")
    d.p("Al probar con la base detenida, GET /api/sensores respondía 503 como dice el contrato, pero POST /api/lecturas "
        "respondía 500. La diferencia es que el registro es transaccional: Spring intenta abrir la transacción antes de "
        "entrar al método, y cuando no hay conexión lanza CannotCreateTransactionException, que pertenece a la jerarquía "
        "de transacciones y no a la de acceso a datos. El manejador solo atendía DataAccessException, así que el error "
        "caía en el caso genérico. Se corrigió agregando TransactionException al mismo manejador y una prueba "
        "(LecturaControllerTest.baseNoDisponible) para que no vuelva a pasar. Lo que aprendí es que una consecuencia de "
        "usar @Transactional es que aparece un tipo de fallo que con JDBC puro no existía por separado.")
    lineas = d.leer("14_base_detenida.txt").splitlines()
    i = next((k for k, l in enumerate(lineas) if l.startswith("--- POST /api/lecturas")), 0)
    d.codigo("\n".join(lineas[i:i + 3]), tam=8)

    d.h("5. Lo que no hice o queda pendiente")
    d.vinetas([
        "No implementé zonas, alertas ni anotaciones en la API; están en el contrato y marcadas como PENDIENTE.",
        "No probé el despliegue en Linux ni la reproducción en otra máquina.",
        "Este registro es solo mío. Las aportaciones de mis compañeros las escribe cada uno en su archivo.",
    ])
    d.guardar(ENTREGA / "P04_PACHECO_ALEJANDRO.docx")


if __name__ == "__main__":
    equipo()
    individual()
