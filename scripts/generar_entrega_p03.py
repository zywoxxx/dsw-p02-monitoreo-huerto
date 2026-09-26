"""
generar_entrega_p03.py - Arma el documento de entrega de P03 (docs/entrega/P03_EQUIPO_01.docx)
con las capturas y salidas de docs/p03/evidencia/. Requiere python-docx (y Pillow para recortar capturas).
Uso: python scripts/generar_entrega_p03.py
"""
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "docs" / "p03" / "evidencia" / "img"
TXT = ROOT / "docs" / "p03" / "evidencia" / "txt"
OUT = ROOT / "docs" / "entrega" / "P03_EQUIPO_01.docx"
OUT.parent.mkdir(parents=True, exist_ok=True)
RECORTES = OUT.parent / ".recortes"

VERDE = RGBColor(0x2F, 0x6B, 0x3A)
GRIS = RGBColor(0x55, 0x55, 0x55)

doc = Document()
st = doc.styles["Normal"]
st.font.name = "Calibri"
st.font.size = Pt(11)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
st.paragraph_format.space_after = Pt(6)
st.paragraph_format.line_spacing = 1.15
for nivel, tam in ((1, 16), (2, 13), (3, 11.5)):
    h_ = doc.styles[f"Heading {nivel}"]
    h_.font.name = "Calibri"
    h_.font.size = Pt(tam)
    h_.font.bold = True
    h_.font.color.rgb = VERDE
    h_.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
    h_.paragraph_format.space_before = Pt(14 if nivel == 1 else 10)
    h_.paragraph_format.space_after = Pt(4)

sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.59), Cm(27.94)
sec.left_margin = sec.right_margin = Cm(2.5)
sec.top_margin = sec.bottom_margin = Cm(2.2)
hp = sec.header.paragraphs[0]
hp.text = "DSW-19559 · P03 · Equipo DSW-E01 · PR09 Monitoreo de huerto o ambiente"
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


def p(texto, negrita=False, cursiva=False, tam=None, alinear=None, color=None, despues=None):
    par = doc.add_paragraph()
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


def h(texto, nivel=1):
    return doc.add_heading(texto, level=nivel)


def recortar(ruta):
    try:
        from PIL import Image
    except ImportError:
        return ruta
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


def figura(nombre_png, pie, ancho_cm=16.5):
    ruta = IMG / nombre_png
    if not ruta.exists():
        p(f"[falta la imagen {nombre_png}]", cursiva=True, color=GRIS)
        return
    ruta = recortar(ruta)
    par = doc.add_paragraph()
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    par.paragraph_format.space_after = Pt(2)
    par.add_run().add_picture(str(ruta), width=Cm(ancho_cm))
    figura.n += 1
    c = doc.add_paragraph()
    c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = c.add_run(f"Figura {figura.n}. {pie}")
    r.italic = True
    r.font.size = Pt(9.5)
    r.font.color.rgb = GRIS
    c.paragraph_format.space_after = Pt(10)


figura.n = 0


def sombrear(celda, hexcolor):
    tcPr = celda._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hexcolor)
    tcPr.append(shd)


def tabla(encabezados, filas, anchos=None, tam=9.5):
    t = doc.add_table(rows=1, cols=len(encabezados))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, e in enumerate(encabezados):
        c = t.rows[0].cells[i]
        c.text = ""
        r = c.paragraphs[0].add_run(e)
        r.bold = True
        r.font.size = Pt(tam)
        sombrear(c, "E6F2E8")
    for fila in filas:
        cells = t.add_row().cells
        for i, v in enumerate(fila):
            cells[i].text = ""
            r = cells[i].paragraphs[0].add_run(str(v))
            r.font.size = Pt(tam)
    if anchos:
        for fila in t.rows:
            for i, a in enumerate(anchos):
                fila.cells[i].width = Cm(a)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def bloque_codigo(texto, tam=8.5):
    lineas = texto.rstrip("\n").split("\n")
    t = doc.add_table(rows=1, cols=1)
    t.style = "Table Grid"
    c = t.rows[0].cells[0]
    sombrear(c, "F4F4F2")
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
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def leer(nombre, max_lineas=None, desde=None, hasta=None, filtro=None):
    ruta = TXT / nombre
    if not ruta.exists():
        return f"[no se encontro {nombre}]"
    lineas = ruta.read_text(encoding="utf-8", errors="replace").splitlines()
    if desde is not None or hasta is not None:
        lineas = lineas[desde:hasta]
    if filtro:
        lineas = [l for l in lineas if filtro(l)]
    if max_lineas:
        lineas = lineas[:max_lineas]
    return "\n".join(l.rstrip() for l in lineas)


