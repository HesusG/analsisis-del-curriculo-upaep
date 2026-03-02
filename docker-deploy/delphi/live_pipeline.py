"""Orchestrates: PDF -> 5 Delphi experts (parallel) -> moderator -> HTML report."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from config import LLM_MODEL_DISPLAY, OUTPUT_DIR
from delphi.live_agents import (
    DELPHI_EXPERTS,
    DelphiExpertAgent,
    DelphiExpertMeta,
    DelphiModeratorAgent,
)
from delphi.live_schema import DelphiExpertEvaluation, DelphiSynthesis
from evaluation.pdf_extract import extract_text

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "report" / "templates"


@dataclass
class DelphiResult:
    """Full result of a live Delphi evaluation."""
    expert_evaluations: dict[str, DelphiExpertEvaluation] = field(default_factory=dict)
    expert_metas: dict[str, DelphiExpertMeta] = field(default_factory=dict)
    synthesis: DelphiSynthesis | None = None
    html_path: str = ""
    pdf_name: str = ""


async def run_delphi_evaluation(pdf_path: str | Path) -> DelphiResult:
    """Run 5 expert evaluations in parallel, then moderator synthesis."""
    text = extract_text(pdf_path)
    pdf_name = Path(pdf_path).stem

    # Run 5 experts in parallel
    agents = {meta.key: DelphiExpertAgent(meta) for meta in DELPHI_EXPERTS}
    tasks = {key: agent.evaluate(text) for key, agent in agents.items()}
    results = await asyncio.gather(*tasks.values())
    expert_evaluations = dict(zip(tasks.keys(), results))
    expert_metas = {meta.key: meta for meta in DELPHI_EXPERTS}

    # Moderator synthesis
    moderator = DelphiModeratorAgent()
    synthesis = await moderator.synthesize(text, expert_evaluations)

    # Generate HTML report
    html_path = _generate_delphi_report(
        expert_evaluations=expert_evaluations,
        expert_metas=expert_metas,
        synthesis=synthesis,
        pdf_name=pdf_name,
    )

    return DelphiResult(
        expert_evaluations=expert_evaluations,
        expert_metas=expert_metas,
        synthesis=synthesis,
        html_path=html_path,
        pdf_name=pdf_name,
    )


def _generate_delphi_report(
    expert_evaluations: dict[str, DelphiExpertEvaluation],
    expert_metas: dict[str, DelphiExpertMeta],
    synthesis: DelphiSynthesis,
    pdf_name: str,
) -> str:
    """Render the Delphi HTML report and return its file path."""
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=True,
    )
    template = env.get_template("delphi_report.html.j2")

    # Compute average score across all experts and dimensions
    all_scores = []
    for ev in expert_evaluations.values():
        for p in ev.puntuaciones:
            all_scores.append(p.score)
    avg_score = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0.0

    # Per-expert average
    expert_averages = {}
    for key, ev in expert_evaluations.items():
        scores = [p.score for p in ev.puntuaciones]
        expert_averages[key] = round(sum(scores) / len(scores), 1) if scores else 0.0

    html = template.render(
        pdf_name=pdf_name,
        expert_evaluations=expert_evaluations,
        expert_metas=expert_metas,
        synthesis=synthesis,
        avg_score=avg_score,
        expert_averages=expert_averages,
        llm_model=LLM_MODEL_DISPLAY,
        date=date.today().isoformat(),
    )

    output_path = OUTPUT_DIR / f"delphi_{pdf_name}_{date.today().isoformat()}.html"
    output_path.write_text(html, encoding="utf-8")
    return str(output_path)
