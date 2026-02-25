"""Tests for Pydantic evaluation schema."""

import copy

import pytest
from pydantic import ValidationError

from evaluation.schema import FullEvaluation, NivelGeneral


class TestFullEvaluationParsing:
    def test_valid_json_parses(self, sample_eval_dict):
        ev = FullEvaluation(**sample_eval_dict)
        assert ev.metadata.evaluador == "Pedagogo"
        assert ev.resumen_ejecutivo.nivel_general == NivelGeneral.EN_PROCESO

    def test_count_criteria(self, sample_eval_dict):
        ev = FullEvaluation(**sample_eval_dict)
        passed, failed = ev.count_criteria()
        # 5+4+3+5+4+6+2 = 29 criteria across parts 2-8 (incl. sub-blocks)
        assert passed + failed == 29
        assert passed == 21
        assert failed == 8

    def test_missing_metadata_rejects(self, sample_eval_dict):
        data = copy.deepcopy(sample_eval_dict)
        del data["metadata"]
        with pytest.raises(ValidationError):
            FullEvaluation(**data)

    def test_invalid_nivel_rejects(self, sample_eval_dict):
        data = copy.deepcopy(sample_eval_dict)
        data["resumen_ejecutivo"]["nivel_general"] = "Excelente"
        with pytest.raises(ValidationError):
            FullEvaluation(**data)

    def test_empty_actions_rejects(self, sample_eval_dict):
        data = copy.deepcopy(sample_eval_dict)
        data["parte_11_propuesta_mejora"]["fases"][0]["acciones"] = []
        with pytest.raises(ValidationError):
            FullEvaluation(**data)

    def test_cumple_as_string_rejects(self, sample_eval_dict):
        data = copy.deepcopy(sample_eval_dict)
        data["parte_2_datos_presentacion"]["criterios"][0]["cumple"] = "Sí"
        with pytest.raises(ValidationError):
            FullEvaluation(**data)