def salto():
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


# ---------- portada ----------
for _ in range(5):
    doc.add_paragraph()
p("Universidad Veracruzana", negrita=True, tam=14, alinear=WD_ALIGN_PARAGRAPH.CENTER, color=VERDE, despues=0)
p("Desarrollo de Sistemas Web (DSW-19559)", tam=12, alinear=WD_ALIGN_PARAGRAPH.CENTER, despues=30)
p("P03. Aplicación Web 2.0 con JSF, PrimeFaces y PostgreSQL", negrita=True, tam=20, alinear=WD_ALIGN_PARAGRAPH.CENTER, despues=6)
p("Segundo incremento del proyecto PR09", tam=14, alinear=WD_ALIGN_PARAGRAPH.CENTER, despues=0)
p("Monitoreo de huerto o ambiente", tam=14, cursiva=True, alinear=WD_ALIGN_PARAGRAPH.CENTER, despues=40)
p("Equipo DSW-E01", negrita=True, tam=13, alinear=WD_ALIGN_PARAGRAPH.CENTER, despues=4)
for nombre in ("Alejandro Pacheco Luna", "Juan Pablo Kuri Ricardez", "Ariadna Trejo Álvarez", "Pedro García Padilla"):
    p(nombre, tam=12, alinear=WD_ALIGN_PARAGRAPH.CENTER, despues=0)
for _ in range(3):
    doc.add_paragraph()
p("Facilitador: Dr. Gabriel Rodríguez Vásquez", tam=11, alinear=WD_ALIGN_PARAGRAPH.CENTER, despues=0)
p("Repositorio: github.com/zywoxxx/dsw-p02-monitoreo-huerto", tam=11, alinear=WD_ALIGN_PARAGRAPH.CENTER, despues=0)
p("Orizaba, Ver., 25 de septiembre de 2026", tam=11, alinear=WD_ALIGN_PARAGRAPH.CENTER)
salto()

h("Contenido")
for linea in ("1. Qué entregamos", "2. De dónde partimos", "3. Versiones que elegimos y por qué", "4. Cómo quedó la aplicación",
              "5. Sesión y roles", "6. Instalación y ejecución", "7. Pruebas y evidencia", "8. Problemas que tuvimos y cómo los resolvimos",
              "9. Relación con la rúbrica R03", "10. Quién hizo qué", "11. Limitaciones y pendientes", "Anexo. Comandos"):
    p(linea, despues=1)
salto()

# 1
h("1. Qué entregamos")
p("Este documento acompaña al repositorio del equipo y describe el segundo incremento del PR09. En P02 el flujo "
  "principal corría con JSP y Servlets; en P03 lo migramos a JSF 2.3 con PrimeFaces 12 sobre el mismo Tomcat 9 y la "
  "misma base PostgreSQL 16. El problema, el alcance, las siete entidades, los datos ficticios, los roles y las reglas "
  "del huerto son los mismos; lo que cambia es cómo se construyen las pantallas, cómo se valida y se responde al "
  "usuario, y que ahora hay control de sesión.")
tabla(["Elemento", "Dónde está"], [
    ("Código JSF/PrimeFaces y configuración", "src/ y pom.xml (WAR web2.war, contexto /web2)"),
    ("Scripts SQL y datos ficticios", "sql/ (sin cambios de esquema respecto a P02)"),
    ("README con requisitos, configuración, compilación, despliegue y usuarios de prueba", "README.md"),
    ("Arquitectura, trazabilidad P02 → P03 → R03, pruebas de aceptación, verificación", "docs/p03/"),
    ("Capturas del recorrido y salidas de comandos", "docs/p03/evidencia/img/ y docs/p03/evidencia/txt/"),
    ("Índice de evidencias frente a R03", "docs/p03/evidencia/INDICE.md"),
    ("Evidencia y documento de P02 (intactos)", "docs/evidencia/, docs/entrega/P02_EQUIPO_01.pdf"),
], anchos=[7.5, 9])

