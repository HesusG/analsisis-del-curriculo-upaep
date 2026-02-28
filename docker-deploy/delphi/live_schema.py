"""Pydantic models for live Delphi panel evaluation (6 dimensions, 1-10 scores)."""

from __future__ import annotations

from pydantic import BaseModel, Field


DIMENSIONS = [
    "Coherencia epistemológica",
    "Rol del estudiante",
    "Integración tecnológica",
    "Reflexión crítica",
    "Conexión teoría-práctica",
    "Evaluación del aprendizaje",
]


class DimensionScore(BaseModel):
    dimension: str
    score: int = Field(ge=1, le=10)
    justificacion: str


class DelphiExpertEvaluation(BaseModel):
    fortalezas: list[str] = Field(min_length=1)
    debilidades: list[str] = Field(min_length=1)
    puntuaciones: list[DimensionScore]
    recomendaciones: list[str] = Field(min_length=1)


class DisensoItem(BaseModel):
    tema: str
    posiciones: dict[str, str]  # expert_key -> position text


class PrioritizedRecommendation(BaseModel):
    texto: str
    prioridad: str  # "Alta", "Media", "Para considerar"
    expertos: list[str]


class DelphiSynthesis(BaseModel):
    consensos: list[str]
    disensos: list[DisensoItem]
    puntuaciones_consolidadas: list[DimensionScore]
    recomendaciones_priorizadas: list[PrioritizedRecommendation]
    fortalezas: list[str]
    areas_criticas: list[str]
