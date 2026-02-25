"""Profesor evaluator agent."""

from .base import AgentMeta, EvaluatorAgent

profesor_agent = EvaluatorAgent(
    meta=AgentMeta(
        key="profesor",
        name="Profesor",
        color="#64B5F6",
        emoji="\U0001F9D1\u200D\U0001F3EB",
        description="Simula la evaluación con la rúbrica de la Dra. Mendoza",
    ),
    prompt_filename="evaluador-profesor.md",
)
