"""Pedagogo evaluator agent."""

from .base import AgentMeta, EvaluatorAgent

pedagogo_agent = EvaluatorAgent(
    meta=AgentMeta(
        key="pedagogo",
        name="Pedagogo",
        color="#BA68C8",
        emoji="\U0001F4DA",
        description="Experto en teoría curricular y pedagogía crítica",
    ),
    prompt_filename="evaluador-pedagogo.md",
)