# 2
h("2. De dónde partimos")
p("El commit de partida es 832f377, el último de P02. De ahí conservamos sin tocar los repositorios JDBC, el servicio "
  "que guarda lectura y alerta en una sola transacción, los validadores y las 14 pruebas unitarias; a esas pruebas "
  "les agregamos 7 (límites del umbral, redondeo y autenticación). Quitamos los tres servlets de lecturas, alertas y "
  "anotaciones y las JSP, porque su trabajo ahora lo hacen vistas Facelets y beans CDI. El único servlet que queda es "
  "el de la ruta de salud, que sigue devolviendo JSON.")
p("No agregamos nada de otras etapas: ni API REST, ni Angular, ni simulador de sensores, ni riego automático. Tampoco "
  "abrimos CRUD de zonas o sensores ni atención de alertas, porque no están en el alcance aprobado. Los filtros, la "
  "paginación y los mensajes son mejoras sobre funciones que ya existían.")

# 3
h("3. Versiones que elegimos y por qué")
p("Nos quedamos con la familia javax porque el curso fija Tomcat 9 (Servlet 4.0). Pasar a jakarta habría obligado a "
  "cambiar servidor, dependencias, importaciones y descriptores al mismo tiempo. Las versiones son las del paquete "
  "docente y todas están fijadas en el pom.")
tabla(["Componente", "Versión", "Por qué"], [
    ("Tomcat", "9.0.115", "Servlet 4.0 / EL 3.0 con javax; ya lo usábamos en P02"),
    ("JSF", "Mojarra 2.3.9", "Versión confirmada en M02/M03; un solo jar con API e implementación"),
    ("PrimeFaces", "12.0.0", "Versión del paquete; el artefacto sin classifier es la variante javax"),
    ("CDI", "Weld Servlet 3.1.9 (shaded)", "JSF 2.3 exige CDI para @Named y @ViewScoped; Tomcat no lo trae; Weld se registra solo"),
    ("Extras JDK 11", "javax.annotation-api 1.3.2, jaxb-api 2.3.1", "El JDK 11 no trae @PostConstruct ni DatatypeConverter; Mojarra usa el segundo al cifrar el flash en redirecciones"),
    ("JDBC", "PostgreSQL 42.7.2", "Sin cambios"),
    ("Bean Validation", "no se usa", "Las reglas ya existían como validadores propios probados con JUnit"),
], anchos=[3, 4, 9.5], tam=9)

# 4
h("4. Cómo quedó la aplicación")
p("La separación es la que pide M03: las vistas XHTML con PrimeFaces presentan, los beans de vista coordinan la "
  "petición, los servicios validan y abren la transacción, y los repositorios concentran el SQL. Ninguna vista tiene "
  "SQL ni reglas.")
tabla(["Capa", "Archivos", "Qué hace"], [
    ("Vistas", "login.xhtml, app/lecturas.xhtml, app/alertas.xhtml, app/anotaciones.xhtml, expirada.xhtml, error.xhtml, plantilla.xhtml", "Facelets con p:panel, p:selectOneMenu, p:inputText, p:inputTextarea, p:commandButton, p:messages, p:dataTable, p:tag, p:blockUI"),
    ("Beans", "SesionBean (@SessionScoped), LecturaBean, AlertaBean, AnotacionBean (@ViewScoped)", "Estado de cada formulario; mensajes; recarga del historial tras guardar"),
    ("Servicios", "LecturaService (P02), AnotacionService, AuthService, Permisos", "Reglas, transacción lectura + alerta, autenticación, permisos por rol"),
    ("Repositorios", "SensorRepository, LecturaRepository, AnotacionRepository (P02)", "PreparedStatement, RETURNING id, cierre de recursos"),
    ("Web", "AutenticacionFilter, HealthServlet", "Protección de /app (también para AJAX) y ruta de salud"),
], anchos=[2.4, 7, 7.1], tam=9)
p("Así se ve el botón que registra la lectura en lecturas.xhtml. Procesa el formulario, y actualiza el propio "
  "formulario, los mensajes y la tabla del historial en una sola respuesta AJAX:")
