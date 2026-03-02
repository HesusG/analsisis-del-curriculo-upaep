"""Generate neobrutalista HTML reports from synthesis results."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from agents import ALL_AGENTS
from agents.synthesizer import SynthesisResult
from config import LLM_MODEL_DISPLAY, OUTPUT_DIR

TEMPLATES_DIR = Path(__file__).parent / "templates"


def generate_report(synthesis: SynthesisResult, pdf_name: str = "planeacion") -> str:
    """Render an HTML report and return its file path."""
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=True,
    )
    template = env.get_template("report.html.j2")

    html = template.render(
        pdf_name=pdf_name,
        synthesis=synthesis,
        agents=ALL_AGENTS,
        llm_model=LLM_MODEL_DISPLAY,
        date=date.today().isoformat(),
    )

    output_path = OUTPUT_DIR / f"reporte_{pdf_name}_{date.today().isoformat()}.html"
    output_path.write_text(html, encoding="utf-8")
    return str(output_path)
