"""Shared test fixtures."""

import json

import pytest


def _make_criterio(name: str, cumple: bool = True) -> dict:
    return {"criterio": name, "cumple": cumple, "observacion": "" if cumple else f"{name} no cumple"}


SAMPLE_EVALUATION = {
    "metadata": {
        "evaluador": "Pedagogo",
        "institucion": "Tec de Monterrey",
        "responsable_planeacion": "Juan Pérez",
        "fecha_evaluacion": "2025-11-01",
    },
    "parte_1_contexto": {
        "diagnostico_institucion": {
            "necesidades": "Fortalecer competencias digitales",
            "modelo_ensenanza": "Tec21",
            "filosofia": "Humanismo cristiano",
        },
        "diagnostico_estudiantes": {
            "numero_estudiantes": "35",
            "grupos": "1",
            "niveles_modalidades": "Licenciatura presencial",
        },
        "descripcion_general": "Curso de primer semestre de ingeniería.",
    },
    "parte_2_datos_presentacion": {
        "criterios": [
            _make_criterio("Nombre de la institución"),
            _make_criterio("Año lectivo"),
            _make_criterio("Responsable de la asignatura"),
            _make_criterio("Nombre de asignatura, grado, grupo y clave"),
            _make_criterio("Otros datos de presentación", False),
        ]
    },
    "parte_3_proposito_objetivo": {
        "criterios": [
            _make_criterio("Redacción: qué, cómo y para qué"),
            _make_criterio("Claro y preciso en lo que pretende lograr"),
            _make_criterio("Alcanzable en el tiempo del curso", False),
            _make_criterio("Observable y evaluable"),
        ],
        "recomendaciones": "Ajustar el alcance temporal.",
    },
    "parte_4_competencias_aprendizajes": {
        "rubros_encontrados": ["Competencias", "Aprendizajes Esperados"],
        "competencias": {
            "aplica": True,
            "criterios": [
                _make_criterio("Estructura: verbo de desempeño + contenido + finalidad + condición"),
                _make_criterio("Clara y concisa", False),
                _make_criterio("Observable y evaluable"),
            ],
        },
        "aprendizajes_esperados": {
            "aplica": True,
            "criterios": [
                _make_criterio("Claridad sobre lo que se espera del estudiante"),
                _make_criterio("Favorece la autonomía", False),
                _make_criterio("Expresa conocimientos, habilidades y/o actitudes"),
                _make_criterio("Precisión en el verbo"),
                _make_criterio("Relevante, claro y evaluable"),
            ],
        },
    },
    "parte_5_contenidos": {
        "descripcion_general": "Contenidos conceptuales y procedimentales.",
        "tipo_contenido_predominante": "Conceptual",
        "criterios": [
            _make_criterio("Relación con la asignatura"),
            _make_criterio("Aportan al logro del propósito"),
            _make_criterio("Favorecen teoría y práctica", False),
            _make_criterio("Adecuados al nivel de los estudiantes"),
        ],
    },
    "parte_6_secuencia": {
        "descripcion_general": "Secuencia en 4 fases.",
        "fases_didacticas": {
            "inicio": True,
            "procesamiento": True,
            "reforzamiento": False,
            "sistematizacion_cierre": True,
        },
        "recomendaciones": "Incluir fase de reforzamiento.",
    },
    "parte_7_metodologia": {
        "descripcion_general": "ABP y aprendizaje colaborativo.",
        "criterios": [
            _make_criterio("Estrategias de enseñanza especifican rol del docente"),
            _make_criterio("Estrategias de aprendizaje especifican rol del estudiante"),
            _make_criterio("Estrategias claras", False),
            _make_criterio("Adecuadas a necesidades, ritmos y estilos de aprendizaje"),
            _make_criterio("Innovadoras y no repetitivas", False),
            _make_criterio("Seleccionadas en función del estudiante, contenido y aprendizaje esperado"),
        ],
    },
    "parte_8_evaluacion": {
        "descripcion_general": "Evaluación diagnóstica y sumativa.",
        "tipos_evaluacion": {
            "diagnostica": True,
            "formativa": False,
            "sumativa": True,
        },
        "criterios": [
            _make_criterio("Coherente con las estrategias de enseñanza-aprendizaje"),
            _make_criterio("Ponderación equilibrada (no solo memorística, también procedimental)", False),
        ],
    },
    "parte_9_recursos": {
        "descripcion_general": "Proyector, laptop, plataforma Canvas.",
        "tipo_recursos": "Aula + digitales",
        "recomendaciones": "Integrar recursos OER.",
    },
    "parte_10_conclusiones": {
        "areas_oportunidad": ["Fortalecer evaluación formativa", "Diversificar estrategias"],
        "recomendaciones_redaccion": "Mejorar redacción de competencias.",
        "recomendaciones_innovacion": "Incorporar gamificación.",
        "herramientas_digitales_sugeridas": ["Kahoot", "Padlet"],
    },
    "parte_11_propuesta_mejora": {
        "fases": [
            {
                "nombre": "Diagnóstico",
                "descripcion": "Evaluar estado actual",
                "acciones": ["Encuesta a estudiantes", "Revisión de resultados"],
            },
            {
                "nombre": "Implementación",
                "descripcion": "Aplicar mejoras",
                "acciones": ["Rediseñar secuencia", "Capacitar docente"],
            },
        ]
    },
    "resumen_ejecutivo": {
        "criterios_cumplidos": 18,
        "criterios_no_cumplidos": 7,
        "porcentaje_cumplimiento": 72.0,
        "nivel_general": "En proceso",
        "fortalezas_principales": ["Diagnóstico institucional completo", "Propósito bien definido"],
        "areas_criticas": ["Evaluación formativa ausente", "Competencias poco claras"],
    },
}


@pytest.fixture
def sample_eval_dict() -> dict:
    """Return a complete sample evaluation dictionary."""
    return json.loads(json.dumps(SAMPLE_EVALUATION))


@pytest.fixture
def sample_eval_json() -> str:
    """Return sample evaluation as JSON string."""
    return json.dumps(SAMPLE_EVALUATION, ensure_ascii=False)
