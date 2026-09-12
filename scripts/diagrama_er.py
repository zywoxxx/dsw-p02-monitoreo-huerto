"""
diagrama_er.py - Dibuja el diagrama entidad-relacion del PR09 como PNG (docs/evidencia/img/00_modelo_er.png).
Se usa en el documento de entrega. Requiere Pillow: python -m pip install pillow
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent.parent / "docs" / "evidencia" / "img" / "00_modelo_er.png"
W, H = 1500, 900
img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)


def fuente(nombre, tam):
    for f in (nombre, "arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(f, tam)
        except OSError:
            continue
    return ImageFont.load_default()


F_T = fuente("arialbd.ttf", 22)
F_A = fuente("arial.ttf", 17)
F_S = fuente("arial.ttf", 15)

VERDE = (47, 107, 58)
GRIS = (90, 90, 90)
BORDE = (120, 120, 120)

entidades = {
    "zona": (60, 80, ["id  PK", "nombre  UK", "cultivo", "ubicacion", "creada_en"]),
    "variable": (60, 520, ["id  PK", "clave  UK", "nombre", "unidad", "valor_minimo", "valor_maximo"]),
    "sensor": (420, 300, ["id  PK", "zona_id  FK", "variable_id  FK", "codigo  UK", "activo", "instalado_en"]),
    "umbral": (780, 80, ["id  PK", "sensor_id  FK UK", "minimo", "maximo"]),
    "lectura": (780, 400, ["id  PK", "sensor_id  FK", "valor", "origen  manual|simulado", "observacion", "registrado_en"]),
    "alerta": (1150, 400, ["id  PK", "lectura_id  FK UK", "nivel  BAJA|ALTA", "mensaje", "atendida", "creada_en"]),
    "anotacion": (1150, 80, ["id  PK", "zona_id  FK", "lectura_id  FK (opcional)", "autor_rol  3 roles", "texto", "creada_en"]),
}
BW = 290
cajas = {}
for nombre, (x, y, attrs) in entidades.items():
    bh = 44 + 26 * len(attrs) + 12
    d.rectangle([x, y, x + BW, y + bh], outline=BORDE, width=2, fill=(250, 250, 248))
    d.rectangle([x, y, x + BW, y + 40], fill=VERDE)
    d.text((x + 12, y + 8), nombre, font=F_T, fill="white")
    for i, a in enumerate(attrs):
        d.text((x + 14, y + 50 + 26 * i), a, font=F_A, fill=GRIS)
    cajas[nombre] = (x, y, x + BW, y + bh)


def centro_lado(caja, lado):
    x1, y1, x2, y2 = caja
    return {"d": (x2, (y1 + y2) // 2), "i": (x1, (y1 + y2) // 2),
            "a": ((x1 + x2) // 2, y1), "b": ((x1 + x2) // 2, y2)}[lado]


def pata_de_gallo(desde, hasta):
    """Dibuja la pata de gallo en 'hasta', orientada segun la direccion desde -> hasta."""
    import math
    dx, dy = hasta[0] - desde[0], hasta[1] - desde[1]
    n = math.hypot(dx, dy) or 1
    ux, uy = dx / n, dy / n           # unitario a lo largo de la linea
    px, py = -uy, ux                  # perpendicular
    base = (hasta[0] - ux * 16, hasta[1] - uy * 16)
    for k in (-1, 0, 1):
        d.line([base, (hasta[0] + px * 9 * k, hasta[1] + py * 9 * k)], fill=BORDE, width=2)


def etiqueta_en(punto, etiqueta):
    tw = d.textlength(etiqueta, font=F_S)
    x, y = punto
    d.rectangle([x - tw / 2 - 4, y - 11, x + tw / 2 + 4, y + 11], fill="white")
    d.text((x - tw / 2, y - 9), etiqueta, font=F_S, fill=VERDE)


def relacion(a, la, b, lb, etiqueta, muchos_en_b=True, via=None):
    """Linea entre dos cajas; 'via' permite un trazado en escuadra por puntos intermedios."""
    p1 = centro_lado(cajas[a], la)
    p2 = centro_lado(cajas[b], lb)
    puntos = [p1] + (via or []) + [p2]
    d.line(puntos, fill=BORDE, width=2, joint="curve")
    if muchos_en_b is True:
        pata_de_gallo(puntos[-2], p2)
    elif muchos_en_b is False and lb is not None and etiqueta.startswith("0..1"):
        pata_de_gallo(puntos[1], p1)
    # etiqueta a la mitad del tramo mas largo
    tramos = list(zip(puntos, puntos[1:]))
    q1, q2 = max(tramos, key=lambda t: abs(t[1][0] - t[0][0]) + abs(t[1][1] - t[0][1]))
    etiqueta_en(((q1[0] + q2[0]) // 2, (q1[1] + q2[1]) // 2), etiqueta)


relacion("zona", "d", "sensor", "i", "1 : N  instala")
relacion("variable", "d", "sensor", "i", "1 : N  mide")
relacion("sensor", "d", "umbral", "i", "1 : 0..1  tiene", muchos_en_b=None)
relacion("sensor", "d", "lectura", "i", "1 : N  registra")
relacion("lectura", "d", "alerta", "i", "1 : 0..1  genera", muchos_en_b=None)
# zona -> anotacion por arriba, en escuadra, para no cruzar el recuadro de umbral
zx = (cajas["zona"][0] + cajas["zona"][2]) // 2
ax = (cajas["anotacion"][0] + cajas["anotacion"][2]) // 2
relacion("zona", "a", "anotacion", "a", "1 : N  recibe", via=[(zx, 40), (ax, 40)])
relacion("lectura", "a", "anotacion", "b", "0..1 : N  comenta")

d.text((60, H - 60), "PR09 Monitoreo de huerto o ambiente - modelo de datos P02 (7 entidades). "
       "Las seis de la ficha C11 mas 'sensor' como dispositivo que mide una variable en una zona.",
       font=F_S, fill=GRIS)
OUT.parent.mkdir(parents=True, exist_ok=True)
img.save(OUT)
print("diagrama guardado en", OUT)
