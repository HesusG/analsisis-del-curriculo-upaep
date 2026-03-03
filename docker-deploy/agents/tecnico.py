"""Técnico evaluator agent."""

from .base import AgentMeta, EvaluatorAgent

tecnico_agent = EvaluatorAgent(
    meta=AgentMeta(
        key="tecnico",
        name="Dra. Isabel Montes",
        color="#81C784",
        emoji="\U0001F517",
        description="Verifica la alineación y coherencia entre todas las secciones",
    ),
    prompt_filename="evaluador-tecnico.md",
)
