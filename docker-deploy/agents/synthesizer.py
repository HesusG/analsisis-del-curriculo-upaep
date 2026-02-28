"""Pure-Python synthesizer: merges 3 FullEvaluation results into consensus."""

from __future__ import annotations

from dataclasses import dataclass, field

from evaluation.schema import FullEvaluation, NivelGeneral


@dataclass
class CriterionResult:
    criterio: str
    parte: str
    votes: dict[str, bool] = field(default_factory=dict)
    observations: dict[str, str] = field(default_factory=dict)


@dataclass
class Prescription:
    """A structured recommendation with source tracking."""
    text: str
    source_agents: list[str] = field(default_factory=list)
    source_part: str = ""

    @property
    def consensus_count(self) -> int:
        return len(self.source_agents)

    @property
    def priority(self) -> str:
        n = self.consensus_count
        if n >= 3:
            return "Alta"
        elif n >= 2:
            return "Media"
        return "Individual"


@dataclass
class SynthesisResult:
    """Output of the synthesis: consensus, dissent, and averages."""
    average_compliance: float
    nivel_general: NivelGeneral
    consensus: list[CriterionResult]  # all agree
    dissent: list[CriterionResult]    # disagree
    prescriptions: list[str]          # deduplicated (kept for backward compat)
    strengths: list[str]              # deduplicated
    critical_areas: list[str]         # deduplicated
    per_agent: dict[str, FullEvaluation]
    structured_prescriptions: list[Prescription] = field(default_factory=list)


def _normalize(text: str) -> str:
    """Normalize text for fuzzy deduplication."""
    return " ".join(text.lower().strip().split())


def synthesize(evaluations: dict[str, FullEvaluation]) -> SynthesisResult:
    """Merge evaluations from multiple agents.

    Args:
        evaluations: mapping of agent_key → FullEvaluation
    """
    # ── Collect all criteria across parts 2-8 ──
    criteria_map: dict[str, CriterionResult] = {}

    parts_with_criterios = [
        ("parte_2", "parte_2_datos_presentacion"),
        ("parte_3", "parte_3_proposito_objetivo"),
        ("parte_5", "parte_5_contenidos"),
        ("parte_7", "parte_7_metodologia"),
        ("parte_8", "parte_8_evaluacion"),
    ]

    for agent_key, ev in evaluations.items():
        # Standard parts with .criterios
        for label, attr in parts_with_criterios:
            part = getattr(ev, attr)
            for c in part.criterios:
                key = f"{label}::{c.criterio}"
                if key not in criteria_map:
                    criteria_map[key] = CriterionResult(criterio=c.criterio, parte=label)
                criteria_map[key].votes[agent_key] = c.cumple
                if c.observacion:
                    criteria_map[key].observations[agent_key] = c.observacion

        # parte_4 sub-blocks
        p4 = ev.parte_4_competencias_aprendizajes
        for sub_name, sub in [("competencias", p4.competencias), ("aprendizajes", p4.aprendizajes_esperados)]:
            if sub.aplica:
                for c in sub.criterios:
                    key = f"parte_4_{sub_name}::{c.criterio}"
                    if key not in criteria_map:
                        criteria_map[key] = CriterionResult(criterio=c.criterio, parte=f"parte_4_{sub_name}")
                    criteria_map[key].votes[agent_key] = c.cumple
                    if c.observacion:
                        criteria_map[key].observations[agent_key] = c.observacion

    # ── Classify consensus vs dissent ──
    consensus = []
    dissent = []
    for cr in criteria_map.values():
        votes = set(cr.votes.values())
        if len(votes) == 1:
            consensus.append(cr)
        else:
            dissent.append(cr)

    # ── Average compliance ──
    percentages = [ev.resumen_ejecutivo.porcentaje_cumplimiento for ev in evaluations.values()]
    avg = round(sum(percentages) / len(percentages), 1) if percentages else 0.0

    if avg >= 80:
        nivel = NivelGeneral.SATISFACTORIO
    elif avg >= 60:
        nivel = NivelGeneral.EN_PROCESO
    else:
        nivel = NivelGeneral.REQUIERE_ATENCION

    # ── Build structured prescriptions with source tracking ──
    prescription_map: dict[str, Prescription] = {}

    for agent_key, ev in evaluations.items():
        # Recommendations from parts 3, 6, 9
        for part_attr, part_label in [
            ("parte_3_proposito_objetivo", "Propósito/Objetivo"),
            ("parte_6_secuencia", "Secuencia Didáctica"),
            ("parte_9_recursos", "Recursos"),
        ]:
            rec = getattr(ev, part_attr).recomendaciones
            if rec and rec.strip():
                norm = _normalize(rec)
                if norm not in prescription_map:
                    prescription_map[norm] = Prescription(text=rec, source_part=part_label)
                if agent_key not in prescription_map[norm].source_agents:
                    prescription_map[norm].source_agents.append(agent_key)

        # Actions from improvement proposal
        for fase in ev.parte_11_propuesta_mejora.fases:
            for accion in fase.acciones:
                if accion and accion.strip():
                    norm = _normalize(accion)
                    if norm not in prescription_map:
                        prescription_map[norm] = Prescription(text=accion, source_part=fase.nombre)
                    if agent_key not in prescription_map[norm].source_agents:
                        prescription_map[norm].source_agents.append(agent_key)

    # Sort by consensus count (highest first)
    structured = sorted(prescription_map.values(), key=lambda p: (-p.consensus_count, p.text))

    # Flat prescriptions for backward compatibility
    prescriptions = [p.text for p in structured]

    # ── Deduplicate strengths and critical areas ──
    all_strengths: list[str] = []
    all_critical: list[str] = []
    for ev in evaluations.values():
        all_strengths.extend(ev.resumen_ejecutivo.fortalezas_principales)
        all_critical.extend(ev.resumen_ejecutivo.areas_criticas)
    strengths = list(dict.fromkeys(all_strengths))
    critical_areas = list(dict.fromkeys(all_critical))

    return SynthesisResult(
        average_compliance=avg,
        nivel_general=nivel,
        consensus=consensus,
        dissent=dissent,
        prescriptions=prescriptions,
        strengths=strengths,
        critical_areas=critical_areas,
        per_agent=evaluations,
        structured_prescriptions=structured,
    )
