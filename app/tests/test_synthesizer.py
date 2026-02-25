"""Tests for the pure-Python synthesizer."""

import copy

from agents.synthesizer import synthesize
from evaluation.schema import FullEvaluation, NivelGeneral
from tests.conftest import SAMPLE_EVALUATION


def _make_eval(**overrides) -> FullEvaluation:
    data = copy.deepcopy(SAMPLE_EVALUATION)
    for key, value in overrides.items():
        keys = key.split(".")
        d = data
        for k in keys[:-1]:
            d = d[k]
        d[keys[-1]] = value
    return FullEvaluation(**data)


class TestSynthesize:
    def test_three_identical_evals_all_consensus(self):
        ev = _make_eval(**{"metadata.evaluador": "Agent A"})
        result = synthesize({"a": ev, "b": ev, "c": ev})
        assert len(result.dissent) == 0
        assert len(result.consensus) > 0

    def test_average_compliance(self):
        ev1 = _make_eval(**{"resumen_ejecutivo.porcentaje_cumplimiento": 80.0})
        ev2 = _make_eval(**{"resumen_ejecutivo.porcentaje_cumplimiento": 60.0})
        ev3 = _make_eval(**{"resumen_ejecutivo.porcentaje_cumplimiento": 70.0})
        result = synthesize({"a": ev1, "b": ev2, "c": ev3})
        assert result.average_compliance == 70.0
        assert result.nivel_general == NivelGeneral.EN_PROCESO

    def test_dissent_when_agents_disagree(self):
        ev1 = _make_eval()
        ev2 = copy.deepcopy(SAMPLE_EVALUATION)
        # Flip one criterion
        ev2["parte_2_datos_presentacion"]["criterios"][0]["cumple"] = False
        ev2["parte_2_datos_presentacion"]["criterios"][0]["observacion"] = "Discrepo"
        ev2_parsed = FullEvaluation(**ev2)

        result = synthesize({"a": ev1, "b": ev2_parsed})
        assert len(result.dissent) >= 1
        dissent_names = [d.criterio for d in result.dissent]
        assert "Nombre de la institución" in dissent_names

    def test_prescriptions_deduplicated(self):
        ev = _make_eval()
        result = synthesize({"a": ev, "b": ev})
        # Same evals → prescriptions should be deduplicated
        assert len(result.prescriptions) == len(set(result.prescriptions))

    def test_nivel_satisfactorio(self):
        ev = _make_eval(**{"resumen_ejecutivo.porcentaje_cumplimiento": 90.0})
        result = synthesize({"a": ev})
        assert result.nivel_general == NivelGeneral.SATISFACTORIO

    def test_nivel_requiere_atencion(self):
        ev = _make_eval(**{"resumen_ejecutivo.porcentaje_cumplimiento": 50.0})
        result = synthesize({"a": ev})
        assert result.nivel_general == NivelGeneral.REQUIERE_ATENCION
