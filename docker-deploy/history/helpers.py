"""Extract per-agent summary dicts from evaluation results."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agents.synthesizer import SynthesisResult
    from delphi.live_pipeline import DelphiResult


def summarize_3expert(synthesis: SynthesisResult) -> dict[str, str]:
    """Return {agent_display_name: 'XX.X%'} for each expert."""
    summary = {}
    for _key, ev in synthesis.per_agent.items():
        name = ev.metadata.evaluador
        pct = ev.resumen_ejecutivo.porcentaje_cumplimiento
        summary[name] = f"{pct:.1f}%"
    return summary


def summarize_delphi(result: DelphiResult) -> dict[str, str]:
    """Return {expert_name: 'X.X/10'} for each Delphi expert."""
    summary = {}
    for key, ev in result.expert_evaluations.items():
        meta = result.expert_metas.get(key)
        name = meta.name if meta else key
        scores = [p.score for p in ev.puntuaciones]
        avg = sum(scores) / len(scores) if scores else 0.0
        summary[name] = f"{avg:.1f}/10"
    return summary
