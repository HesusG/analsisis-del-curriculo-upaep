# Análisis y Propuesta de Adecuación Curricular

**Del Aprendizaje Fragmentado al Diseño Integrado de Significado**

Proyecto final para el curso de Análisis del Currículum (UPAEP).

---

## Documentos del Proyecto

| Documento | Descripción |
|-----------|-------------|
| [**Presentación**](https://hgcoder.github.io/analsisis-del-curriculo-upaep/) | Slides interactivos en línea |
| [**Documento académico (PDF)**](document/main.pdf) | Análisis completo (~23 páginas) |

### Materiales de Apoyo

- [Handout: Validación con IA](slides/handout-validacion-ia.md) - Metodología Wideband Delphi
- [Handout: Objetos de Aprendizaje](slides/handout-objetos-aprendizaje.md) - Rediseño de OA1 y OA2
- [Handout: Sesiones](slides/handout-sesiones-modificadas.md) - Cambios propuestos

---

## Validación con Wideband Delphi Simulado

La propuesta curricular fue validada mediante una **simulación de Wideband Delphi con agentes de IA**. Esta metodología es fundamentalmente diferente a simplemente "preguntarle a ChatGPT":

### ¿Por qué no solo preguntar a ChatGPT?

Una consulta directa a un LLM produce una sola perspectiva sin contraste ni iteración. El Wideband Delphi simulado, en cambio:

1. **Crea un panel de expertos simulados**: 5 agentes con perfiles específicos (especialista en multiliteracidades, diseñador instruccional, docente universitario, experto en evaluación, crítico curricular)
2. **Ejecuta rondas iterativas**: Cada agente evalúa independientemente, luego ve las puntuaciones de otros y puede ajustar
3. **Busca consenso mediante diálogo**: Los agentes "discuten" discrepancias hasta converger
4. **Genera métricas cuantificables**: Puntuaciones promedio y desviación estándar por criterio

### Proceso de Simulación

```
Ronda 1: Evaluación independiente (5 agentes × 6 criterios)
         ↓
Ronda 2: Agentes ven puntuaciones de otros, pueden ajustar
         ↓
Ronda 3: Discusión de discrepancias, búsqueda de consenso
         ↓
Resultado: Puntuaciones consolidadas + retroalimentación cualitativa
```

### Resultados Obtenidos

| Criterio | Puntuación | Desv. Est. |
|----------|------------|------------|
| Coherencia teórica | 8.4 | 0.5 |
| Viabilidad de implementación | 7.2 | 0.8 |
| Alineación con competencias | 8.0 | 0.7 |
| Innovación pedagógica | 8.6 | 0.5 |
| Potencial de impacto | 7.8 | 0.8 |
| Claridad de la propuesta | 8.2 | 0.4 |

El código de la simulación está disponible en [`simulation/`](simulation/).

---

## Resumen

El trabajo analiza el curso **MT1001B** del Tecnológico de Monterrey y propone adecuaciones curriculares fundamentadas en:

- **Multiliteracidades** (Cope & Kalantzis) - Estudiante como diseñador de significado
- **Enfoque Socio-Crítico** (Apple) - El currículum no es neutral
- **Conectivismo** (Siemens) - Aprendizaje en redes

---

## Estructura del Repositorio

```
├── document/     # Documento LaTeX (main.tex, main.pdf)
├── slides/       # Presentación Slidev + handouts
├── simulation/   # Scripts de evaluación con IA
└── sources/      # Documentación curricular original
```

---

## Créditos

**Autor:** Hesus Garcia Cobos
**Curso:** Análisis del Currículum, UPAEP
**Profesora:** Dra. Melissa Isaaly Mendoza Bernabe
**Fecha:** Noviembre 2025

---

*"El currículum nunca es simplemente un montaje neutral de conocimientos..."* — Michael Apple
