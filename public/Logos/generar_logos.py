# -*- coding: utf-8 -*-
"""
generar_logos.py - Coleccion de logos de RC ESTRUCTURAS
=======================================================
Regenera TODA la coleccion (SVG, PDF, PNG, ICO, DXF y MANUAL_MARCA.pdf)
a partir de los PARAMETROS de abajo. Cambia un valor y vuelve a ejecutar:

    python generar_logos.py

Dependencias (pip install ...):
    fonttools Pillow cairosvg reportlab svglib shapely ezdxf
Fuente: Montserrat (SIL Open Font License 1.1) en ./_fuentes/Montserrat-VF.ttf
El texto se convierte a trazados: los archivos finales NO dependen de fuentes.
"""
import io
import math
import re
import shutil
import struct
import tempfile
from pathlib import Path

# =====================================================================
# PARAMETROS
# =====================================================================
SIGLAS = "RC"
PALABRA = "ESTRUCTURAS"
LEMA = "EDIFICACIÓN · INDUSTRIAL"   # solo en el logo especial "horizontal-lema"
PREFIJO = "rc"
VERSION_MANUAL = "v1.0 · noviembre 2026"

# Paleta
AZUL = "#1E2D3D"          # azul acero oscuro: siglas y textos
ACERO = "#5F6B76"         # gris acero: textos secundarios (manual)
COBRE = "#A9672F"         # cobre: cercha, acentos
COBRE_CLARO = "#C98A4B"   # cobre aclarado para fondos oscuros (mas contraste)
GRIS_CLARO = "#E6E8EA"    # fondos suaves
GRIS_MARCA = "#E1E4E7"    # marca de agua
NEGRO, BLANCO = "#000000", "#FFFFFF"

# Pesos de Montserrat (fuente variable, eje wght)
PESO_SIGLAS = 700
PESO_TEXTO = 500
PESO_LEMA = 600
PESO_CAJETIN = 600
KERN_RC = -0.02            # ajuste entre letras de las siglas (em)

# Cercha (proporciones respecto al tamano de fuente de las siglas S)
CERCHA_SEPARACION = 0.095  # hueco entre siglas y cordon superior
CERCHA_ALTO = 0.115
CERCHA_TRAZO = 0.020
CERCHA_NODO = 0.95         # radio de nodos = trazo * este factor
CERCHA_NODO_CLAVE = 2.1    # radio del nodo central = trazo * este factor

# Salidas
PNG_ANCHO = 4000          # un unico tamano PNG: el maximo (ancho en px)
DXF_ANCHO_MM = 100        # ancho del bloque DXF de los logos
DXF_CAJETIN_MM = 20       # ancho del bloque DXF del cajetin
FIRMA_ANCHO_PX = 600      # la firma de correo es la unica excepcion de tamano
FIRMA_MAX_KB = 50
FAVICON_PX = (16, 32, 48)

ROOT = Path(__file__).resolve().parent
FUENTE_VF = ROOT / "_fuentes" / "Montserrat-VF.ttf"
CARPETAS = ["SVG", "PNG", "DXF", "ICO"]  # organizacion por tipo de archivo

# =====================================================================
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.basePen import BasePen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union
import cairosvg
from PIL import Image

KO = None  # "sin tinta": el elemento se recorta del fondo (transparente)
S = 1000.0  # unidad de diseno: tamano de fuente de las siglas


# ---------------------------------------------------------------------
# Fuentes y texto -> trazados
# ---------------------------------------------------------------------
_fuentes = {}


def fuente(peso):
    if peso not in _fuentes:
        from fontTools.ttLib.removeOverlaps import removeOverlaps
        ft = instantiateVariableFont(TTFont(FUENTE_VF), {"wght": peso}, inplace=False)
        removeOverlaps(ft)  # la fuente variable trae contornos solapados (p. ej. la R): se limpian
        _fuentes[peso] = ft
    return _fuentes[peso]


class FlattenPen(BasePen):
    """Convierte un glifo en poligonos (para DXF y recortes booleanos)."""

    def __init__(self, gs, tf, seg=16):
        super().__init__(gs)
        self.tf, self.seg, self.rings, self.cur = tf, seg, [], []

    def _p(self, x, y):
        a, b, c, d, e, f = self.tf
        return (a * x + c * y + e, b * x + d * y + f)

    def _moveTo(self, p):
        self.cur, self.last = [self._p(*p)], p

    def _lineTo(self, p):
        self.cur.append(self._p(*p)); self.last = p

    def _qCurveToOne(self, p1, p2):
        p0 = self.last
        for i in range(1, self.seg + 1):
            t = i / self.seg; u = 1 - t
            self.cur.append(self._p(u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
                                    u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]))
        self.last = p2

    def _curveToOne(self, p1, p2, p3):
        p0 = self.last
        for i in range(1, self.seg + 1):
            t = i / self.seg; u = 1 - t
            self.cur.append(self._p(
                u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0],
                u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1]))
        self.last = p3

    def _closePath(self):
        if len(self.cur) > 2:
            self.rings.append(self.cur)
        self.cur = []

    _endPath = _closePath


class Item:
    """Elemento grafico: rol (para el color), trazado SVG exacto y geometria."""

    def __init__(self, role, d, geom):
        self.role, self.d, self.geom = role, d, geom


