"""Base evaluator agent that calls the configured LLM and returns structured JSON."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from openai import AsyncOpenAI

from config import AGENT_PROMPTS_DIR, LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, LLM_MODEL_DISPLAY, LLM_TEMPERATURE, RULES_PATH
from evaluation.schema import FullEvaluation, NivelGeneral

MAX_RETRIES = 2
REQUIRED_TOP_KEYS = {"metadata", "parte_2_datos_presentacion", "resumen_ejecutivo"}


@dataclass
class AgentMeta:
    """Visual metadata for report rendering."""
    key: str
    name: str
    color: str
    emoji: str
    description: str


class EvaluatorAgent:
    """Wraps an evaluator persona: loads prompt, calls LLM, parses JSON."""

    def __init__(self, meta: AgentMeta, prompt_filename: str) -> None:
        self.meta = meta
        self._prompt_path = AGENT_PROMPTS_DIR / prompt_filename
        self._rules_path = RULES_PATH
        self._client = AsyncOpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)

    @property
    def system_prompt(self) -> str:
        persona = self._prompt_path.read_text(encoding="utf-8")
        rules = self._rules_path.read_text(encoding="utf-8")
        return f"{persona}\n\n---\n\n{rules}"

    async def _call_llm(self, plan_text: str) -> str:
        """Single LLM call, returns raw content string."""
        user_msg = (
            "Analiza la siguiente planeacion didactica y responde UNICAMENTE con el "
            "JSON completo del schema (metadata, parte_1_contexto, parte_2_datos_presentacion, "
            "... hasta resumen_ejecutivo). Sin texto adicional, solo el JSON.\n\n"
            "---\n\n" + plan_text
        )
        response = await self._client.chat.completions.create(
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_msg},
            ],
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content or ""

    async def evaluate(self, plan_text: str) -> FullEvaluation:
        """Send the plan text to the LLM and return a parsed FullEvaluation.

        Retries up to MAX_RETRIES times if the LLM returns malformed JSON.
        """
        last_error = None
        for attempt in range(1, MAX_RETRIES + 1):
            raw = await self._call_llm(plan_text)
            try:
                evaluation = self._parse(raw)
                break
            except Exception as e:
                last_error = e
                print(
                    f"[{self.meta.key}] Attempt {attempt}/{MAX_RETRIES} failed: {e}"
                )
                if attempt < MAX_RETRIES:
                    print(f"[{self.meta.key}] Retrying...")
                    continue
                # Show what the LLM actually returned for debugging
                preview = raw[:300] if raw else "(empty)"
                raise ValueError(
                    f"Agent '{self.meta.key}' failed after {MAX_RETRIES} attempts. "
                    f"Last error: {last_error}. LLM returned: {preview}"
                ) from last_error

        # Override evaluator identity with actual model + agent role
        evaluation.metadata.evaluador = f"{LLM_MODEL_DISPLAY} ({self.meta.name})"

        # Recalculate compliance programmatically (don't trust the LLM)
        passed, failed = evaluation.count_criteria()
        total = passed + failed
        pct = round((passed / total) * 100, 1) if total > 0 else 0.0
        evaluation.resumen_ejecutivo.criterios_cumplidos = passed
        evaluation.resumen_ejecutivo.criterios_no_cumplidos = failed
        evaluation.resumen_ejecutivo.porcentaje_cumplimiento = pct

        if pct >= 80:
            evaluation.resumen_ejecutivo.nivel_general = NivelGeneral.SATISFACTORIO
        elif pct >= 60:
            evaluation.resumen_ejecutivo.nivel_general = NivelGeneral.EN_PROCESO
        else:
            evaluation.resumen_ejecutivo.nivel_general = NivelGeneral.REQUIERE_ATENCION

        return evaluation

    @staticmethod
    def _parse(raw: str) -> FullEvaluation:
        """Parse JSON, stripping markdown fences if present."""
        text = raw.strip()
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        data = json.loads(text)

        # LLM sometimes wraps the object in a list — unwrap it
        if isinstance(data, list):
            data = data[0]

        # LLM sometimes wraps in a function-call or nested envelope — dig for payload
        if isinstance(data, dict) and not REQUIRED_TOP_KEYS.issubset(data.keys()):
            # Search one level deep for the real evaluation dict
            for val in data.values():
                if isinstance(val, dict) and REQUIRED_TOP_KEYS.issubset(val.keys()):
                    data = val
                    break

        # Final validation: if still missing required keys, raise clear error
        if isinstance(data, dict) and not REQUIRED_TOP_KEYS.issubset(data.keys()):
            got_keys = list(data.keys())[:5]
            raise ValueError(
                f"LLM returned JSON with wrong structure. "
                f"Expected keys like 'metadata', 'parte_2_datos_presentacion', etc. "
                f"Got keys: {got_keys}"
            )

        return FullEvaluation(**data)
