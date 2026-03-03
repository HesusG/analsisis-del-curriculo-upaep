"""Pedagogo evaluator agent."""

from .base import AgentMeta, EvaluatorAgent

pedagogo_agent = EvaluatorAgent(
    meta=AgentMeta(
        key="pedagogo",
        name="Dra. Lina Campos",
        color="#E57373",
        emoji="\U0001F50D",
        description="Verifica la presencia y completitud de cada elemento requerido",
    ),
    prompt_filename="evaluador-pedagogo.md",
)
