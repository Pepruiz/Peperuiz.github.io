# Sistema de Diseño y Arquitectura Frontend · RC Estructuras

Este documento define la identidad visual, el sistema de diseño (Design System), los tokens CSS y las pautas arquitectónicas del frontend de **RC Estructuras**. Está concebido como una guía contextual exhaustiva para que cualquier inteligencia artificial o desarrollador mantenga la máxima coherencia visual, técnica y funcional en futuras ampliaciones.

---

## 1. Filosofía de Diseño e Identidad Visual

* **Arquetipo**: Consultoría técnica de alta ingeniería estructural, cálculo computacional y rehabilitación de patrimonio.
* **Estilo Visual**: *Technical Editorial & Swiss Modernism* — sobrio, limpio, de alta legibilidad y con un marcado carácter arquitectónico.
* **Tono de Marca**: Rigor analítico, precisión matemática, transparencia y profesionalidad contemporánea.
* **Enfoque Tecnológico**: Cero dependencias externas pesadas (sin Tailwind ni Bootstrap). Todo el diseño se apoya en **CSS nativo modular**, diseño responsivo mediante CSS Grid/Flexbox, tipografía suiza/geométrica y gráficos interactivos vectoriales en SVG.

---

## 2. Tokens de Diseño (Design Tokens)

Todos los tokens globales residen en src/css/variables.css dentro del selector :root.

### 2.1 Paleta de Color

| Variable | Valor Hex / RGBA | Uso Principal |
| :--- | :--- | :--- |
| --bg-color | #ffffff | Fondo principal de la web y tarjetas de contenido |
| --bg-secondary | #f8fafc (Slate 50) | Fondos de secciones alternas, herramientas y pies de página |
| --text-primary | #1e293b (Slate 800) | Títulos, encabezados y texto de máxima jerarquía |
| --text-secondary | #475569 (Slate 600) | Párrafos descriptivos, subtítulos y metadatos |
| --accent-blue | #0284c7 (Sky 600) | Color corporativo primario, enlaces, bordes activos y focos |
| --accent-blue-hover | #0369a1 (Sky 700) | Estados hover en botones y enlaces interactivos |
| --accent-yellow | #f59e0b (Amber 500) | Acento para datos variables, armaduras y alertas secundarias |
| --border-color | #e2e8f0 (Slate 200) | Líneas divisorias, bordes de tarjetas y campos de entrada |

#### Colores Semánticos de Diagnóstico (Herramientas de Cálculo)
* **Aprobado / Cumple**: Fondo #ecfdf5 (Emerald 50), Texto #065f46 (Emerald 800), Borde #a7f3d0.
* **Fallo / No Cumple**: Fondo #fef2f2 (Red 50), Texto #991b1b (Red 800), Borde #fecaca.
* **Aviso / Despegue**: Fondo #fff8e6, Texto #6b5314, Borde #e8d48a.

### 2.2 Tipografía

La web emplea dos familias tipográficas de Google Fonts optimizadas para rendimiento:

1. **--font-sans ('Inter', system-ui, sans-serif)**:
   * Utilizada en todo el cuerpo de texto, párrafos, formularios, botones, datos de cálculo y navegación.
   * Pesos: 300 (Light), 400 (Regular), 500 (Medium), 600 (SemiBold), 700 (Bold).
2. **--font-display ('Roboto', system-ui, sans-serif)**:
   * Utilizada en títulos principales (h1, h2, h3), logotipos, etiquetas de sección y rótulos técnicos.
   * Pesos: 400 (Regular), 500 (Medium), 700 (Bold), 800 (ExtraBold).

### 2.3 Medidas, Espaciados y Framing
* --container-width: 1200px, centrado con margin: 0 auto y padding lateral de 2rem.
* --header-height: 80px (altura de la barra fija superior).
* **Radios de Borde (order-radius)**:
  * Botones y tarjetas estándar: 2px a 6px (estética poligonal sobria).
  * Tarjetas de herramientas y paneles: 8px a 12px.
  * Píldoras e insignias (*badges*): 20px a 50px.
* **Fondo con Trama Técnica**:
  El ody cuenta con una retícula sutil (*blueprint grid*) de 40px x 40px, generada con gradientes alternados de 
gba(226, 232, 240, 0.45).

---

## 3. Arquitectura Modular del CSS

Estructura de archivos en src/css/ centralizados en src/style.css:

`
src/
├── style.css             # Punto de entrada maestro (@import de módulos)
└── css/
    ├── variables.css     # Tokens de color, fuentes y dimensiones globales
    ├── base.css          # Reseteo, estilos base, navbar, enlaces y footer
    ├── hero.css          # Portada: Hero, badges pulsantes y pilares técnicos
    ├── ticker.css        # Cinta infinita de software técnico (Marquee continuo)
    ├── components.css    # Secciones Quiénes Somos, Servicios y Proyectos
    └── tools.css         # Design system completo de herramientas de cálculo
`

---

## 4. Componentes y Patrones de la Portada (index.html)

