"""Técnico evaluator agent."""

from .base import AgentMeta, EvaluatorAgent

tecnico_agent = EvaluatorAgent(
    meta=AgentMeta(
        key="tecnico",
        name="Técnico",
        color="#81C784",
        emoji="\U0001F4CB",
        description="Especialista en formato APA 7 y estructura documental",
    ),
    prompt_filename="evaluador-tecnico.md",
)