bloque_codigo(
    '<p:commandButton id="btnGuardar" value="Registrar lectura" icon="pi pi-save"\n'
    '                 action="#{lecturaBean.guardar}" process="@form"\n'
    '                 update="@form :mensajes :formTabla:tablaLecturas"/>\n'
    '<p:blockUI block="formLectura" trigger="btnGuardar">Guardando...</p:blockUI>')
p("Y la acción del bean. El valor llega como texto y lo valida el mismo LecturaValidator de P02; si algo falla, no se "
  "limpia nada, así que al re-renderizar el formulario el usuario conserva lo que escribió. Solo cuando la persistencia "
  "se confirmó se vacían los campos y se recarga el historial:")
bloque_codigo(
    "public void guardar() {\n"
    "    if (!sesion.puede(Permiso.REGISTRAR_LECTURA)) {\n"
    "        Mensajes.error(\"Accion no permitida\", \"Tu rol (\" + sesion.getRol() + \") solo puede consultar lecturas.\");\n"
    "        return;\n"
    "    }\n"
    "    try {\n"
    "        LecturaService.Resultado r = lecturaService.registrar(sensorId == null ? null : sensorId.toString(), valor, observacion);\n"
    "        Mensajes.info(\"Lectura #\" + r.getLecturaId() + \" registrada\", \"Se guardo con procedencia manual y su instante de captura.\");\n"
    "        if (r.getAlertaNivel() != null) {\n"
    "            Mensajes.advertencia(\"Alerta \" + r.getAlertaNivel() + \" generada\", \"...la alerta quedo en la misma transaccion.\");\n"
    "        }\n"
    "        valor = null; observacion = null;                 // solo tras confirmar la persistencia\n"
    "        lecturas = lecturaRepository.findRecientes(LIMITE_HISTORIAL);\n"
    "    } catch (ValidacionException e) {\n"
    "        for (String err : e.getErrores()) Mensajes.error(\"La lectura no se registro\", err);\n"
    "    } catch (SQLException e) {\n"
    "        Mensajes.error(\"Error de persistencia\", \"PostgreSQL rechazo la operacion o no esta disponible: \" + e.getMessage());\n"
    "    }\n"
    "}")
p("Usamos p:inputText y no p:inputNumber para el valor a propósito: un convertidor numérico redondea 24.555 a 24.56 "
  "sin avisar, y la regla del huerto es rechazarlo.")
tabla(["Ruta", "Qué hace"], [
    ("/web2/", "Redirige al acceso o al flujo principal según haya sesión"),
    ("/web2/login.xhtml", "Inicio de sesión"),
    ("/web2/app/lecturas.xhtml", "Sensores, captura de lectura con info del sensor por AJAX, historial con filtros, orden y paginación"),
    ("/web2/app/alertas.xhtml", "Alertas con filtro por nivel"),
    ("/web2/app/anotaciones.xhtml", "Zonas y anotaciones firmadas con el rol de la sesión"),
    ("/web2/health", "JSON de salud; 503 si PostgreSQL no responde"),
], anchos=[5.5, 11], tam=9)

# 5
h("5. Sesión y roles")
p("P03 pide control de sesión real, así que ya no se elige el rol en un formulario: hay que entrar con usuario y "
  "contraseña. Los tres usuarios son ficticios y sus contraseñas se guardan como hash PBKDF2-HMAC-SHA256 con sal y "
  "120 000 iteraciones en usuarios.properties dentro del WAR; no hay contraseñas en claro en el repositorio. No agregamos "
  "una tabla de usuarios para no salir de las siete entidades aprobadas; si el equipo lo aprueba más adelante, ese es el "
  "siguiente paso.")
tabla(["Usuario", "Rol", "Puede"], [
    ("observador", "OBSERVADOR", "registrar lecturas, anotar, consultar"),
    ("responsable", "RESPONSABLE", "anotar, consultar"),
    ("coordinacion", "COORDINACION", "anotar, consultar"),
], anchos=[4, 4, 8.5], tam=9.5)
p("Los permisos salen del acta: el observador captura lecturas y anotaciones; el responsable y coordinación consultan y "
  "anotan. El acta no dice que el responsable capture lecturas, y lo respetamos tal cual; cambiarlo es una línea en "
  "Permisos.java y una nota en el acta. Los permisos se comprueban en el servidor dentro de guardar(), no solo ocultando "
  "botones, y el rol de cada anotación se toma de la sesión.")
