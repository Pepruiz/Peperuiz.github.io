# RC Estructuras — Web Corporativa y Suite de Herramientas Estructurales

Sitio web corporativo y suite interactiva de cálculo y comprobación estructural de **RC Estructuras** (Consultoría e Ingeniería de Estructuras, Madrid).

---

## 🏗️ 1. Arquitectura Técnica y Tecnologías

El proyecto está diseñado bajo un enfoque de **máximo rendimiento, accesibilidad y posicionamiento SEO internacional**:

- **Motor y Empaquetador:** [Vite 5](https://vitejs.dev/) configurado como generador estático multi-página (*Multi-Page Application*).
- **Frontend Core:** HTML5 semántico, CSS3 modular (con CSS Variables) y Vanilla JavaScript (ES6+ Modules).
- **Sin dependencias pesadas:** Cero frameworks reactivos (sin React, sin Vue) para garantizar tiempos de carga sub-segundo (< 1s en First Contentful Paint).
- **Arquitectura Internacional (i18n):** Estructura en subcarpeta física `/en/` (Solución A) para indexación multilingüe en Google mediante etiquetas recíprocas `hreflang` y sitemap XML bilingüe.

---

## 📁 2. Estructura del Proyecto

```text
Web Pepe/
│
├── index.html                             # Página principal (Español)
├── conocenos.html                         # Quiénes somos y equipo (Español)
├── privacidad.html                        # Política de privacidad RGPD (Español)
│
├── herramienta-zapatas.html               # Herramienta: Zapatas Aisladas Rígidas (ES)
├── herramienta-zapatas-combinadas.html    # Herramienta: Zapatas Combinadas Rígidas (ES)
│
├── proyecto-rehabilitacion-entramado.html # Caso de estudio: Rehabilitación Madera 1862 (ES)
├── project-parking-alcobendas.html        # Caso de estudio: Aparcamiento Semienterrado (ES)
├── project-rio-perales.html               # Caso de estudio: Puente Río Perales (ES)
├── project-viviendas-alcala.html          # Caso de estudio: 102 Viviendas Alcalá (ES)
│
├── en/                                    # --- VERSIÓN EN INGLÉS ---
│   ├── index.html                         # Home page (English)
│   ├── about.html                         # About us (English)
│   ├── privacy.html                       # Privacy policy (English)
│   ├── isolated-footing-tool.html         # Tool: Rigid Isolated Footings (EN)
│   ├── combined-footing-tool.html         # Tool: Rigid Combined Footings (EN)
│   ├── project-timber-retrofitting.html   # Case study: Timber Retrofitting (EN)
│   ├── project-parking-alcobendas.html    # Case study: Parking Facility (EN)
│   ├── project-rio-perales.html           # Case study: Perales River Bridge (EN)
│   └── project-viviendas-alcala.html      # Case study: Alcalá Residential (EN)
│
├── assets/                                # Recursos gráficos estáticos
│   ├── logos/                             # Identidad corporativa oficial en SVG/PNG
│   │   ├── rc_horizontal_color.svg        # Logotipo principal oficial
│   │   └── ...
│   └── proyectos/                         # Fotografías y renders de obras por proyecto
│       ├── alcobendas/                    # Fotos del aparcamiento
│       ├── rehabilitacion/                # Fotos de la rehabilitación histórica
│       ├── rio-perales/                   # Fotos del puente
│       └── viviendas-alcala/              # Renders de viviendas
│
├── public/                                # Archivos públicos servidos en la raíz web
│   ├── sitemap.xml                        # Mapa del sitio bilingüe con anotaciones xhtml:link
│   ├── robots.txt                         # Directivas para rastreadores de búsqueda
│   ├── favicon.svg / favicon.ico          # Favicons oficiales en varias resoluciones
│   └── Logos/                             # Manuales y guías de uso de marca
│
├── src/                                   # Código fuente modular
│   ├── style.css                          # Hoja principal que importa los módulos CSS
│   ├── main.js                            # Lógica global (navegación, logo click, animaciones)
│   └── css/                               # Módulos CSS ordenados por responsabilidad
│       ├── variables.css                  # Tokens de color, tipografía y espaciado
│       ├── base.css                       # Reset, botones, layout base y navbar
│       ├── hero.css                       # Estilos del hero y tarjetas de pilares
│       ├── components.css                 # Servicios, portfolio, contacto y formularios
│       ├── tools.css                      # Formularios, canvas SVG y badges de las herramientas
│       └── ticker.css                     # Cintillo de novedades continuo
│
├── docs/                                  # Documentación técnica interna y memorias
│   ├── Memoria_Zapatas_Combinadas.docx    # Base matemática y formulación de zapatas
│   └── diseno.md                          # Notas de diseño
│
├── vite.config.js                         # Configuración de compilación multi-página
└── package.json                           # Scripts y dependencias de desarrollo
```

---

## 🎨 3. Sistema de Diseño e Identidad de Marca

La paleta cromática está unificada en `src/css/variables.css` y refleja la solidez, sobriedad y máxima precisión técnica de la ingeniería estructural:

| Token CSS | Hex / RGB | Aplicación |
| :--- | :--- | :--- |
| `--accent-blue` | `#1E2D3D` | Azul Acero Oscuro corporativo (botones primarios, cabeceras, títulos) |
| `--accent-blue-hover` | `#111C26` | Hover sobre botones primarios y navegación |
| `--accent-slate` | `#475569` | Pizarra / Gris Técnico (subtítulos, acentos sobrios) |
| `--text-primary` | `#1E2D3D` | Tipografía principal de alta legibilidad |
| `--text-secondary` | `#5F6B76` | Párrafos técnicos, subtítulos y textos auxiliares |
| `--bg-secondary` | `#F8FAFC` | Fondo técnico de paneles y tarjetas de proyecto |
| `--border-color` | `#E2E8F0` | Líneas de división y bordes de tarjetas |

### Comportamiento del Logotipo
- Al hacer clic sobre el logotipo en cualquier circunstancia:
  - En la página principal (`index.html` o `/en/index.html`): hace scroll suave hacia la parte superior.
  - En páginas interiores o herramientas: redirige de vuelta a la portada en su respectivo idioma (`index.html` para ES, `/en/index.html` para EN).

---

## 🌐 4. Sistema Multilingüe y SEO Internacional

1. **Correspondencia 1:1 entre Español e Inglés:**
   - Cada página en español tiene su contraparte idéntica en inglés dentro de `/en/`.
   - El selector `.lang-switch` presente en la cabecera permite alternar entre versiones instantáneamente manteniendo la página análoga.

2. **Etiquetas Hreflang en el `<head>` de cada archivo:**
   ```html
   <link rel="canonical" href="https://rcestructuras.es/..." />
   <link rel="alternate" hreflang="es" href="https://rcestructuras.es/..." />
   <link rel="alternate" hreflang="en" href="https://rcestructuras.es/en/..." />
   <link rel="alternate" hreflang="x-default" href="https://rcestructuras.es/..." />
   ```

3. **Sitemap XML Multilingüe (`public/sitemap.xml`):**
   - Incorpora las 18 URLs con el espacio de nombres `xmlns:xhtml="http://www.w3.org/1999/xhtml"` y enlaces cruzados bidireccionales, asegurando que Google indexe tanto el tráfico hispanohablante como el mercado internacional.

---

## 💻 5. Cómo Ejecutar el Proyecto en Local

### Opción A (Recomendada con Node.js / Vite):
```bash
# 1. Instalar dependencias (solo la primera vez)
npm install

# 2. Iniciar servidor de desarrollo en tiempo real
npm run dev
```
Abre en el navegador la dirección que indique la consola (normalmente `http://localhost:5173/`).

### Opción B (Sin Node.js, usando Python):
```bash
python -m http.server 5173
```
Visita `http://localhost:5173/` en el navegador.

### Compilación para Producción (Deploy):
```bash
npm run build
```
Genera la carpeta `dist/` optimizada con todos los HTMLs (raíz y `/en/`), hojas CSS minificadas y scripts listos para ser publicados en GitHub Pages o servidor web.

---

## 🛠️ 6. Cómo Añadir Nuevos Elementos al Proyecto

### Añadir una nueva herramienta de cálculo:
1. Crear el archivo en español en la raíz: `herramienta-[nombre].html`.
2. Crear su homólogo en inglés: `en/[name]-tool.html`.
3. Añadir el botón en la barra selectora `.tool-hub-nav` de todas las herramientas.
4. Registrar ambas páginas en `vite.config.js` dentro de `build.rollupOptions.input`.
5. Añadir las dos URLs con sus etiquetas `xhtml:link` a `public/sitemap.xml`.

### Añadir un nuevo proyecto / caso de estudio:
1. Crear la carpeta en `assets/proyectos/[nombre-proyecto]/` con las fotografías optimizadas.
2. Crear `project-[nombre].html` en español y `en/project-[name].html` en inglés.
3. Enlazar el proyecto en la sección `#projects` de `index.html` y `en/index.html`.
4. Registrar ambas páginas en `vite.config.js` y `public/sitemap.xml`.

---

© 2026 **RC Estructuras** · Consultoría de Estructuras. Todos los derechos reservados.
