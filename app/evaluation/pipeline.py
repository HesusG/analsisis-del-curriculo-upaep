"""Orchestrates: PDF → text → 3 agents (parallel) → synthesis → HTML report."""

from __future__ import annotations

import asyncio
from pathlib import Path

from agents import ALL_AGENTS
from agents.synthesizer import SynthesisResult, synthesize
from evaluation.pdf_extract import extract_text
from report.generator import generate_report


async def run_evaluation(pdf_path: str | Path) -> tuple[SynthesisResult, str]:
    """Run the full evaluation pipeline.

    Returns:
        (synthesis_result, html_path) — the synthesis and path to the generated HTML.
    """
    # 1. Extract text from PDF
    text = extract_text(pdf_path)

    # 2. Run all agents in parallel
    tasks = {agent.meta.key: agent.evaluate(text) for agent in ALL_AGENTS}
    results = await asyncio.gather(*tasks.values())
    evaluations = dict(zip(tasks.keys(), results))

    # 3. Synthesize
    synthesis = synthesize(evaluations)

    # 4. Generate HTML report
    html_path = generate_report(synthesis, pdf_name=Path(pdf_path).stem)

    return synthesis, html_path