def rings_to_geom(rings):
    """Regla 'nonzero' de TrueType: la fuente variable trae contornos solapados, asi que
    se unen los contornos exteriores y se restan los interiores (sentido de giro opuesto)."""
    polys = []
    for r in rings:
        p = Polygon(r)
        area = sum(r[i][0] * r[i - 1][1] - r[i - 1][0] * r[i][1] for i in range(len(r))) / 2  # con signo
        polys.append((area > 0, p if p.is_valid else p.buffer(0), abs(area)))
    exterior = max(polys, key=lambda t: t[2])[0]
    fuera = unary_union([p for ccw, p, _ in polys if ccw == exterior])
    dentro = [p for ccw, p, _ in polys if ccw != exterior]
    return fuera.difference(unary_union(dentro)) if dentro else fuera


def texto(peso, s, x, base, size, track, role):
    """Texto -> lista de Items (un trazado por glifo). Devuelve (items, bbox_tinta)."""
    f = fuente(peso)
    gs, cmap = f.getGlyphSet(), f.getBestCmap()
    sc = size / f["head"].unitsPerEm
    items, cx = [], x
    for ch in s:
        g = gs[cmap[ord(ch)]]
        tf = (sc, 0, 0, -sc, cx, base)
        sp = SVGPathPen(gs)
        g.draw(TransformPen(sp, tf))
        fp = FlattenPen(gs, tf)
        g.draw(fp)
        if fp.rings:
            items.append(Item(role, sp.getCommands(), rings_to_geom(fp.rings)))
        cx += g.width * sc + track
    return items, bbox(items)


def texto_ajustado(peso, s, x_izq, base, size, role, ancho):
    """Texto con tracking calculado para que la tinta ocupe exactamente 'ancho'."""
    _, b0 = texto(peso, s, 0, 0, size, 0, role)
    track = (ancho - (b0[2] - b0[0])) / (len(s) - 1)
    return texto(peso, s, x_izq - b0[0], base, size, track, role)


def cap(peso, size):
    return fuente(peso)["OS/2"].sCapHeight * size / 1000.0


def bbox(items):
    bs = [i.geom.bounds for i in items if not i.geom.is_empty]
    return (min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs))