p("Al entrar se renueva el identificador de sesión (contra fijación), al salir se invalida y la sesión caduca a los 20 "
  "minutos. Las páginas de /app están detrás de un filtro; cuando la petición es AJAX y no hay sesión, el filtro responde "
  "con una redirección en formato partial-response, que es lo que entiende jsf.js. Una redirección HTTP normal rompía la "
  "respuesta parcial; lo comprobamos en la prueba 11e.")

# 6
h("6. Instalación y ejecución")
p("El paso a paso completo está en el README. Resumen de lo que hicimos en Windows con Git Bash:")
bloque_codigo(
    "docker compose -f docker/docker-compose.yml up -d        # PostgreSQL 16 en localhost:5436 (misma base de P02)\n"
    "cp scripts/setenv.bat.example \"$CATALINA_HOME/bin/setenv.bat\"   # DB_URL, DB_USER, DB_PASSWORD\n"
    "mvn clean package                                          # 21 pruebas, target/web2.war\n"
    "export CATALINA_HOME=/c/Tools/apache-tomcat-9.0.115\n"
    "./scripts/redeploy-tomcat.sh target/web2.war web2          # detiene Tomcat, limpia el despliegue viejo, arranca\n"
    "# http://localhost:8080/web2/  ->  usuario observador / Observador#2026")
p("El script de redespliegue existe porque en Windows Tomcat bloquea los jars de WEB-INF/lib mientras corre y el "
  "autodespliegue puede quedarse con clases viejas; nos pasó en el primer intento y quedó en la bitácora.")

# 7
h("7. Pruebas y evidencia")
h("7.1 Verificación reproducible", 2)
p("La guía pide ./scripts/verify-module.sh M03. Nuestro script acepta M02 y M03 y se ejecuta desde la raíz de este "
  "repositorio (la ruta codigo/dsw-evolucion-web del paquete docente no existe aquí). Para M03 compila, corre las "
  "pruebas unitarias, revisa que el WAR traiga Mojarra, PrimeFaces, Weld, beans.xml y vistas XHTML y ningún JSP, consulta "
  "PostgreSQL, redespliega, espera la ruta de salud, comprueba el acceso y la protección de /app, y lanza el recorrido en "
  "navegador. La última corrida terminó así:")
bloque_codigo(leer("16_resumen.txt"))
h("7.2 Pruebas unitarias", 2)
p("21 casos con JUnit 5, sin Tomcat ni base: los 14 de P02 más límites exactos del umbral (15 y 32 no generan alerta), "
  "límites del rango físico, rechazo de 24.555 y 24.550 sin redondeo, autenticación con hash y sal, credenciales "
  "incorrectas, rol no permitido y permisos por rol.")
bloque_codigo(leer("02_pruebas_unitarias.txt", filtro=lambda l: "Tests run" in l or "Test set" in l))
h("7.3 Recorrido en navegador real", 2)
p("Los formularios JSF no se prueban con curl: hay ViewState, cookie de sesión, identificadores de componentes y "
  "respuestas parciales. Escribimos scripts/pruebas_jsf.py con Playwright: entra, elige, captura, lee los mensajes y, en "
  "cada paso, cuenta filas en PostgreSQL para comprobar que la base cambió (o no cambió). Son 26 comprobaciones y todas "
  "quedaron VERIFICADO; el detalle con conteos está en docs/p03/evidencia/txt/pruebas_jsf.txt.")
figura("04_lecturas_inicial_observador.png", "Flujo principal al entrar como observador: cabecera con usuario y rol, formulario, catálogo desplegado e historial.")
figura("05_ajax_info_sensor.png", "Al elegir el sensor, un p:ajax muestra variable, unidad, rango físico y umbral sin recargar la página.")
figura("06_lectura_valida_25_5.png", "Lectura 25.5 °C: mensaje de éxito, fila nueva con procedencia manual y formulario limpio.")
figura("07_lectura_38_alerta_alta.png", "Lectura 38 °C: válida, pero fuera del umbral; la alerta ALTA se guarda en la misma transacción.")
figura("09_limites_15_y_32_sin_alerta.png", "Los límites exactos del umbral (15 y 32) se aceptan sin alerta.")
h("7.4 Validaciones negativas", 2)
p("En todos los casos el servidor responde con el motivo, conserva lo capturado y la base no cambia (los conteos antes y "
  "después son iguales en la bitácora del recorrido).")
