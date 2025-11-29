# Análisis y Propuesta de Adecuación Curricular

**Del Aprendizaje Fragmentado al Diseño Integrado de Significado**

[![Ver Presentación](https://img.shields.io/badge/Ver-Presentaci%C3%B3n-DC2626?style=for-the-badge)](https://hgcoder.github.io/analsisis-del-curriculo-upaep/)

---

## Descripción del Proyecto

Este repositorio contiene el **proyecto final** para el curso de Análisis del Currículum (UPAEP). El trabajo analiza críticamente el curso **MT1001B** del Tecnológico de Monterrey y propone adecuaciones curriculares fundamentadas en tres marcos teóricos:

| Marco Teórico | Autor(es) | Idea Central |
|---------------|-----------|--------------|
| **Multiliteracidades** | [Cope & Kalantzis](https://newlearningonline.com/multiliteracies) | El estudiante como diseñador activo de significado |
| **Enfoque Socio-Crítico** | [Michael Apple](https://education.wisc.edu/staff/apple-michael-w/) | El currículum no es neutral: ¿a quién sirve? |
| **Conectivismo** | [George Siemens](https://www.siemens.com/global/en.html) | Saber dónde encontrar es tan importante como saber |

---

## Acceso Rápido

| Recurso | Descripción |
|---------|-------------|
| [**Presentación en línea**](https://hgcoder.github.io/analsisis-del-curriculo-upaep/) | Slides interactivos (18 diapositivas) |
| [**Documento académico**](document/main.tex) | Análisis completo en LaTeX (~10 cuartillas) |
| [**Handout: Validación IA**](slides/handout-validacion-ia.md) | Metodología Wideband Delphi con agentes |
| [**Handout: Objetos de Aprendizaje**](slides/handout-objetos-aprendizaje.md) | Rediseño de OA1 y OA2 |
| [**Handout: Sesiones**](slides/handout-sesiones-modificadas.md) | Cambios propuestos en sesiones |

---

## Estructura del Repositorio

```
├── document/           # Documento LaTeX del proyecto
│   ├── main.tex        # Documento principal
│   └── referencias.bib # Bibliografía APA 7
│
├── slides/             # Presentación Slidev
│   ├── slides.md       # Diapositivas principales
│   ├── public/         # Imágenes locales
│   └── handout-*.md    # Materiales de apoyo
│
├── simulation/         # Simulación de evaluación con IA
│   └── run_simulation.py
│
├── agentes/            # Prompts de los agentes evaluadores
│
├── sources/            # Documentación curricular original
│
└── assets/             # Gráficas y visualizaciones
```

---

## Glosario para Educadores

Si eres educador y algunos términos técnicos te resultan nuevos, aquí hay una guía rápida:

### Inteligencia Artificial (IA)

**¿Qué es?** Programas de computadora que pueden realizar tareas que normalmente requieren inteligencia humana, como entender texto, responder preguntas o analizar datos.

**En este proyecto:** Usamos IA de dos formas:
1. **Como evaluadores simulados**: Programamos 5 "agentes" de IA, cada uno con una perspectiva teórica diferente (crítico, multiliteracidades, conectivista, etc.), para que evaluaran el currículum desde múltiples ángulos.
2. **Como herramienta pedagógica**: Proponemos que los estudiantes dialoguen con un asistente de IA programado para hacer preguntas socráticas, no para dar respuestas.

**Herramientas mencionadas:**
- [ChatGPT](https://chat.openai.com/) - Asistente de IA de OpenAI (versión gratuita disponible)
- [Claude](https://claude.ai/) - Asistente de IA de Anthropic
- [Gamma](https://gamma.app/) - Genera presentaciones con IA (tiene versión gratuita)

### API (Interfaz de Programación)

**¿Qué es?** Una forma de que programas de computadora "hablen" entre sí. Es como un mesero en un restaurante: tú le dices lo que quieres, él va a la cocina, y te trae el resultado.

**En este proyecto:** Usamos APIs para conectar con modelos de IA como Llama y GPT-4. Esto permitió automatizar la simulación de evaluación curricular.

**No necesitas saber programar** para usar las ideas de este proyecto. Las propuestas pedagógicas (foros, diálogos con IA, gamificación) se pueden implementar con herramientas gratuitas sin escribir código.

### Kaggle

**¿Qué es?** Una plataforma gratuita con miles de conjuntos de datos reales que cualquier persona puede descargar y usar. También es una comunidad donde científicos de datos comparten sus análisis.

**Enlace:** [kaggle.com](https://www.kaggle.com/)

**En este proyecto:** Proponemos que los estudiantes trabajen con datos reales de Kaggle (por ejemplo, [Customer Segmentation](https://www.kaggle.com/datasets/vjchoudhary7/customer-segmentation-tutorial-in-python)) en lugar de casos ficticios inventados.

### Slidev

**¿Qué es?** Una herramienta para crear presentaciones usando código (Markdown). Genera slides interactivos que se pueden ver en cualquier navegador web.

**Enlace:** [sli.dev](https://sli.dev/)

**En este proyecto:** Las diapositivas de la presentación están hechas con Slidev y se publican automáticamente en GitHub Pages.

### GitHub / GitHub Pages

**¿Qué es?** GitHub es una plataforma para almacenar y compartir código. GitHub Pages es un servicio gratuito que convierte repositorios en sitios web.

**En este proyecto:** El código está almacenado en GitHub, y la presentación se publica automáticamente en GitHub Pages cada vez que hay cambios.

---

## Marcos Teóricos: Recursos para Profundizar

### Multiliteracidades (Cope & Kalantzis)

- [New Learning Online](https://newlearningonline.com/multiliteracies) - Sitio oficial con recursos gratuitos
- Cope, B. & Kalantzis, M. (2009). "Multiliteracies": New Literacies, New Learning. *Pedagogies: An International Journal*, 4(3), 164-195.
- Cope, B. & Kalantzis, M. (2012). *Literacies*. Cambridge University Press.

**Idea clave:** Los estudiantes no son receptores pasivos de información. Son **diseñadores activos de significado** que se expresan a través de múltiples modos: texto, imagen, audio, video, gestos.

### Enfoque Socio-Crítico (Michael Apple)

- Apple, M. W. (1979). *Ideology and Curriculum*. Routledge.
- Apple, M. W. (2004). *Ideology and Curriculum* (3rd ed.). Routledge.

**Idea clave:** El currículum nunca es neutral. Cada decisión sobre qué enseñar refleja **relaciones de poder**. La pregunta fundamental es: ¿a quién sirve este currículum? ¿Qué voces se incluyen y cuáles se silencian?

### Conectivismo (George Siemens)

- Siemens, G. (2005). Connectivism: A Learning Theory for the Digital Age. *International Journal of Instructional Technology and Distance Learning*, 2(1).
- [Artículo original](http://www.intructionaldesignacademy.com/2013/05/28/siemens-2005-connectivism-a-learning-theory-for-the-digital-age/)

**Idea clave:** En la era digital, el aprendizaje ocurre a través de **redes y conexiones**. Saber dónde encontrar información es tan importante como poseer esa información. El aula no puede ser una isla desconectada.

---

## Cómo Usar Este Repositorio

### Solo quiero ver la presentación

Visita: **https://hgcoder.github.io/analsisis-del-curriculo-upaep/**

### Quiero leer el documento completo

El documento está en formato LaTeX en [`document/main.tex`](document/main.tex). Puedes:
- Leerlo directamente en GitHub (se renderiza como texto)
- Compilarlo a PDF con cualquier editor LaTeX ([Overleaf](https://www.overleaf.com/) es gratuito y en línea)

### Quiero ejecutar la presentación localmente

Requisitos: [Node.js](https://nodejs.org/) instalado (versión 18 o superior)

```bash
cd slides
npm install
npm run dev
```

Esto abrirá la presentación en `http://localhost:3030`

### Quiero replicar la simulación con IA

Requisitos: Python 3.8+ y claves de API para los modelos de IA

```bash
cd simulation
pip install -r requirements.txt
cp .env.example .env  # Edita con tus claves de API
python run_simulation.py
```

**Nota:** La simulación requiere acceso a APIs de pago (OpenAI, Together AI). Si no tienes acceso, los resultados de la simulación están documentados en el handout.

---

## Propuestas Pedagógicas que Puedes Implementar

Estas ideas **no requieren conocimientos técnicos** y se pueden adaptar a cualquier curso:

### 1. Datos Reales en Lugar de Casos Ficticios

En lugar de usar casos inventados, pide a tus estudiantes que trabajen con datos reales de:
- [Kaggle](https://www.kaggle.com/datasets) - Miles de datasets gratuitos
- [INEGI](https://www.inegi.org.mx/datos/) - Datos oficiales de México
- [datos.gob.mx](https://datos.gob.mx/) - Portal de datos abiertos del gobierno

### 2. Foros Estructurados en Canvas/Moodle

Estructura los foros con tres fases:
1. **Post inicial obligatorio** (antes de ver otros posts)
2. **Respuestas constructivas** a 2 compañeros
3. **Síntesis integradora** (opcional, para crédito extra)

### 3. Diálogos con IA para Reflexión Crítica

Crea un GPT personalizado (o usa ChatGPT con instrucciones) con este prompt:

> "Eres un experto en ética. Cuando el estudiante te presente una propuesta, haz preguntas socráticas: ¿Quién queda excluido? ¿Qué sesgos podría tener? ¿Qué implicaciones éticas hay? No des respuestas directas, guía al estudiante a descubrirlas."

El estudiante exporta la conversación y escribe una reflexión de 150 palabras.

### 4. Gamificación con Propósito

- **Badges** por logros sustantivos (no por participar, sino por demostrar pensamiento crítico)
- **Tabla de equipos** (no individual, para reducir ansiedad)
- **Narrativa envolvente**: "Son una firma consultora compitiendo por un cliente real"

---

## Preguntas Frecuentes

### ¿Necesito saber programar para usar estas ideas?

No. Las propuestas pedagógicas (foros, IA como herramienta reflexiva, gamificación) se pueden implementar con herramientas existentes como Canvas, ChatGPT, y Kahoot.

### ¿La IA reemplaza al docente?

Absolutamente no. En esta propuesta, la IA es una **herramienta de cuestionamiento**, no una fuente de respuestas. El docente sigue siendo esencial para diseñar las actividades, dar retroalimentación, y facilitar el aprendizaje.

### ¿Qué hago si los estudiantes usan IA para copiar?

La propuesta invierte la lógica: el entregable no es lo que dice la IA, sino **la reflexión del estudiante** después del diálogo. Es difícil copiar un proceso de pensamiento personal.

### ¿Esto funciona en cualquier disciplina?

Los principios (datos reales, reflexión crítica, colaboración en red) son transferibles a cualquier campo. Los ejemplos específicos (Kaggle, marketing) se pueden adaptar a cada disciplina.

---

## Créditos y Licencia

**Autor:** Hesus Garcia Cobos
**Curso:** Análisis del Currículum, UPAEP
**Profesora:** Dra. Melissa Isaaly Mendoza Bernabe
**Fecha:** Noviembre 2025

Este proyecto está disponible bajo licencia [MIT](LICENSE) para fines educativos y de investigación.

---

## Contacto

- **GitHub:** [@HesusG](https://github.com/HesusG)
- **Repositorio:** [analsisis-del-curriculo-upaep](https://github.com/HesusG/analsisis-del-curriculo-upaep)

---

*"El currículum nunca es simplemente un montaje neutral de conocimientos... Es siempre parte de una tradición selectiva."* — Michael Apple
