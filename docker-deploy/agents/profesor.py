"""Profesor evaluator agent."""

from .base import AgentMeta, EvaluatorAgent

profesor_agent = EvaluatorAgent(
    meta=AgentMeta(
        key="profesor",
        name="Dr. Marco Fuentes",
        color="#64B5F6",
        emoji="\U0001F3AF",
        description="Evalúa la calidad pedagógica y el diseño didáctico de cada elemento",
    ),
    prompt_filename="evaluador-profesor.md",
)