### 4.1 Barra de Navegación (#navbar)
* Fija en la parte superior (position: fixed), altura 80px, fondo translúcido (ackdrop-filter: blur(12px)).
* Logo: RC<span>ESTRUCTURAS</span> con tipografía 700 en estructuras.
* 5 Enlaces Directos: Quiénes Somos (#about), Servicios (#services), Proyectos (#projects), Herramientas (herramienta-zapatas.html), Contacto (#contact).

### 4.2 Hero Section (#hero)
* **Badge Superior**: Píldora con indicador pulsante (.badge-indicator) con leyenda «Consultoría de Ingeniería Estructural».
* **Titular**: clamp(3.2rem, 6vw, 4.8rem) con palabra Estructuras en azul.
* **Pilares Estratégicos**: 3 tarjetas sobrias (*Ámbito*, *Especialidad*, *Normativa*).

### 4.3 Carrusel Infinito de Software (.tech-stack-ribbon)
* Animación continua infinita en CSS con logotipos de Tricalc, AutoCAD, SAP2000, Revit, CYPE y Python. Se pausa suavemente al pasar el ratón.

### 4.4 Sección Editorial «Quiénes Somos» (#about)
* Formato editorial de **doble columna técnica** (sin foto decorativa forzada):
  * **Cabecera**: Etiqueta Filosofía & Enfoque, título y subtítulo de propuesta de valor.
  * **Columna 1**: *Rigor Normativo y Cálculo Avanzado* (Código Estructural, Eurocódigos, elementos finitos).
  * **Columna 2**: *Cercanía y Viabilidad en Obra* (colaboración con arquitectos, optimización de costes y refuerzo de patologías).

### 4.5 Catálogo de Servicios (#services)
* Tarjetas arquitectónicas con iconos SVG enmarcados en azul vitrificado y efecto elevación 	ranslateY(-4px) al hover.

### 4.6 Biblioteca de Proyectos (#projects)
* Cuadrícula de 3 columnas:
  1. *Rehabilitación en el Centro de Madrid* (entramado histórico de 1862).
  2. *Aparcamiento Semienterrado* (patología, derrumbe, rediseño y forjado reticular).
  3. *Más Proyectos en Redacción* (tarjeta con borde discontinuo, insignia Próximamente y enlace a #contact).

### 4.7 Formulario de Contacto Asíncrono (#contact)
* Envío AJAX en segundo plano con FormSubmit sin recargar la página ni redirigir a terceros. Muestra banner verde de confirmación instantánea.

---

## 5. Patrón de Páginas de Detalle de Proyectos (project-*.html)

1. **Hero de Proyecto (.project-hero)**: Etiqueta de categoría, título 2.5rem y barra de metadatos (Ubicación, Año, Tipología, Cliente).
2. **Imagen Principal**: Encuadre arquitectónico con order-radius: 8px y altura máxima limpia (500-540px).
3. **Bloques Técnicos**: Títulos h2 con subrayado azul corporativo, sin numeración en los títulos.
4. **Figuras Arquitectónicas (.article-image-box)**: Contenedores centrados con pie de foto explicativo en cursiva.
5. **Barra de Navegación Inferior (.project-nav)**: Botones para avanzar o volver entre casos de estudio.

---

## 6. Design System de Herramientas de Ingeniería (	ools.css)

Estructura de cálculo (ej. herramienta-zapatas.html):
1. **Hero Técnico**: Etiqueta de categoría (*Geotecnia & Cimentaciones*), título y subtítulo normativo (Código Estructural y CTE DB-SE-C).
2. **1 · Datos de Entrada**: Panel Datos Fijos (Azul) + Panel Datos Variables (Ámbar).
3. **2 · Geometría y Alzados**: Vistas SVG arquitectónicas con cotas y texturas (Planta, Alzado A, Alzado B).
4. **3 · Presiones Sobre el Terreno**: Diagramas de tensiones con límites admisibles y alertas de despegue.
5. **4 · Valores Intermedios**: Grid de métricas numéricas ($, $, $, {C,x}$, {C,y}$, $).
6. **5 · Comprobaciones**: Banner general de diagnóstico + Tarjetas de verificación con insignias CUMPLE / NO CUMPLE.
7. **6 · Criterios y Metodología**: Memoria técnica paso a paso con formulación matemática precisa (.eq).

---

## 7. Guía de Reglas para Desarrolladores e Inteligencias Artificiales

1. **Nombre de Marca**: Todas las referencias deben decir siempre **RC Estructuras**.
2. **Sobriedad y Limpieza**: No añadir imágenes de stock ni decoraciones innecesarias. Si una sección no requiere foto, aplicar formato editorial técnico.
3. **Unidades de Ingeniería**: Siempre en Sistema Internacional (grados, kN, kN·m, N/mm² / MPa con equivalencia \text{ kp/cm}^2 \approx 0.10\text{ N/mm}^2$).
4. **CSS Modular**: No crear estilos inline masivos, apoyarse en las clases existentes en src/css/.