# ---------------------------------------------------------------------
# Primitivas exactas (trazados con arcos, no aproximados)
# ---------------------------------------------------------------------
def f2(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def barra(role, p1, p2, w):
    """Barra de ancho w con extremos redondeados (como un trazo, pero en relleno)."""
    (x1, y1), (x2, y2) = p1, p2
    L = math.hypot(x2 - x1, y2 - y1); h = w / 2
    nx, ny = -(y2 - y1) / L * h, (x2 - x1) / L * h
    d = (f"M{f2(x1+nx)},{f2(y1+ny)}L{f2(x2+nx)},{f2(y2+ny)}A{f2(h)},{f2(h)} 0 0 0 {f2(x2-nx)},{f2(y2-ny)}"
         f"L{f2(x1-nx)},{f2(y1-ny)}A{f2(h)},{f2(h)} 0 0 0 {f2(x1+nx)},{f2(y1+ny)}Z")
    return Item(role, d, LineString([p1, p2]).buffer(h, quad_segs=24))


def rect(role, x, y, w, h):
    d = f"M{f2(x)},{f2(y)}h{f2(w)}v{f2(h)}h{f2(-w)}Z"
    return Item(role, d, box(x, y, x + w, y + h))


def punto(role, cx, cy, r):
    d = (f"M{f2(cx+r)},{f2(cy)}A{f2(r)},{f2(r)} 0 1 0 {f2(cx-r)},{f2(cy)}"
         f"A{f2(r)},{f2(r)} 0 1 0 {f2(cx+r)},{f2(cy)}Z")
    return Item(role, d, Point(cx, cy).buffer(r, quad_segs=32))


# ---------------------------------------------------------------------
# Simbolo: cercha Warren
# ---------------------------------------------------------------------
def cercha_recta(x0, x1, yt, h, sw, paneles=None, role="cercha"):
    """Cercha simplificada: cordones iguales, montantes extremos y diagonales en zigzag.
    Sin nodos ni detalles finos: pensada para 16 px, sellos y cajetines."""
    if paneles is None:
        paneles = max(2, round((x1 - x0) / (1.6 * h)))
    xs = [x0 + (x1 - x0) * i / paneles for i in range(paneles + 1)]
    yb = yt + h
    its = [barra(role, (x0, yt), (x1, yt), sw), barra(role, (x0, yb), (x1, yb), sw),
           barra(role, (x0, yt), (x0, yb), sw), barra(role, (x1, yt), (x1, yb), sw)]
    for i in range(paneles):
        a, b = (yt, yb) if i % 2 == 0 else (yb, yt)
        its.append(barra(role, (xs[i], a), (xs[i + 1], b), sw))
    return its


def cercha(x0, x1, yt, h, sw, paneles=None, nodos=True, clave=True,
           role="cercha", role_clave="nodo"):
    """Cercha Warren con nodos (version detallada)."""
    if paneles is None:
        paneles = max(2, 2 * round((x1 - x0) / (4.4 * h)))
    xt = [x0 + (x1 - x0) * i / paneles for i in range(paneles + 1)]
    xb = [x0 + (x1 - x0) * (i + 0.5) / paneles for i in range(paneles)]
    yb = yt + h
    its = [barra(role, (x0, yt), (x1, yt), sw), barra(role, (xb[0], yb), (xb[-1], yb), sw)]
    for i in range(paneles):
        its.append(barra(role, (xt[i], yt), (xb[i], yb), sw))
        its.append(barra(role, (xb[i], yb), (xt[i + 1], yt), sw))
    if nodos:
        r = sw * CERCHA_NODO
        its += [punto(role, x, yt, r) for x in xt] + [punto(role, x, yb, r) for x in xb]
    if clave and paneles % 2 == 0:
        its.append(punto(role_clave, xt[paneles // 2], yt, sw * CERCHA_NODO_CLAVE))
    return its


def siglas(x, top, s, role="siglas", peso=PESO_SIGLAS):
    return texto(peso, SIGLAS, x, top + cap(peso, s), s, KERN_RC * s, role)


# ---------------------------------------------------------------------
# Logos (cada builder recibe origen ox, oy y escala)
# ---------------------------------------------------------------------
def b_principal(ox=0, oy=0, k=1.0):
    s = S * k
    its, b = siglas(ox, oy, s)
    sw = CERCHA_TRAZO * s
    yt = b[3] + CERCHA_SEPARACION * s
    h = CERCHA_ALTO * s
    x0, x1 = b[0] + sw * CERCHA_NODO, b[2] - sw * CERCHA_NODO
    its += cercha(x0, x1, yt, h, sw, paneles=6)
    ts = 0.155 * s
    base = yt + h + 0.10 * s + cap(PESO_TEXTO, ts)
    t, _ = texto_ajustado(PESO_TEXTO, PALABRA, b[0], base, ts, "texto", b[2] - b[0])
    return its + t


def _bloque_derecho(x, top_rc, cap_rc, s, con_lema):
    ts = 0.30 * s
    cT = cap(PESO_TEXTO, ts)
    gap, h, sw = 0.075 * s, 0.10 * s, 0.017 * s
    ls = 0.105 * s
    cL = cap(PESO_LEMA, ls)
    alto = cT + gap + h + ((0.085 * s + cL) if con_lema else 0)
    top = top_rc + (cap_rc - alto) / 2
    t, bt = texto(PESO_TEXTO, PALABRA, x, top + cT, ts, 0.06 * ts, "texto")
    yt = top + cT + gap
    r = sw * CERCHA_NODO
    its = t + cercha(bt[0] + r, bt[2] - r, yt, h, sw)
    if con_lema:
        l, _ = texto_ajustado(PESO_LEMA, LEMA, bt[0], yt + h + 0.085 * s + cL, ls, "lema", bt[2] - bt[0])
        its += l
    return its


def b_horizontal(ox=0, oy=0, k=1.0, con_lema=False):
    s = S * k
    its, b = siglas(ox, oy, s)
    c = b[3] - b[1]
    xd = b[2] + 0.13 * s
    its.append(rect("linea", xd, b[1] - 0.05 * s, 0.014 * s, c + 0.10 * s))
    its += _bloque_derecho(xd + 0.014 * s + 0.13 * s, b[1], c, s, con_lema)
    return its


def b_horizontal_lema(ox=0, oy=0, k=1.0):
    return b_horizontal(ox, oy, k, con_lema=True)


def _ancho_siglas(s):
    _, b = siglas(0, 0, s)
    return b[2] - b[0], b


def b_isotipo(ox=0, oy=0, k=1.0):
    """Isotipo: fondo macizo, siglas caladas y cercha gruesa de 3 paneles (legible desde 32 px)."""
    L = S * k
    w1, _ = _ancho_siglas(1.0)
    si = 0.64 * L / w1
    gap, h, sw = 0.08 * L, 0.15 * L, 0.036 * L
    alto = cap(PESO_SIGLAS, si) + gap + h
    _, b0 = siglas(0, 0, si)
    its = [rect("fondo", ox, oy, L, L)]
    s_its, b = siglas(ox + (L - (b0[2] - b0[0])) / 2 - b0[0], oy + (L - alto) / 2, si, role="sobre_fondo")
    its += s_its
    its += cercha_recta(b[0] + sw / 2, b[2] - sw / 2, b[3] + gap, h, sw, paneles=3, role="cercha_fondo")
    return its


def b_isotipo_micro(ox=0, oy=0, k=1.0):
    """Solo para 16 px: siglas grandes y una viga maciza (la cercha no se lee a 16 px)."""
    L = S * k
    w1, _ = _ancho_siglas(1.0)
    si = 0.80 * L / w1
    gap, h = 0.08 * L, 0.12 * L
    alto = cap(PESO_SIGLAS, si) + gap + h
    _, b0 = siglas(0, 0, si)
    its = [rect("fondo", ox, oy, L, L)]
    s_its, b = siglas(ox + (L - (b0[2] - b0[0])) / 2 - b0[0], oy + (L - alto) / 2, si, role="sobre_fondo")
    return its + s_its + [rect("cercha_fondo", b[0], b[3] + gap, b[2] - b[0], h)]


def b_cajetin(ox=0, oy=0, k=1.0):
    """Para cajetin de planos: una linea de texto gruesa + cercha gruesa sin detalles."""
    s = S * k
    its, b = siglas(ox, oy, s)
    ts = s * cap(PESO_SIGLAS, 1) / cap(PESO_CAJETIN, 1)
    _, b0 = texto(PESO_CAJETIN, PALABRA, 0, 0, ts, 0.04 * ts, "texto")
    t, bt = texto(PESO_CAJETIN, PALABRA, b[2] + 0.42 * s - b0[0], b[3], ts, 0.04 * ts, "texto")
    its += t
    sw, h = 0.075 * s, 0.30 * s
    paneles = max(4, round((bt[2] - b[0]) / (3.2 * h)))
    its += cercha_recta(b[0] + sw / 2, bt[2] - sw / 2, b[3] + 0.17 * s, h, sw, paneles=paneles)
    return its


# ---------------------------------------------------------------------
# Colores
# ---------------------------------------------------------------------
ROLES = ["siglas", "texto", "cercha", "nodo", "marco", "linea", "lema", "acento",
         "fondo", "sobre_fondo", "cercha_fondo"]


def _todo(c, ko=True):
    d = {r: c for r in ROLES}
    if ko:
        d["sobre_fondo"] = d["cercha_fondo"] = KO
    return d


COLORES = {
    "color": dict(siglas=AZUL, texto=AZUL, cercha=COBRE, nodo=AZUL, marco=AZUL, linea=COBRE,
                  lema=COBRE, acento=COBRE, fondo=AZUL, sobre_fondo=BLANCO, cercha_fondo=COBRE_CLARO),
    "negativo": dict(siglas=BLANCO, texto=BLANCO, cercha=COBRE_CLARO, nodo=BLANCO, marco=BLANCO,
                     linea=COBRE_CLARO, lema=COBRE_CLARO, acento=COBRE_CLARO, fondo=BLANCO,
                     sobre_fondo=AZUL, cercha_fondo=COBRE),
    "mono-negro": _todo(NEGRO),
    "gris-claro": _todo(GRIS_MARCA),  # solo marca de agua
}


# ---------------------------------------------------------------------
# Render: SVG / PDF / PNG / DXF
# ---------------------------------------------------------------------
def geom_a_d(g):
    out = []
    polys = [g] if g.geom_type == "Polygon" else [p for p in getattr(g, "geoms", []) if p.geom_type == "Polygon"]
    for p in polys:
        for ring in [p.exterior] + list(p.interiors):
            cs = list(ring.coords)[:-1]
            out.append("M" + "L".join(f"{f2(x)},{f2(y)}" for x, y in cs) + "Z")
    return "".join(out)


def resolver(items, cw):
    """Pinta en orden; los elementos KO recortan lo que hay debajo (transparencia real)."""
    capas = []
    for it in items:
        col = cw[it.role]
        if col is KO:
            for c in capas:
                if c[2].intersects(it.geom):
                    c[2] = c[2].difference(it.geom); c[1] = None
        else:
            capas.append([col, it.d, it.geom, it.role])
    return capas


def resolver_plano(items, cw):
    """Para DXF: cada elemento recorta a los anteriores (sin solapes); el blanco es papel."""
    capas = []
    for it in items:
        col = cw[it.role]
        for c in capas:
            if c[1].intersects(it.geom):
                c[1] = c[1].difference(it.geom)
        if col not in (KO, BLANCO):
            capas.append([col, it.geom, it.role])
    grupos = {}
    for col, g, role in capas:
        grupos.setdefault((role, col), []).append(g)
    return [(role, col, unary_union(gs)) for (role, col), gs in grupos.items()]


def svg(items, cw, pad=0.03, ancho_mm=None, html=False, fondo=None):
    capas = resolver(items, cw)
    x0, y0, x1, y1 = bbox(items)
    p = pad * max(x1 - x0, y1 - y0)
    x0, y0, w, h = x0 - p, y0 - p, x1 - x0 + 2 * p, y1 - y0 + 2 * p
    tam = ""
    if ancho_mm and not html:
        tam = f' width="{f2(ancho_mm)}mm" height="{f2(ancho_mm * h / w)}mm"'
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{f2(x0)} {f2(y0)} {f2(w)} {f2(h)}"{tam}'
           f' role="img" aria-label="{SIGLAS} {PALABRA}">']
    if not html:
        out.append(f"<title>{SIGLAS} {PALABRA}</title>")
    if fondo:
        out.append(f'<rect x="{f2(x0)}" y="{f2(y0)}" width="{f2(w)}" height="{f2(h)}" fill="{fondo}"/>')
    sep = "" if html else "\n"
    for col, d, g, _ in capas:
        if d is not None:
            out.append(f'<path fill="{col}" d="{d}"/>')
        elif not g.is_empty:
            out.append(f'<path fill="{col}" fill-rule="evenodd" d="{geom_a_d(g)}"/>')
    out.append("</svg>")
    return sep.join(out) + "\n"


def png(svg_txt, ruta, ancho, optimizar=False):
    data = cairosvg.svg2png(bytestring=svg_txt.encode("utf-8"), output_width=ancho)
    im = Image.open(io.BytesIO(data)).convert("RGBA")
    if optimizar:
        im = im.quantize(colors=256, method=Image.Quantize.FASTOCTREE)
    im.save(ruta, optimize=True)


def sin_huecos(pol):
    """Parte un poligono con huecos en piezas macizas que encajan entre si.
    AutoCAD no siempre respeta las islas de un sombreado (el interior de la R salia relleno);
    con piezas sin huecos el resultado no depende de la deteccion de islas."""
    out, pila = [], [pol]
    while pila:
        p = pila.pop()
        if p.is_empty or p.area < 1e-9:
            continue
        if not p.interiors:
            out.append(p)
            continue
        # corte vertical por el centro del hueco: mitad izquierda y mitad derecha
        hx0, _, hx1, _ = Polygon(p.interiors[0]).bounds
        cx = (hx0 + hx1) / 2
        x0, y0, x1, y1 = p.bounds
        for mitad in (box(x0 - 1, y0 - 1, cx, y1 + 1), box(cx, y0 - 1, x1 + 1, y1 + 1)):
            g = p.intersection(mitad)
            pila += [q for q in getattr(g, "geoms", [g]) if q.geom_type == "Polygon"]
    # solape minimo entre piezas contiguas para que no se vea la junta (0,4 ud = ~0,02 mm a 100 mm)
    return [q.buffer(0.4, join_style=2) for q in out]


def dxf(items, cw, ruta, ancho_mm, nombre_bloque):
    import ezdxf
    from ezdxf import const
    capas = resolver_plano(items, cw)
    x0, y0, x1, y1 = bbox(items)
    k = ancho_mm / (x1 - x0)
    doc = ezdxf.new("R2010", setup=False)
    doc.units = ezdxf.units.MM
    doc.header["$MEASUREMENT"] = 1
    blk = doc.blocks.new(name=nombre_bloque, base_point=(0, 0))
    doc.layers.add("RC_CONTORNO", color=7)  # contornos como polilineas (se puede apagar)

    def pts(ring):
        return [((x - x0) * k, (y1 - y) * k) for x, y in list(ring.coords)[:-1]]

    for role, col, g in capas:
        capa = "RC_" + role.upper()
        if capa not in doc.layers:
            doc.layers.add(capa, color=7)
        polys = [g] if g.geom_type == "Polygon" else [p for p in g.geoms if p.geom_type == "Polygon"]
        for pol in polys:
            if pol.is_empty:
                continue
            for ring in [pol.exterior] + list(pol.interiors):
                blk.add_lwpolyline(pts(ring), close=True, dxfattribs={"layer": "RC_CONTORNO"})
            for pieza in sin_huecos(pol):
                ht = blk.add_hatch(dxfattribs={"layer": capa})
                if col == NEGRO:
                    ht.set_solid_fill(color=7, style=0)  # 7 = negro al imprimir (blanco en pantalla oscura)
                else:
                    ht.set_solid_fill(color=256, style=0, rgb=tuple(int(col[i:i + 2], 16) for i in (1, 3, 5)))
                ht.paths.add_polyline_path(pts(pieza.exterior), is_closed=True, flags=const.BOUNDARY_PATH_EXTERNAL)
    doc.modelspace().add_blockref(nombre_bloque, (0, 0))
    doc.saveas(ruta)


# ---------------------------------------------------------------------
# Coleccion
# ---------------------------------------------------------------------
# tipo: (builder, ancho fisico del SVG en mm al insertarlo en Word)
TIPOS = {
    "principal": (b_principal, 60),
    "horizontal": (b_horizontal, 80),
    "horizontal-lema": (b_horizontal_lema, 90),
    "isotipo": (b_isotipo, 25),
    "cajetin": (b_cajetin, 40),
}
COLORES_BASE = ["color", "negativo", "mono-negro"]
DXF_TIPOS = {"principal": DXF_ANCHO_MM, "horizontal": DXF_ANCHO_MM,
             "isotipo": DXF_ANCHO_MM, "cajetin": DXF_CAJETIN_MM}  # en monocromo


def nombre(tipo, color, uso=None, ext="svg"):
    return "_".join([PREFIJO, tipo, color] + ([uso] if uso else [])) + "." + ext


def escribir(ruta, txt):
    ruta.write_text(txt, encoding="utf-8")


def write_ico(ruta, imgs):
    """ICO con una imagen PNG distinta por tamano (diseno especifico para 16 px)."""
    head = struct.pack("<HHH", 0, 1, len(imgs))
    off = 6 + 16 * len(imgs)
    ent, data = b"", b""
    for size, b in imgs:
        ent += struct.pack("<BBBBHHII", size % 256, size % 256, 0, 0, 1, 32, len(b), off + len(data))
        data += b
    ruta.write_bytes(head + ent + data)


def png_bytes(svg_txt, ancho):
    data = cairosvg.svg2png(bytestring=svg_txt.encode("utf-8"), output_width=ancho, output_height=ancho)
    out = io.BytesIO()
    Image.open(io.BytesIO(data)).convert("RGBA").save(out, "PNG", optimize=True)
    return out.getvalue()


def generar():
    for c in CARPETAS:
        if (ROOT / c).exists():
            shutil.rmtree(ROOT / c)
        (ROOT / c).mkdir()

    svg_d, png_d, dxf_d, ico_d = (ROOT / c for c in CARPETAS)

    # Logos: 5 tipos x 3 colores, en SVG y en PNG a maxima resolucion
    for tipo, (fn, mm) in TIPOS.items():
        items = fn()
        pad = 0 if tipo == "isotipo" else 0.03
        for color in COLORES_BASE:
            s = svg(items, COLORES[color], pad=pad, ancho_mm=mm)
            escribir(svg_d / nombre(tipo, color), s)
            png(s, png_d / nombre(tipo, color, ext="png"), PNG_ANCHO)

    # AutoCAD: monocromo (color 7)
    for tipo, mm in DXF_TIPOS.items():
        dxf(TIPOS[tipo][0](), COLORES["mono-negro"], dxf_d / nombre(tipo, "mono-negro", "autocad", "dxf"),
            mm, f"{PREFIJO.upper()}_{tipo.upper().replace('-', '_')}")

    # Firma de correo: unico PNG pequeno (< 50 KB), con fondo blanco para que se vea en modo oscuro
    s = svg(b_horizontal(), COLORES["color"], fondo=BLANCO, pad=0.06)
    ruta = png_d / nombre("horizontal", "color", "firma-correo", "png")
    png(s, ruta, FIRMA_ANCHO_PX)
    if ruta.stat().st_size > FIRMA_MAX_KB * 1024:
        png(s, ruta, FIRMA_ANCHO_PX, optimizar=True)

    # Marca de agua (gris muy claro)
    s = svg(b_principal(), COLORES["gris-claro"], ancho_mm=150)
    escribir(svg_d / nombre("principal", "gris-claro", "marca-agua"), s)
    png(s, png_d / nombre("principal", "gris-claro", "marca-agua", "png"), PNG_ANCHO)

    # Favicon: un .ico con 16 px (version micro) y 32/48 px (isotipo)
    s_iso = svg(b_isotipo(), COLORES["color"], pad=0)
    s_micro = svg(b_isotipo_micro(), COLORES["color"], pad=0)
    write_ico(ico_d / nombre("isotipo", "color", "favicon", "ico"),
              [(px, png_bytes(s_micro if px < 24 else s_iso, px)) for px in FAVICON_PX])


# ---------------------------------------------------------------------
# Manual de marca (PDF, 2 paginas)
# ---------------------------------------------------------------------
def cmyk(hexc):
    r, g, b = (int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5))
    k = 1 - max(r, g, b)
    if k >= 1:
        return (0, 0, 0, 100)
    return tuple(round(100 * v) for v in ((1 - r - k) / (1 - k), (1 - g - k) / (1 - k), (1 - b - k) / (1 - k), k))


def manual():
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas as rl_canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont as RLFont
    from reportlab.lib.colors import HexColor
    from reportlab.platypus import Table, TableStyle, Paragraph
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.graphics import renderPDF
    from svglib.svglib import svg2rlg

    tmp = Path(tempfile.mkdtemp())
    for nom, peso in (("MB", 700), ("MS", 600), ("MM", 500), ("MR", 400)):
        ruta = tmp / f"{nom}.ttf"
        ft = instantiateVariableFont(TTFont(FUENTE_VF), {"wght": peso}, inplace=False)
        for nid in (1, 3, 4, 6):  # nombre interno unico por peso (si no, el PDF los confunde)
            ft["name"].setName(f"Montserrat-RC-{peso}", nid, 3, 1, 0x409)
        ft.save(str(ruta))
        pdfmetrics.registerFont(RLFont(nom, str(ruta)))

    def dib(items, cw, x, y, ancho=None, alto=None, pad=0.0, sx=1, sy=1, fondo=None):
        """Dibuja un logo vectorial; (x, y) = esquina inferior izquierda. Devuelve (w, h, escala)."""
        ruta = tmp / f"t{len(list(tmp.iterdir()))}.svg"
        ruta.write_text(svg(items, cw, pad=pad, fondo=fondo), encoding="utf-8")
        d = svg2rlg(str(ruta))
        k = ancho / d.width if ancho else alto / d.height
        d.scale(k * sx, k * sy)
        w, h = d.width * k * sx, d.height * k * sy
        d.width, d.height = w, h
        renderPDF.draw(d, c, x, y)
        return w, h, k

    W, H = A4
    M = 40
    c = rl_canvas.Canvas(str(ROOT / "MANUAL_MARCA.pdf"), pagesize=A4)
    c.setTitle(f"{SIGLAS} {PALABRA} - Manual de marca")
    az, cu, ac = HexColor(AZUL), HexColor(COBRE), HexColor(ACERO)

    def cabecera(pag, titulo):
        c.setFillColor(az); c.rect(0, H - 62, W, 62, stroke=0, fill=1)
        dib(b_horizontal(), COLORES["negativo"], M, H - 50, alto=38)
        c.setFillColor(HexColor(BLANCO)); c.setFont("MS", 9)
        c.drawRightString(W - M, H - 30, f"MANUAL DE MARCA  ·  {titulo}")
        c.setFillColor(HexColor(COBRE_CLARO)); c.setFont("MR", 7.5)
        c.drawRightString(W - M, H - 42, f"{VERSION_MANUAL}  ·  página {pag}/2")

    def seccion(y, t):
        c.setFillColor(cu); c.rect(M, y - 1, 14, 2.2, stroke=0, fill=1)
        c.setFillColor(az); c.setFont("MB", 11); c.drawString(M + 20, y - 4, t)
        return y - 20

    def txt(x, y, s, f="MR", t=8, col=ac):
        c.setFillColor(col); c.setFont(f, t); c.drawString(x, y, s)

    # ---------------- Pagina 1 ----------------
    cabecera(1, "LOGOTIPO, COLOR Y TIPOGRAFÍA")
    y = H - 92
    y = seccion(y, "1. Versiones del logotipo")
    w, h, _ = dib(b_principal(), COLORES["color"], M + 10, y - 130, alto=125)
    txt(M + 10, y - 145, "Principal (portadas, sellos grandes)")
    vers = [(b_horizontal, "Horizontal (memorias, informes)", 30),
            (b_horizontal_lema, "Especial con lema", 34),
            (b_cajetin, "Cajetín de planos (monocromo en AutoCAD)", 20)]
    yy = y - 10
    for fn, lab, al in vers:
        dib(fn(), COLORES["color"], 260, yy - al, alto=al)
        txt(260, yy - al - 11, lab, t=7)
        yy -= al + 26
    dib(b_isotipo(), COLORES["color"], 260, yy - 52, alto=52)
    txt(260, yy - 63, "Isotipo (avatar, favicon, sellos)", t=7)
    y = min(y - 160, yy - 80)

    # Zona de respeto
    y = seccion(y, "2. Zona de respeto y tamaño mínimo")
    items = b_principal()
    bx = bbox(items)
    _, bR = siglas(0, 0, S)
    x_unid = (bR[3] - bR[1]) / 4  # x = 1/4 de la altura de las siglas
    alto_logo = 105
    k = alto_logo / (bx[3] - bx[1])
    xm = x_unid * k
    lx, ly = M + 10 + xm, y - 20 - xm - alto_logo
    dib(items, COLORES["color"], lx, ly, alto=alto_logo)
    lw = (bx[2] - bx[0]) * k
    c.setStrokeColor(cu); c.setLineWidth(0.6); c.setDash(3, 2)
    c.rect(lx - xm, ly - xm, lw + 2 * xm, alto_logo + 2 * xm, stroke=1, fill=0)
    c.setDash(); c.setStrokeColor(HexColor("#B8BEC4")); c.setLineWidth(0.4)
    c.rect(lx, ly, lw, alto_logo, stroke=1, fill=0)
    txt(lx - xm + 2, ly + alto_logo + xm - 9, "x", "MB", 7, cu)
    notas = ["x = 1/4 de la altura de las siglas RC.",
             "Deja al menos 1x libre alrededor del logo",
             "(sin textos, bordes ni otros logos).",
             "",
             "Tamaño mínimo recomendado:"]
    minimos = [("Principal", "25 mm", "120 px"), ("Horizontal", "35 mm", "160 px"),
               ("Especial con lema", "45 mm", "220 px"), ("Isotipo", "8 mm", "32 px"),
               ("Cajetín de planos", "20 mm", "-")]
    tx = M + 10 + lw + 2 * xm + 30
    ty = y - 22
    for n in notas:
        txt(tx, ty, n, t=8); ty -= 11
    for a, b, cc in minimos:
        txt(tx, ty, a, "MM", 7.5, az); txt(tx + 110, ty, b, t=7.5); txt(tx + 160, ty, cc, t=7.5); ty -= 10.5
    y = min(ly - xm - 26, ty - 14)

    # Colores
    y = seccion(y, "3. Colores")
    pal = [("Azul acero", AZUL, "siglas y textos"), ("Cobre", COBRE, "cercha y acentos"),
           ("Cobre claro", COBRE_CLARO, "acentos sobre fondo oscuro"), ("Gris acero", ACERO, "textos secundarios"),
           ("Gris claro", GRIS_CLARO, "fondos y marca de agua")]
    sw_ = (W - 2 * M - 4 * 8) / 5
    for i, (n, hx, uso) in enumerate(pal):
        x = M + i * (sw_ + 8)
        c.setFillColor(HexColor(hx)); c.setStrokeColor(HexColor("#C9CED3")); c.setLineWidth(0.4)
        c.rect(x, y - 40, sw_, 40, stroke=1 if hx == GRIS_CLARO else 0, fill=1)
        r, g, b = (int(hx[j:j + 2], 16) for j in (1, 3, 5))
        txt(x, y - 52, n, "MB", 8, az)
        txt(x, y - 62, f"HEX {hx}", t=7)
        txt(x, y - 71, f"RGB {r} {g} {b}", t=7)
        txt(x, y - 80, "CMYK≈ {} {} {} {}".format(*cmyk(hx)), t=7)
        txt(x, y - 90, uso, t=6.5)
    txt(M, y - 104, "CMYK calculado por conversión directa: es APROXIMADO, no es Pantone oficial. "
        "Pide prueba de color a la imprenta antes de imprimir en offset.", "MM", 7, cu)
    y -= 126

    # Tipografia
    y = seccion(y, "4. Tipografía")
    muestras = [("MB", "Montserrat Bold 700", "Siglas RC"), ("MM", "Montserrat Medium 500", "Nombre ESTRUCTURAS"),
                ("MS", "Montserrat SemiBold 600", "Lema y cajetín de planos"), ("MR", "Montserrat Regular 400", "Textos de documentos")]
    for i, (f, n, uso) in enumerate(muestras):
        x = M + (i % 2) * 260
        yy = y - (i // 2) * 34
        txt(x, yy - 8, "Aa Bb 0123 ÁÉÍÓÚ Ñ", f, 13, az)
        txt(x, yy - 20, f"{n} · {uso}", t=7)
    txt(M, y - 78, "Licencia SIL Open Font License (uso comercial libre). Descarga: fonts.google.com/specimen/Montserrat.", t=7)
    txt(M, y - 88, "En los logos el texto está convertido a trazados: no hace falta tener la fuente instalada.", t=7)
    c.showPage()

    # ---------------- Pagina 2 ----------------
    cabecera(2, "USOS INCORRECTOS Y ARCHIVOS")
    y = H - 92
    y = seccion(y, "5. Usos incorrectos")
    items = b_principal()
    cw_mal = dict(COLORES["color"], siglas="#B03A2E", texto="#B03A2E", cercha="#2E8B57", nodo="#2E8B57")
    cel_w, cel_h = (W - 2 * M - 20) / 3, 108
    casos = ["No deformar ni estirar", "No cambiar los colores", "No girar",
             "No añadir sombras ni efectos", "No usar sobre fondos sin contraste", "No cambiar la tipografía"]
    for i, cap_ in enumerate(casos):
        cx = M + (i % 3) * (cel_w + 10)
        cy = y - (i // 3 + 1) * (cel_h + 18)
        c.setFillColor(HexColor("#F4F5F6")); c.rect(cx, cy, cel_w, cel_h, stroke=0, fill=1)
        al = 70
        if i == 0:
            dib(items, COLORES["color"], cx + 20, cy + 22, alto=al * 0.65, sx=1.9, sy=1)
        elif i == 1:
            dib(items, cw_mal, cx + cel_w / 2 - 45, cy + 20, alto=al)
        elif i == 2:
            c.saveState(); c.translate(cx + cel_w / 2, cy + cel_h / 2); c.rotate(18)
            dib(items, COLORES["color"], -45, -35, alto=al); c.restoreState()
        elif i == 3:
            dib(items, _todo("#9AA3AB", ko=False), cx + cel_w / 2 - 41, cy + 15, alto=al)
            dib(items, COLORES["color"], cx + cel_w / 2 - 45, cy + 20, alto=al)
        elif i == 4:
            c.setFillColor(HexColor("#2F4356")); c.rect(cx + 15, cy + 10, cel_w - 30, cel_h - 20, stroke=0, fill=1)
            dib(items, COLORES["color"], cx + cel_w / 2 - 45, cy + 20, alto=al)
        else:
            c.setFillColor(az); c.setFont("Times-Bold", 58); c.drawCentredString(cx + cel_w / 2, cy + 44, SIGLAS)
            c.setFont("Times-Roman", 11); c.drawCentredString(cx + cel_w / 2, cy + 24, PALABRA)
        c.setStrokeColor(HexColor("#C0392B")); c.setLineWidth(2.2)
        c.line(cx + cel_w - 26, cy + cel_h - 8, cx + cel_w - 10, cy + cel_h - 24)
        c.line(cx + cel_w - 26, cy + cel_h - 24, cx + cel_w - 10, cy + cel_h - 8)
        txt(cx, cy - 11, cap_, "MM", 7.5, az)
    y = y - 2 * (cel_h + 18) - 34

    y = seccion(y, "6. Qué archivo usar para qué")
    st = ParagraphStyle("t", fontName="MR", fontSize=6.8, leading=8.4, textColor=az)
    sh = ParagraphStyle("h", fontName="MB", fontSize=7, leading=8.6, textColor=HexColor(BLANCO))
    filas = [
        ("Uso", "Archivo recomendado", "Carpeta"),
        ("Memorias de cálculo, informes (Word)", "rc_horizontal_color.svg (o .png)", "SVG / PNG"),
        ("Portadas de memorias y proyectos", "rc_principal_color.svg", "SVG"),
        ("Cajetín de planos AutoCAD", "rc_cajetin_mono-negro_autocad.dxf (bloque de 20 mm, escalable)", "DXF"),
        ("Logo en AutoCAD", "rc_principal / horizontal / isotipo_mono-negro_autocad.dxf (100 mm)", "DXF"),
        ("Firma de correo", "rc_horizontal_color_firma-correo.png (mostrar a 300 px de ancho)", "PNG"),
        ("Favicon web", "rc_isotipo_color_favicon.ico", "ICO"),
        ("Avatar WhatsApp, LinkedIn, redes", "rc_isotipo_color.png", "PNG"),
        ("Marca de agua en informes", "rc_principal_gris-claro_marca-agua.png / .svg", "PNG / SVG"),
        ("Cabeceras de herramientas HTML", "rc_horizontal_color.svg", "SVG"),
        ("Fondos oscuros, presentaciones", "rc_[tipo]_negativo.svg / .png", "SVG / PNG"),
        ("Impresión B/N, planos, sellos", "rc_[tipo]_mono-negro.svg / .png", "SVG / PNG"),
        ("Especial: edificación e industria", "rc_horizontal-lema_color.svg", "SVG"),
    ]
    data = [[Paragraph(a, sh if i == 0 else st), Paragraph(b, sh if i == 0 else st), Paragraph(d, sh if i == 0 else st)]
            for i, (a, b, d) in enumerate(filas)]
    t = Table(data, colWidths=[150, 270, W - 2 * M - 420])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), az),
                           ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor(BLANCO), HexColor("#F2F3F5")]),
                           ("LINEBELOW", (0, 0), (-1, -1), 0.3, HexColor("#D5D9DD")),
                           ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                           ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    tw, th = t.wrapOn(c, W - 2 * M, y)
    t.drawOn(c, M, y - th)
    txt(M, 30, "Archivos generados por generar_logos.py. Para cambiar colores o textos, edita los parámetros del script y vuelve a ejecutarlo.", t=6.5)
    c.showPage()
    c.save()
    shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------
