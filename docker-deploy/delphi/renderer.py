"""Render Delphi HTML tabs using Jinja2 templates."""

from __future__ import annotations

from pathlib import Path

import markdown
from jinja2 import Environment, FileSystemLoader

from config import AGENT_PROMPTS_DIR, RULES_PATH
from .loader import DelphiData

TEMPLATES_DIR = Path(__file__).parent / "templates"

_MD = markdown.Markdown(extensions=["tables", "fenced_code"])


def _md_to_html(text: str) -> str:
    _MD.reset()
    return _MD.convert(text)


def _get_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=True,
    )


def render_delphi_summary(data: DelphiData) -> str:
    """Render the Delphi Summary tab HTML."""
    env = _get_env()
    tpl = env.get_template("delphi_summary.html.j2")
    return tpl.render(data=data)


def render_delphi_detail(data: DelphiData) -> str:
    """Render the Delphi Detail tab HTML."""
    env = _get_env()
    tpl = env.get_template("delphi_detail.html.j2")
    return tpl.render(data=data)


def render_metodologia(data: DelphiData) -> str:
    """Render the Methodology tab HTML with app evaluator prompts + rules."""
    env = _get_env()
    tpl = env.get_template("metodologia.html.j2")

    # Load app evaluator prompts
    evaluator_prompts = []
    for md_file in sorted(AGENT_PROMPTS_DIR.glob("evaluador-*.md")):
        name = md_file.stem.replace("evaluador-", "").title()
        html = _md_to_html(md_file.read_text(encoding="utf-8"))
        evaluator_prompts.append((f"Evaluador: {name}", html))

    # Load rules.md
    rules_html = _md_to_html(RULES_PATH.read_text(encoding="utf-8"))

    return tpl.render(data=data, evaluator_prompts=evaluator_prompts, rules_html=rules_html)
