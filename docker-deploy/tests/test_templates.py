"""Tests for Jinja2 templates — rendering without errors + no '3 expertos'."""

import subprocess
from pathlib import Path

import pytest
from jinja2 import Environment, FileSystemLoader


DOCKER_DEPLOY = Path(__file__).resolve().parent.parent


# ── Helpers ───────────────────────────────────────────────────────────

def _get_env(template_dir: Path):
    return Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=True,
    )


# ── Mock objects that quack like the real dataclasses ─────────────────

class _Obj:
    """Generic object that accepts arbitrary kwargs as attributes."""
    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)

    def __getitem__(self, key):
        return getattr(self, key)

    def get(self, key, default=None):
        return getattr(self, key, default)


def _mock_criterio(cumple=True):
    return _Obj(criterio="Test criterio", cumple=cumple, observacion="obs", evidencia="ev")


def _mock_sub_bloque(aplica=True, n=1):
    return _Obj(aplica=aplica, criterios=[_mock_criterio()] * n)


class _MockNivelGeneral:
    def __init__(self, val):
        self.value = val


def _mock_full_evaluation():
    return _Obj(
        metadata=_Obj(evaluador="GPT-4o (Pedagogo)", institucion="UPAEP",
                       responsable_planeacion="Prof", fecha_evaluacion="2026-01-01"),
        parte_2_datos_presentacion=_Obj(criterios=[_mock_criterio(True), _mock_criterio(False)]),
        parte_3_proposito_objetivo=_Obj(criterios=[_mock_criterio()], recomendaciones=""),
        parte_4_competencias_aprendizajes=_Obj(
            rubros_encontrados=["Competencias"],
            competencias=_mock_sub_bloque(aplica=True),
            aprendizajes_esperados=_mock_sub_bloque(aplica=False, n=0),
        ),
        parte_5_contenidos=_Obj(criterios=[_mock_criterio()]),
        parte_7_metodologia=_Obj(criterios=[_mock_criterio(False)]),
        parte_8_evaluacion=_Obj(criterios=[_mock_criterio()]),
        parte_11_propuesta_mejora=_Obj(fases=[
            _Obj(nombre="Fase 1", descripcion="desc", acciones=["accion1"]),
        ]),
        resumen_ejecutivo=_Obj(porcentaje_cumplimiento=75.0),
    )


def _mock_agent_meta(name="Pedagogo", key="pedagogo"):
    return _Obj(name=name, key=key, color="#E57373", emoji="📚", description="Desc")


def _mock_agent(name="Pedagogo", key="pedagogo"):
    return _Obj(meta=_mock_agent_meta(name, key))


def _mock_criterion_result(criterio="Test", passed=True):
    votes = {"pedagogo": passed, "profesor": passed, "tecnico": passed}
    return _Obj(criterio=criterio, votes=votes)


def _mock_prescription(text="Mejorar X", count=3, part="Metodología"):
    return _Obj(text=text, consensus_count=count, source_part=part, priority="Alta")


def _mock_synthesis():
    agents = [_mock_agent("Pedagogo", "pedagogo"), _mock_agent("Profesor", "profesor"), _mock_agent("Tecnico", "tecnico")]
    ev = _mock_full_evaluation()
    return _Obj(
        average_compliance=75.0,
        nivel_general=_MockNivelGeneral("En proceso"),
        per_agent={"pedagogo": ev, "profesor": ev, "tecnico": ev},
        consensus=[_mock_criterion_result("C1", True)],
        dissent=[_mock_criterion_result("C2", False)],
        strengths=["Buena estructura"],
        critical_areas=["Falta innovacion"],
        structured_prescriptions=[_mock_prescription()],
    ), agents


# ── report.html.j2 ───────────────────────────────────────────────────

class TestReportTemplate:
    def test_renders_without_error(self):
        env = _get_env(DOCKER_DEPLOY / "report" / "templates")
        tpl = env.get_template("report.html.j2")
        synthesis, agents = _mock_synthesis()

        html = tpl.render(
            pdf_name="test.pdf",
            synthesis=synthesis,
            agents=agents,
            llm_model="gpt-4o",
            date="2026-01-01",
        )
        assert "Evaluador Curricular UPAEP" in html
        assert "75.0%" in html

    def test_agent_count_is_dynamic(self):
        """The template uses {{ agents|length }}, not hardcoded '3'."""
        env = _get_env(DOCKER_DEPLOY / "report" / "templates")
        tpl = env.get_template("report.html.j2")
        # Use 2 agents to prove the count is dynamic
        agents = [_mock_agent("Pedagogo", "pedagogo"), _mock_agent("Profesor", "profesor")]
        ev = _mock_full_evaluation()
        synthesis = _Obj(
            average_compliance=75.0,
            nivel_general=_MockNivelGeneral("En proceso"),
            per_agent={"pedagogo": ev, "profesor": ev},
            consensus=[_mock_criterion_result("C1", True)],
            dissent=[],
            strengths=["Buena estructura"],
            critical_areas=["Falta innovacion"],
            structured_prescriptions=[_mock_prescription()],
        )
        html = tpl.render(
            pdf_name="test.pdf",
            synthesis=synthesis,
            agents=agents,
            llm_model="gpt-4o",
            date="2026-01-01",
        )
        assert "2 expertos" in html
        # Hardcoded "3 expertos" should NOT appear with 2 agents
        assert "3 expertos" not in html