# Verificacion automatica
# ---------------------------------------------------------------------
PATRON = re.compile(r"^rc(_[a-z0-9]+(-[a-z0-9]+)*){2,3}\.(svg|png|ico|dxf)$")


def verificar():
    errores = []
    for c in CARPETAS + ["referencia"]:
        d = ROOT / c
        archivos = list(d.iterdir())
        if not archivos:
            errores.append(f"Carpeta vacia: {c}")
        for f in archivos:
            if not PATRON.match(f.name):
                errores.append(f"Nombre fuera de convencion: {c}/{f.name}")
            if f.suffix == ".svg":
                t = f.read_text(encoding="utf-8")
                if re.search(r"<text|font-family|@font-face|<image|xlink:href|href=", t):
                    errores.append(f"SVG con dependencia externa: {f.name}")
            if f.suffix == ".dxf":
                import ezdxf
                doc = ezdxf.readfile(f)
                hs = [e for b in doc.blocks for e in b if e.dxftype() == "HATCH"]
                if doc.audit().has_errors or any(len(h.paths) != 1 for h in hs):
                    errores.append(f"DXF con errores o sombreados con islas: {f.name}")
    for f in (ROOT / "PNG").glob("*firma-correo*.png"):
        kb = f.stat().st_size / 1024
        print(f"  firma {f.name}: {kb:.1f} KB")
        if kb > FIRMA_MAX_KB:
            errores.append(f"Firma > {FIRMA_MAX_KB} KB: {f.name}")
    n = sum(1 for c in CARPETAS for _ in (ROOT / c).iterdir())
    print(f"  {n} archivos en {len(CARPETAS)} carpetas")
    for e in errores:
        print("  ERROR:", e)
    print("  Verificacion OK" if not errores else f"  {len(errores)} errores")
    return not errores


if __name__ == "__main__":
    print("Generando coleccion...")
    generar()
    print("Generando manual de marca...")
    manual()
    print("Verificando...")
    verificar()
