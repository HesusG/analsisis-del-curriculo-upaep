"""Live Delphi agents: 5 experts + moderator, calling the configured LLM with JSON output."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from openai import AsyncOpenAI

from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, LLM_TEMPERATURE
from delphi.live_schema import (
    DelphiExpertEvaluation,
    DelphiSynthesis,
    DIMENSIONS,
)

PROMPTS_DIR = Path(__file__).parent / "prompts"

# ── Expert metadata ──────────────────────────────────────────────────

@dataclass
class DelphiExpertMeta:
    key: str
    name: str
    color: str
    emoji: str
    marco: str
    prompt_file: str


DELPHI_EXPERTS = [
    DelphiExpertMeta(
        key="critico",
        name="Dr. Critico",
        color="#E57373",
        emoji="\U0001F9D0",
        marco="Teoria curricular critica (Apple, Gimeno Sacristan)",
        prompt_file="critico_system.md",
    ),
    DelphiExpertMeta(
        key="multiliteracidades",
        name="Dra. Multiliteracidades",
        color="#BA68C8",
        emoji="\U0001F4DA",
        marco="Pedagogia del nuevo aprendizaje (Cope & Kalantzis)",
        prompt_file="multiliteracidades_system.md",
    ),
    DelphiExpertMeta(
        key="conectivista",
        name="Dr. Conectivista",
        color="#64B5F6",
        emoji="\U0001F310",
        marco="Conectivismo y aprendizaje en red (Siemens)",
        prompt_file="conectivista_system.md",
    ),
    DelphiExpertMeta(
        key="marketing",
        name="Dra. Marketing Educativo",
        color="#FFB74D",
        emoji="\U0001F4C8",
        marco="Innovacion en educacion de negocios (Guha, Demirci)",
        prompt_file="marketing_system.md",
    ),
    DelphiExpertMeta(
        key="pedagogia_critica",
        name="Dr. Pedagogia Critica",
        color="#81C784",
        emoji="\u270A",
        marco="Pedagogia de la liberacion (Freire, Giroux, McLaren)",
        prompt_file="pedagogia_critica_system.md",
    ),
]

# JSON output instructions appended to every expert prompt
_EXPERT_JSON_INSTRUCTION = """

---

## INSTRUCCIÓN DE FORMATO (OBLIGATORIA):
Responde EXCLUSIVAMENTE con un objeto JSON válido con esta estructura exacta:

```json
{
  "fortalezas": ["fortaleza 1", "fortaleza 2", "fortaleza 3"],
  "debilidades": ["debilidad 1", "debilidad 2", "debilidad 3"],
  "puntuaciones": [
    {"dimension": "Coherencia epistemológica", "score": 7, "justificacion": "..."},
    {"dimension": "Rol del estudiante", "score": 6, "justificacion": "..."},
    {"dimension": "Integración tecnológica", "score": 5, "justificacion": "..."},
    {"dimension": "Reflexión crítica", "score": 4, "justificacion": "..."},
    {"dimension": "Conexión teoría-práctica", "score": 6, "justificacion": "..."},
    {"dimension": "Evaluación del aprendizaje", "score": 5, "justificacion": "..."}
  ],
  "recomendaciones": ["recomendacion 1", "recomendacion 2", "recomendacion 3"]
}
```

Las 6 dimensiones son OBLIGATORIAS. Los scores son enteros de 1 a 10. Incluye al menos 3 items en fortalezas, debilidades y recomendaciones.
NO incluyas texto fuera del JSON. NO uses markdown code fences.
"""

_MODERATOR_JSON_INSTRUCTION = """

---

## INSTRUCCIÓN DE FORMATO (OBLIGATORIA):
Responde EXCLUSIVAMENTE con un objeto JSON válido con esta estructura exacta:

```json
{
  "consensos": ["consenso 1", "consenso 2"],
  "disensos": [
    {"tema": "tema del disenso", "posiciones": {"critico": "posicion...", "multiliteracidades": "posicion..."}}
  ],
  "puntuaciones_consolidadas": [
    {"dimension": "Coherencia epistemológica", "score": 7, "justificacion": "..."},
    {"dimension": "Rol del estudiante", "score": 6, "justificacion": "..."},
    {"dimension": "Integración tecnológica", "score": 5, "justificacion": "..."},
    {"dimension": "Reflexión crítica", "score": 5, "justificacion": "..."},
    {"dimension": "Conexión teoría-práctica", "score": 6, "justificacion": "..."},
    {"dimension": "Evaluación del aprendizaje", "score": 5, "justificacion": "..."}
  ],
  "recomendaciones_priorizadas": [
    {"texto": "recomendacion...", "prioridad": "Alta", "expertos": ["critico", "multiliteracidades", "conectivista"]},
    {"texto": "recomendacion...", "prioridad": "Media", "expertos": ["marketing", "pedagogia_critica"]}
  ],
  "fortalezas": ["fortaleza principal 1", "fortaleza principal 2"],
  "areas_criticas": ["area critica 1", "area critica 2"]
}
```

Las 6 dimensiones son OBLIGATORIAS en puntuaciones_consolidadas. Prioridad debe ser "Alta", "Media" o "Para considerar".
NO incluyas texto fuera del JSON. NO uses markdown code fences.
"""


def _parse_json(raw: str):
    """Parse JSON, stripping markdown fences if present."""
    text = raw.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


class DelphiExpertAgent:
    """Calls the configured LLM with an expert prompt and returns structured evaluation."""

    def __init__(self, meta: DelphiExpertMeta) -> None:
        self.meta = meta
        self._client = AsyncOpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)

    @property
    def system_prompt(self) -> str:
        prompt_path = PROMPTS_DIR / self.meta.prompt_file
        return prompt_path.read_text(encoding="utf-8") + _EXPERT_JSON_INSTRUCTION

    async def evaluate(self, plan_text: str) -> DelphiExpertEvaluation:
        response = await self._client.chat.completions.create(
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": plan_text},
            ],
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content or ""
        data = _parse_json(raw)
        return DelphiExpertEvaluation(**data)


class DelphiModeratorAgent:
    """Synthesizes 5 expert evaluations into a consolidated report."""

    def __init__(self) -> None:
        self._client = AsyncOpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)

    @property
    def system_prompt(self) -> str:
        prompt_path = PROMPTS_DIR / "moderador_system.md"
        return prompt_path.read_text(encoding="utf-8") + _MODERATOR_JSON_INSTRUCTION

    async def synthesize(
        self,
        plan_text: str,
        expert_results: dict[str, DelphiExpertEvaluation],
    ) -> DelphiSynthesis:
        # Build context with all expert evaluations
        experts_context = "# Evaluaciones de los 5 expertos:\n\n"
        for key, ev in expert_results.items():
            experts_context += f"## {key}:\n{ev.model_dump_json(indent=2)}\n\n"

        response = await self._client.chat.completions.create(
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": (
                        f"# Planeación evaluada:\n{plan_text}\n\n"
                        f"---\n\n{experts_context}\n\n"
                        "Genera la síntesis del moderador consolidando las 5 evaluaciones."
                    ),
                },
            ],
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content or ""
        data = _parse_json(raw)
        return DelphiSynthesis(**data)
