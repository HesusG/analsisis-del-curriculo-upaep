"""Tests for delphi.live_schema — parsing typical LLM JSON output."""

import pytest

from delphi.live_schema import (
    DelphiExpertEvaluation,
    DelphiSynthesis,
    DimensionScore,
    DisensoItem,
    PrioritizedRecommendation,
    DIMENSIONS,
)


def _dim_score(dim="Coherencia epistemológica", score=7):
    return {"dimension": dim, "score": score, "justificacion": "Justificacion test"}


def _expert_eval_dict(**overrides):
    base = {
        "fortalezas": ["Buena estructura general"],
        "debilidades": ["Falta reflexion critica"],
        "puntuaciones": [_dim_score(d, 7) for d in DIMENSIONS],
        "recomendaciones": ["Integrar mas tecnologia"],
    }
    base.update(overrides)
    return base


def _synthesis_dict(**overrides):
    base = {
        "consensos": ["Todos coinciden en buena estructura"],
        "disensos": [
            {
                "tema": "Nivel de tecnologia",
                "posiciones": {
                    "critico": "Insuficiente",
                    "conectivista": "Adecuado",
                },
            }
        ],
        "puntuaciones_consolidadas": [_dim_score(d, 6) for d in DIMENSIONS],
        "recomendaciones_priorizadas": [
            {
                "texto": "Agregar herramientas digitales",
                "prioridad": "Alta",
                "expertos": ["critico", "conectivista", "multiliteracidades"],
            },
        ],
        "fortalezas": ["Estructura clara"],
        "areas_criticas": ["Falta innovacion"],
    }
    base.update(overrides)
    return base


class TestDelphiExpertEvaluation:
    def test_parse_typical_json(self):
        ev = DelphiExpertEvaluation(**_expert_eval_dict())
        assert len(ev.puntuaciones) == 6
        assert ev.fortalezas[0] == "Buena estructura general"
        assert ev.recomendaciones[0] == "Integrar mas tecnologia"

    def test_scores_in_range(self):
        ev = DelphiExpertEvaluation(**_expert_eval_dict())
        for p in ev.puntuaciones:
            assert 1 <= p.score <= 10

    def test_score_below_range_fails(self):
        data = _expert_eval_dict()
        data["puntuaciones"][0]["score"] = 0
        with pytest.raises(Exception):
            DelphiExpertEvaluation(**data)

    def test_score_above_range_fails(self):
        data = _expert_eval_dict()
        data["puntuaciones"][0]["score"] = 11
        with pytest.raises(Exception):
            DelphiExpertEvaluation(**data)


class TestDelphiSynthesis:
    def test_parse_typical_json(self):
        syn = DelphiSynthesis(**_synthesis_dict())
        assert len(syn.consensos) == 1
        assert len(syn.disensos) == 1
        assert len(syn.puntuaciones_consolidadas) == 6
        assert syn.recomendaciones_priorizadas[0].prioridad == "Alta"

    def test_disenso_positions(self):
        syn = DelphiSynthesis(**_synthesis_dict())
        d = syn.disensos[0]
        assert d.tema == "Nivel de tecnologia"
        assert "critico" in d.posiciones
        assert "conectivista" in d.posiciones

    def test_prioritized_recommendations(self):
        syn = DelphiSynthesis(**_synthesis_dict())
        rec = syn.recomendaciones_priorizadas[0]
        assert rec.prioridad == "Alta"
        assert len(rec.expertos) == 3