# ── delphi_report.html.j2 ────────────────────────────────────────────

def _mock_dim_score(dim="Coherencia", score=7):
    return _Obj(dimension=dim, score=score, justificacion="Just")


def _mock_delphi_expert_eval():
    dims = ["Coherencia", "Rol", "Integracion", "Reflexion", "Conexion", "Evaluacion"]
    return _Obj(
        fortalezas=["f1"],
        debilidades=["d1"],
        puntuaciones=[_mock_dim_score(d, 7) for d in dims],
        recomendaciones=["r1"],
    )


def _mock_delphi_synthesis():
    dims = ["Coherencia", "Rol", "Integracion", "Reflexion", "Conexion", "Evaluacion"]
    return _Obj(
        consensos=["c1"],
        disensos=[_Obj(tema="T", posiciones={"critico": "pos1", "conectivista": "pos2"})],
        puntuaciones_consolidadas=[_mock_dim_score(d, 6) for d in dims],
        recomendaciones_priorizadas=[
            _Obj(texto="rec", prioridad="Alta", expertos=["critico", "conectivista"]),
        ],
        fortalezas=["f1"],
        areas_criticas=["a1"],
    )


class TestDelphiReportTemplate:
    def test_renders_without_error(self):
        env = _get_env(DOCKER_DEPLOY / "report" / "templates")
        tpl = env.get_template("delphi_report.html.j2")

        metas = {
            "critico": _Obj(name="Dr. Critico", color="#E57373", emoji="🔍", marco="Socio-critico"),
            "conectivista": _Obj(name="Dr. Conectivista", color="#64B5F6", emoji="🌐", marco="Conectivismo"),
        }
        evals = {
            "critico": _mock_delphi_expert_eval(),
            "conectivista": _mock_delphi_expert_eval(),
        }

        html = tpl.render(
            pdf_name="test.pdf",
            expert_evaluations=evals,
            expert_metas=metas,
            expert_averages={"critico": 7.0, "conectivista": 7.0},
            synthesis=_mock_delphi_synthesis(),
            avg_score=7.0,
            llm_model="gpt-4o",
            date="2026-01-01",
        )
        assert "Panel de Expertos IA" in html or "PANEL DE EXPERTOS IA" in html
        assert "3 expertos" not in html


# ── metodologia.html.j2 ──────────────────────────────────────────────

class TestMetodologiaTemplate:
    def test_renders_without_error(self):
        env = _get_env(DOCKER_DEPLOY / "delphi" / "templates")
        tpl = env.get_template("metodologia.html.j2")

        html = tpl.render(
            evaluator_prompts=[("Evaluador: Pedagogo", "<p>Prompt text</p>")],
            rules_html="<p>Rules</p>",
        )
        assert "Como Funciona el Evaluador" in html

    def test_no_3_expertos_in_output(self):
        env = _get_env(DOCKER_DEPLOY / "delphi" / "templates")
        tpl = env.get_template("metodologia.html.j2")

        html = tpl.render(
            evaluator_prompts=[("Evaluador: Pedagogo", "<p>Prompt</p>")],
            rules_html="<p>Rules</p>",
        )
        assert "3 expertos" not in html


# ── Global grep check ────────────────────────────────────────────────

class TestNo3ExpertosAnywhere:
    def test_grep_no_3_expertos_in_source_files(self):
        """Ensure hardcoded '3 expertos' does not appear in source files."""
        result = subprocess.run(
            ["grep", "-r", "--include=*.py", "--include=*.j2",
             "--include=*.html", "--exclude-dir=tests",
             "3 expertos", str(DOCKER_DEPLOY)],
            capture_output=True, text=True,
        )
        assert result.stdout.strip() == "", (
            f"Found '3 expertos' in:\n{result.stdout}"
        )
