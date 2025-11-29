# Metodología de Validación con Inteligencia Artificial

## Wideband Delphi con Agentes IA

**Proyecto:** Análisis y Propuesta de Adecuación Curricular MT1001B
**Autor:** Hesus Garcia Cobos
**Fecha:** Noviembre 2025

---

## Descripción de la Metodología

Se realizó una simulación del método **Wideband Delphi** utilizando agentes de inteligencia artificial, cada uno programado con una perspectiva teórica distinta. El objetivo fue triangular el análisis curricular desde múltiples perspectivas teóricas.

### Metodología: Wideband Delphi Simulado

Se implementó el método en **tres rondas**:

1. **Ronda 1**: Cada agente evaluó el currículum de forma independiente según su marco teórico.
2. **Ronda 2**: Los agentes revisaron las posiciones de sus pares y debatieron puntos de convergencia y divergencia.
3. **Ronda 3**: Un moderador sintetizó consensos, disensos y recomendaciones priorizadas.

### Panel de Agentes

| Agente | Perspectiva | Referencias Base |
|--------|-------------|------------------|
| **Dr. Crítico** | Teoría curricular crítica | Apple (2004), Gimeno Sacristán (1991) |
| **Dra. Multiliteracidades** | Diseño de significado | Cope & Kalantzis (2009, 2012) |
| **Dr. Conectivista** | Era digital | Siemens (2005) |
| **Dra. Marketing Educativo** | PBL e IA en negocios | Guha et al. (2024), Demirci et al. (2023) |
| **Dr. Pedagogía Crítica** | Pedagogía de la liberación | Freire (1970), Giroux (1997) |

**Implementación técnica:** Modelos de lenguaje (Llama 3.3 70B, Qwen 72B vía Together AI) con moderador GPT-4o (OpenAI) para síntesis final.

---

## Dimensiones Evaluadas

Cada agente evaluó el currículum en 6 dimensiones, usando una escala de 1 a 10:

1. **Coherencia epistemológica**: ¿Hay coherencia entre objetivos, contenidos y evaluación?
2. **Rol del estudiante**: ¿El estudiante es activo o pasivo en su aprendizaje?
3. **Integración tecnológica**: ¿La tecnología se usa como herramienta de aprendizaje?
4. **Reflexión crítica**: ¿Se fomenta el cuestionamiento y análisis profundo?
5. **Conexión teoría-práctica**: ¿Los contenidos teóricos se vinculan con aplicaciones reales?
6. **Evaluación del aprendizaje**: ¿La evaluación mide competencias reales o solo memorización?

---

## Resultados: Puntuaciones Consolidadas

| Dimensión | Crítico | Multilit. | Conect. | Marketing | Ped. Crítica | **Promedio** |
|-----------|:-------:|:---------:|:-------:|:---------:|:------------:|:------------:|
| Coherencia epistemológica | 7 | 7 | 7 | 7 | 7 | **7.0** |
| Rol del estudiante | 8 | 8 | 6 | 8 | 7.5 | **7.5** |
| Integración tecnológica | 6 | 6 | 5 | 5 | 5.5 | **5.5** |
| Reflexión crítica | 5 | 7 | 6 | 6 | 6 | **6.0** |
| Conexión teoría-práctica | 8 | 8 | 8 | 8 | 8 | **8.0** |
| Evaluación del aprendizaje | 7 | 6 | 5 | 5 | 5.75 | **5.75** |

### Interpretación

- **Fortalezas (≥7.0)**: Conexión teoría-práctica (8.0), rol del estudiante (7.5), coherencia epistemológica (7.0). El modelo Tec21 de retos aplicados genera buena vinculación con la práctica.

- **Áreas de Oportunidad (6.0-6.9)**: Reflexión crítica (6.0). Los estudiantes analizan casos pero raramente cuestionan supuestos o exploran perspectivas alternativas.

- **Debilidades (<6.0)**: Evaluación del aprendizaje (5.75) e integración tecnológica (5.5). El examen representa 70% de la calificación. La tecnología se usa para entregar tareas, no para aprender.

---

## Extractos Representativos

**Dr. Crítico** (Ronda 1):
> "Aunque el currículum aborda aspectos importantes de la estrategia de mercado, parece haber una falta de enfoque en la perspectiva crítica, especialmente en relación con la reproducción de las estructuras de poder y la ideología dominante en el mercado. [...] La estructura del currículum y los objetivos de aprendizaje parecen centrarse principalmente en la visión empresarial y del mercado, sin considerar suficientemente las voces y perspectivas de otros actores sociales."

**Dra. Multiliteracidades** (Ronda 1):
> "Podría profundizarse más en la integración de modos visuales, espaciales, gestuales, auditivos, y táctiles para abordar las diversas necesidades de aprendizaje. [...] La estructura del curso, con sesiones donde el profesor explica contenidos conceptuales, podría sugerir un enfoque transmisionista. Esto podría limitar la agencia del estudiante como diseñador activo de significado."

---

## Recomendaciones del Panel

**Alta prioridad** (unanimidad):
- Diversificar los métodos de evaluación para promover pensamiento crítico
- Mejorar la integración de tecnologías emergentes

**Media prioridad** (mayoría):
- Incorporar perspectiva crítica sobre estructuras de poder
- Fomentar colaboración en red y trabajo en equipo

---

## Limitaciones del Ejercicio

Este ejercicio tiene limitaciones importantes:

- Los modelos de lenguaje **no son expertos reales** con experiencia vivida ni juicio profesional genuino
- Pueden reflejar **sesgos** presentes en sus datos de entrenamiento
- **No sustituyen** una evaluación curricular formal con expertos humanos
- El ejercicio tiene **valor exploratorio y didáctico**, no validez empírica

---

## Acceso a Materiales Completos

**Repositorio GitHub:**
github.com/HesusG/analsisis-del-curriculo-upaep

Incluye:
- Prompts de cada agente
- Transcripción completa de evaluaciones
- Documento final del proyecto (LaTeX)
- Anexos con análisis detallado

---

*Este handout acompaña la presentación del proyecto final para el curso de Análisis del Currículum, UPAEP, Noviembre 2025.*