figura("11_valor_no_numerico_conserva_entrada.png", "Entrada no numérica: se rechaza y el formulario conserva el valor y la observación escritos.")
figura("12_valor_150_rango_fisico.png", "150 °C está fuera del rango físico de la variable: se rechaza sin tocar PostgreSQL.")
figura("13_valor_24_555_decimales.png", "24.555 se rechaza por exceso de decimales; no se redondea.")
h("7.5 Anotaciones", 2)
figura("18_anotacion_valida_observador.png", "Anotación válida firmada con el rol de la sesión (OBSERVADOR), sin campo de rol en el formulario.")
figura("20_anotacion_lectura_inexistente.png", "Referencia a una lectura inexistente: se rechaza.")
h("7.6 Sesión y roles", 2)
figura("01_acceso.png", "Página de acceso con componentes PrimeFaces.")
figura("22_sesion_expirada_en_ajax.png", "Sesión ausente durante un envío AJAX: el filtro redirige al acceso y no se guarda nada.")
figura("23_coordinacion_sin_formulario.png", "Rol COORDINACION: no hay formulario de lecturas y se explica por qué; sí puede anotar.")
h("7.7 Persistencia", 2)
figura("25_transaccion_revertida.png", "Con una restricción temporal que impide insertar la alerta, la lectura tampoco queda: la transacción se revierte.")
figura("26_base_no_disponible.png", "Con PostgreSQL detenido, la vista avisa y oculta el formulario; al volver la base, todo funciona sin reiniciar Tomcat.")

sh = doc.add_section(WD_SECTION.NEW_PAGE)
sh.orientation = WD_ORIENT.LANDSCAPE
sh.page_width, sh.page_height = Cm(27.94), Cm(21.59)
sh.left_margin = sh.right_margin = Cm(1.8)
sh.top_margin = sh.bottom_margin = Cm(2.0)
h("7.8 Estado de la base de datos después del recorrido", 2)
p("Consultado con psql usando sql/03_consultas_verificacion.sql al terminar verify-module.sh M03. Las lecturas con "
  "observación [prueba] P03 y las anotaciones firmadas por OBSERVADOR y COORDINACION son las del recorrido.")
bloque_codigo(leer("10_postgres_despues.txt", desde=5), tam=7.5)
sv = doc.add_section(WD_SECTION.NEW_PAGE)
sv.orientation = WD_ORIENT.PORTRAIT
sv.page_width, sv.page_height = Cm(21.59), Cm(27.94)
sv.left_margin = sv.right_margin = Cm(2.5)
sv.top_margin = sv.bottom_margin = Cm(2.2)

# 8
h("8. Problemas que tuvimos y cómo los resolvimos")
p("El primero apareció en el primer arranque: cualquier redirección de JSF terminaba en la página de error. El log decía "
  "NoClassDefFoundError: javax/xml/bind/DatatypeConverter. Mojarra cifra la cookie flash con JAXB y el JDK 11 ya no lo "
  "incluye; se resolvió agregando jaxb-api al pom.")
p("El segundo fue con el redespliegue en Windows: al copiar un WAR nuevo, Tomcat seguía sirviendo clases viejas porque "
  "tenía bloqueados los jars del despliegue anterior. De ahí salió scripts/redeploy-tomcat.sh, que detiene, limpia y "
  "arranca.")
p("El tercero fue de JSF, no de la app: el mensaje \"base de datos no disponible\" nunca se veía. El bean de vista se creaba "
  "durante el render, después de que p:messages ya se había pintado. Lo arreglamos con un f:viewAction en cada vista, que "
  "crea el bean antes del render, y bajamos el tiempo de espera de la conexión JDBC a cinco segundos para que la vista "
  "avise pronto.")
p("Los demás fueron del script de pruebas: el contenedor de mensajes conserva el texto anterior hasta que llega la "
  "respuesta AJAX, así que hay que vaciarlo antes de cada envío; y PrimeFaces recorta a 300 caracteres en el cliente el "
  "texto de la anotación, por lo que la regla de más de 300 solo se puede ejercer con la prueba unitaria. Todo está en "
  "docs/bitacora.md con la hora y el diagnóstico.")

