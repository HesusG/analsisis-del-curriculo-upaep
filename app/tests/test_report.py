"""Tests for HTML report generation."""

import copy
from unittest.mock import patch

from agents.synthesizer import synthesize
from evaluation.schema import FullEvaluation
from report.generator import generate_report
from tests.conftest import SAMPLE_EVALUATION


def _make_synthesis():
    ev1 = FullEvaluation(**copy.deepcopy(SAMPLE_EVALUATION))
    ev2 = FullEvaluation(**copy.deepcopy(SAMPLE_EVALUATION))
    ev3 = FullEvaluation(**copy.deepcopy(SAMPLE_EVALUATION))
    return synthesize({"pedagogo": ev1, "profesor": ev2, "tecnico": ev3})


class TestReportGenerator:
    def test_generates_valid_html(self, tmp_path):
        synthesis = _make_synthesis()
        with patch("report.generator.OUTPUT_DIR", tmp_path):
            path = generate_report(synthesis, pdf_name="test_plan")

        html = open(path, encoding="utf-8").read()
        assert "<!DOCTYPE html>" in html
        assert "test_plan" in html

    def test_contains_expert_panels(self, tmp_path):
        synthesis = _make_synthesis()
        with patch("report.generator.OUTPUT_DIR", tmp_path):
            path = generate_report(synthesis, pdf_name="test")

        html = open(path, encoding="utf-8").read()
        assert "expert-panel" in html
        assert "Pedagogo" in html
        assert "Profesor" in html

    def test_contains_criteria_tables(self, tmp_path):
        synthesis = _make_synthesis()
        with patch("report.generator.OUTPUT_DIR", tmp_path):
            path = generate_report(synthesis, pdf_name="test")

        html = open(path, encoding="utf-8").read()
        assert "criteria-table" in html
        assert "criteria-pass" in html or "criteria-fail" in html

    def test_contains_synthesis_section(self, tmp_path):
        synthesis = _make_synthesis()
        with patch("report.generator.OUTPUT_DIR", tmp_path):
            path = generate_report(synthesis, pdf_name="test")

        html = open(path, encoding="utf-8").read()
        assert "Consensos" in html
        assert "Prescripciones Unificadas" in html

    def test_contains_summary(self, tmp_path):
        synthesis = _make_synthesis()
        with patch("report.generator.OUTPUT_DIR", tmp_path):
            path = generate_report(synthesis, pdf_name="test")

        html = open(path, encoding="utf-8").read()
        assert "Resumen Ejecutivo" in html
        assert "Fortalezas" in html
        assert "compliance-bar" in html
