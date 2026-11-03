# LOGOS_RC · RC ESTRUCTURAS

## Estructura

```
LOGOS_RC/
├── SVG/   vectorial: Word, web, HTML, imprenta
├── PNG/   imagen a máxima calidad (4000 px de ancho)
├── DXF/   AutoCAD
├── ICO/   favicon web
├── MANUAL_MARCA.pdf
├── generar_logos.py
├── _fuentes/    Montserrat (la usa el script; los logos no la necesitan)
└── referencia/  propuesta original de la otra IA
```

## Nombres

`rc_[tipo]_[color].ext`, y `rc_[tipo]_[color]_[uso].ext` en los archivos de uso concreto.

| Tipo | Para qué |
|---|---|
| `principal` | RC + cercha + ESTRUCTURAS apilado. Portadas. |
| `horizontal` | RC │ ESTRUCTURAS. Memorias, informes, cabeceras. |
| `horizontal-lema` | Horizontal con "EDIFICACIÓN · INDUSTRIAL". Logo especial. |
| `isotipo` | Cuadrado con RC y cercha. Avatar, sellos, iconos. |
| `cajetin` | Una línea con trazo grueso. Cajetín de planos. |

| Color | Para qué |
|---|---|
| `color` | Azul acero + cobre. Uso normal. |
| `negativo` | Blanco + cobre. Fondos oscuros. |
| `mono-negro` | Todo negro. Impresión en blanco y negro, planos, sellos. |

Archivos de uso concreto:

- `PNG/rc_horizontal_color_firma-correo.png`: 600 px y menos de 50 KB, con fondo blanco. Muéstralo a 300 px de ancho en la firma.
- `PNG/` y `SVG/rc_principal_gris-claro_marca-agua`: marca de agua.
- `ICO/rc_isotipo_color_favicon.ico`: favicon (16, 32 y 48 px).
- `DXF/rc_[tipo]_mono-negro_autocad.dxf`: principal, horizontal e isotipo a 100 mm; cajetín a 20 mm.

## AutoCAD

- Formato DXF R2010 en milímetros. Contiene un **bloque** (`RC_CAJETIN`, `RC_HORIZONTAL`…) insertado en 0,0. Para cambiar el tamaño, escala el bloque.
- **Relleno:** sombreados SOLID en color 7 (se imprime negro). Cada sombreado es una pieza maciza sin islas, así los interiores de la R, la A, la cercha… quedan vacíos sin depender de cómo AutoCAD detecte las islas.
- **Capa `RC_CONTORNO`:** los contornos como polilíneas cerradas. Apágala si solo quieres el relleno, o usa solo esta capa si prefieres líneas.

## Regenerar

Cambia los PARÁMETROS al principio del script (colores, textos, tamaños) y ejecuta:

```
python generar_logos.py
```

El script borra y vuelve a crear `SVG/`, `PNG/`, `DXF/` e `ICO/`.

Dependencias: `pip install fonttools Pillow cairosvg reportlab svglib shapely ezdxf`.
