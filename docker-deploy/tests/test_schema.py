"""Tests for evaluation.schema — null coercion, count_criteria, and parsing."""

import json
import pytest

from evaluation.schema import (
    FullEvaluation,
    SubBloque,
    FaseMejora,
    Parte10Conclusiones,
    ResumenEjecutivo,
    NivelGeneral,
)


# ── Minimal valid FullEvaluation JSON ─────────────────────────────────

def _criterio(cumple=True):
    return {"criterio": "Test", "cumple": cumple, "observacion": "", "evidencia": ""}


def _full_eval_dict(**overrides):
    """Return a minimal FullEvaluation dict; override any top-level key."""
    base = {
        "metadata": {
            "evaluador": "Test",
            "institucion": "UPAEP",
            "responsable_planeacion": "Prof",
            "fecha_evaluacion": "2026-01-01",
        },
        "parte_1_contexto": {
            "diagnostico_institucion": {
                "necesidades": "n",
                "modelo_ensenanza": "m",
                "filosofia": "f",
            },
            "diagnostico_estudiantes": {
                "numero_estudiantes": "30",
                "grupos": "A",
                "niveles_modalidades": "Lic",
            },
            "descripcion_general": "ctx",
        },
        "parte_2_datos_presentacion": {"criterios": [_criterio(True), _criterio(False)]},
        "parte_3_proposito_objetivo": {"criterios": [_criterio(True)], "recomendaciones": ""},
        "parte_4_competencias_aprendizajes": {
            "rubros_encontrados": ["Competencias"],
            "competencias": {"aplica": True, "criterios": [_criterio(True)]},
            "aprendizajes_esperados": {"aplica": False, "criterios": []},
        },
        "parte_5_contenidos": {
            "descripcion_general": "d",
            "tipo_contenido_predominante": "t",
            "criterios": [_criterio(True)],
        },
        "parte_6_secuencia": {
            "descripcion_general": "d",
            "fases_didacticas": {
                "inicio": True,
                "procesamiento": True,
                "reforzamiento": False,
                "sistematizacion_cierre": True,
            },
            "recomendaciones": "",
        },
        "parte_7_metodologia": {
            "descripcion_general": "d",
            "criterios": [_criterio(False)],
        },
        "parte_8_evaluacion": {
            "descripcion_general": "d",
            "tipos_evaluacion": {
                "diagnostica": True,
                "formativa": True,
                "sumativa": False,
            },
            "criterios": [_criterio(True), _criterio(True)],
        },
        "parte_9_recursos": {"descripcion_general": "d", "tipo_recursos": "", "recomendaciones": ""},
        "parte_10_conclusiones": {
            "areas_oportunidad": ["area1"],
            "recomendaciones_redaccion": "r",
            "recomendaciones_innovacion": "i",
            "herramientas_digitales_sugeridas": ["tool1"],
        },
        "parte_11_propuesta_mejora": {
            "fases": [
                {"nombre": "Fase 1", "descripcion": "d", "acciones": ["a1"]},
            ],
        },
        "resumen_ejecutivo": {
            "criterios_cumplidos": 5,
            "criterios_no_cumplidos": 2,
            "porcentaje_cumplimiento": 71.4,
            "nivel_general": "En proceso",
            "fortalezas_principales": ["f1"],
            "areas_criticas": ["c1"],
        },
    }
    base.update(overrides)
    return base


# ── Tests ─────────────────────────────────────────────────────────────


class TestFullEvaluationParsing:
    def test_parse_valid_json(self):
        data = _full_eval_dict()
        ev = FullEvaluation(**data)
        assert ev.metadata.evaluador == "Test"
        assert ev.resumen_ejecutivo.nivel_general == NivelGeneral.EN_PROCESO

    def test_parse_with_null_lists(self):
        """LLM may return null instead of [] — should not crash."""
        data = _full_eval_dict()
        data["parte_4_competencias_aprendizajes"]["rubros_encontrados"] = None
        data["parte_10_conclusiones"]["areas_oportunidad"] = None
        data["parte_10_conclusiones"]["herramientas_digitales_sugeridas"] = None
        data["resumen_ejecutivo"]["fortalezas_principales"] = None
        data["resumen_ejecutivo"]["areas_criticas"] = None
        data["parte_11_propuesta_mejora"]["fases"][0]["acciones"] = None

        ev = FullEvaluation(**data)
        assert ev.parte_4_competencias_aprendizajes.rubros_encontrados == []
        assert ev.parte_10_conclusiones.areas_oportunidad == []
        assert ev.parte_10_conclusiones.herramientas_digitales_sugeridas == []
        assert ev.resumen_ejecutivo.fortalezas_principales == []
        assert ev.resumen_ejecutivo.areas_criticas == []
        assert ev.parte_11_propuesta_mejora.fases[0].acciones == []

    def test_parse_with_empty_lists(self):
        data = _full_eval_dict()
        data["parte_10_conclusiones"]["areas_oportunidad"] = []
        data["resumen_ejecutivo"]["fortalezas_principales"] = []
        ev = FullEvaluation(**data)
        assert ev.parte_10_conclusiones.areas_oportunidad == []
        assert ev.resumen_ejecutivo.fortalezas_principales == []


class TestCountCriteria:
    def test_count_criteria_basic(self):
        ev = FullEvaluation(**_full_eval_dict())
        passed, failed = ev.count_criteria()
        # parte_2: 1p+1f, parte_3: 1p, parte_4 comp: 1p, parte_5: 1p,
        # parte_7: 1f, parte_8: 2p => passed=6, failed=2
        assert passed == 6
        assert failed == 2

    def test_count_criteria_with_null_coerced_subbloque(self):
        data = _full_eval_dict()
        data["parte_4_competencias_aprendizajes"]["competencias"]["criterios"] = None
        ev = FullEvaluation(**data)
        passed, failed = ev.count_criteria()
        # Same minus the 1 passed from competencias => 5 passed, 2 failed
        assert passed == 5
        assert failed == 2


class TestIndividualModels:
    def test_subbloque_null_criterios(self):
        sb = SubBloque(**{"aplica": True, "criterios": None})
        assert sb.criterios == []

    def test_fase_mejora_null_acciones(self):
        fm = FaseMejora(**{"nombre": "F", "descripcion": "D", "acciones": None})
        assert fm.acciones == []

    def test_parte10_null_fields(self):
        p = Parte10Conclusiones(**{
            "areas_oportunidad": None,
            "recomendaciones_redaccion": "r",
            "recomendaciones_innovacion": "i",
            "herramientas_digitales_sugeridas": None,
        })
        assert p.areas_oportunidad == []
        assert p.herramientas_digitales_sugeridas == []

    def test_resumen_ejecutivo_null_fields(self):
        r = ResumenEjecutivo(**{
            "criterios_cumplidos": 5,
            "criterios_no_cumplidos": 2,
            "porcentaje_cumplimiento": 71.4,
            "nivel_general": "En proceso",
            "fortalezas_principales": None,
            "areas_criticas": None,
        })
        assert r.fortalezas_principales == []
        assert r.areas_criticas == []
