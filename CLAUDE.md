# Agente de Diseño Pedagógico - Proyecto Curricular UPAEP

## Rol del Agente
Actúas como agente de diseño pedagógico que desarrolla un proyecto final de análisis y adecuación curricular.

## Principios Operativos
1. **Consulta constante**: Antes de cada acción significativa, pregunta con detalle las opciones viables
2. **Evaluación multi-perspectiva**: Argumenta pros/contras desde perspectivas pedagógica, técnica y práctica
3. **Documentación**: Toda decisión relevante debe quedar explicitada
4. **Flujo iterativo**: Propón → Usuario aprueba → Implementa → Verifica

## Estructura del Proyecto
```
project/
├── sources/      # Materiales del currículum (PDFs, referencias)
├── document/     # Documento LaTeX modular
├── slides/       # Presentación Slidev
├── assets/       # Imágenes, tablas, esquemas
├── scripts/      # Automatización
└── agentes/      # Prompts evaluadores
```

## Estándares del Documento
- **Formato**: APA 7ª edición
- **Tipografía**: Times New Roman, 12pt
- **Márgenes**: 2.5cm en todos los lados
- **Interlineado**: 1.5 líneas
- **Extensión**: 6-10 cuartillas (sin portada ni referencias)

## Estándares de Slidev
- **Theme**: Rojo UPAEP suavizado (#DC2626)
- **Fondo**: Blanco (#FFFFFF)
- **Tipografía**: Inter (sans-serif)
- **Aspect ratio**: 16:9

## Git
- NO incluir "Co-Authored-By: Claude" en commits
- NO incluir "Generated with Claude Code" en footers

## Estado del Documento
- **Págs 1-5**: Correcciones menores de estilo y claridad
- **Págs 6+**: Reescritura profunda necesaria
- **Reflexión Final**: Falta escribir completamente

## Marcos Teóricos a Integrar
- Multiliteracidades (Cope & Kalantzis, 2012)
- Enfoque socio-crítico (Apple, 1979)
- Currículum como práctica (Sacristán, 2010)
- Conectivismo (Siemens, 2005)

## Criterios de Evaluación (Rúbrica del Profesor)
| Criterio | Peso |
|----------|------|
| Calidad conceptual | 20% |
| Pertinencia del diagnóstico | 20% |
| Diseño de la propuesta | 25% |
| Reflexión final | 20% |
| Presentación y formato APA | 15% |

## App Evaluadora (HF Spaces)

### Estructura docker-deploy/
```
docker-deploy/
├── app.py                 # Gradio: 5 tabs (Evaluar, RAG, Delphi×2, Metodología)
├── config.py              # LLM_MODEL=gpt-4o, paths, ChromaDB config
├── agents/
│   ├── base.py            # EvaluatorAgent: llama LLM, recalcula compliance
│   ├── synthesizer.py     # Síntesis + Prescription con prioridad
│   └── {pedagogo,profesor,tecnico}.py
├── evaluation/
│   ├── schema.py          # Pydantic: Criterio tiene campo evidencia
│   └── pipeline.py        # PDF → 3 agentes → síntesis → HTML
├── report/templates/       # Jinja2 neobrutalista
├── delphi/                # Tabs Wideband Delphi (estático)
│   ├── loader.py          # Carga .md → HTML al startup
│   ├── renderer.py        # Renderiza 3 templates Jinja2
│   ├── data/              # 13 archivos .md de simulation/output
│   └── prompts/           # 6 archivos .md de simulation/prompts
└── rag/                   # RAG con ChromaDB Cloud
```

### Decisiones Técnicas
- **Gradio 5.23.2**: Versión fijada por compatibilidad con HF Spaces (commit 86e286d)
- **pydantic <2.11**: Cap necesario para evitar crash con Gradio
- **Compliance recalculado**: `count_criteria()` en Python, no por el LLM
- **Evaluador = modelo**: Se muestra "GPT-4o (Pedagogo)" en vez del nombre del prompt
- **Delphi estático**: Los 13 .md se convierten a HTML al startup con `markdown` lib
- **Prescripciones priorizadas**: Agrupadas por Alta/Media/Individual según consenso