# 9
h("9. Relación con la rúbrica R03")
tabla(["Criterio R03", "Puntos", "Dónde está la evidencia"], [
    ("JSF y PrimeFaces", "3", "Vistas XHTML, beans CDI, web.xml/faces-config.xml/beans.xml; txt/03_war_contenido y txt/05_tomcat_log (Mojarra 2.3.9, PrimeFaces 12, Weld); figuras 1 a 5"),
    ("Formularios, validaciones y componentes", "3", "p:selectOneMenu con AJAX, p:inputText, p:inputTextarea con contador, p:messages, p:blockUI, p:dataTable con filtros, orden y paginación; casos 2 a 12; 21 pruebas unitarias; figuras 3, 6 a 11"),
    ("Persistencia PostgreSQL", "2.5", "Misma base y transacción de P02; conteos antes/después en txt/pruebas_jsf.txt; txt/04 y txt/10; figuras 12 y 13; sección 7.8"),
    ("Experiencia de usuario", "2", "Navegación con rol visible, info del sensor antes de capturar, unidades, umbrales y procedencia en tablas, estados vacíos, bloqueo al guardar, mensajes en español, CSS con contraste y diseño adaptable"),
    ("Evidencia, README y repositorio", "1.5", "README, docs/p03 (arquitectura, trazabilidad, pruebas, verificación), docs/p03/evidencia/INDICE.md, bitácora, commits"),
], anchos=[5, 1.5, 10], tam=9)

# 10
h("10. Quién hizo qué")
p("Seguimos el reparto acordado en el acta: Juan Pablo Kuri Ricardez en la parte web (vistas JSF, beans, despliegue), "
  "Pedro García Padilla en datos (base, scripts SQL, repositorios y la comprobación de persistencia), y Alejandro Pacheco "
  "Luna con Ariadna Trejo Álvarez en evidencia y documentación (recorrido de pruebas, capturas, README, trazabilidad e "
  "índice R03). Los commits de este incremento están a nombre de la cuenta que integró el trabajo en GitHub (zywoxxx). "
  "Cada integrante puede ampliar su parte en docs/p03/verificacion.md antes de la entrega.")

# 11
h("11. Limitaciones y pendientes")
tabla(["Punto", "Estado", "Comentario"], [
    ("Caducidad real de 20 minutos", "NO_VERIFICADO", "Se probó el efecto de sesión ausente en un envío AJAX, no la espera"),
    ("Sensor inexistente/inactivo y anotación de 301 por navegador", "NO_VERIFICADO por ese medio", "PrimeFaces no permite enviarlos; cubiertos por JUnit"),
    ("POST forjado por un rol sin permiso", "NO_VERIFICADO por HTTP", "El chequeo está en el bean y en la prueba de permisos"),
    ("Paginación con más de 10 filas; despliegue en Linux", "PENDIENTE", "Prueba manual"),
    ("Reproducción por otro integrante en máquina limpia", "PENDIENTE", "CA05"),
    ("Confirmación del facilitador en F02", "PENDIENTE", "No se afirma que esté confirmada"),
], anchos=[6.5, 3, 7], tam=9)
p("Otras limitaciones: una conexión JDBC por petición (sin pool); usuarios en un archivo de propiedades dentro del WAR; "
  "fechas en la zona horaria del servidor de base de datos; cookie HttpOnly pero sin Secure porque el laboratorio no usa HTTPS.")

h("Anexo. Comandos")
bloque_codigo(
    "export CATALINA_HOME=/c/Tools/apache-tomcat-9.0.115\n"
    "python -m pip install playwright && python -m playwright install chromium\n"
    "./scripts/verify-module.sh M03          # build, WAR, PostgreSQL, redespliegue, salud, recorrido en navegador\n"
    "./scripts/cleanup.sh                     # borra lecturas manuales y anotaciones [prueba]\n"
    "docker exec -i dsw-p02-huerto-db psql -U huerto_app -d huerto_db < sql/03_consultas_verificacion.sql")

doc.save(OUT)
print("documento generado en", OUT)
