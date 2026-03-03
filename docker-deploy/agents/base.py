"""Base evaluator agent that calls the configured LLM and returns structured JSON."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from openai import AsyncOpenAI

from config import AGENT_PROMPTS_DIR, LLM_API_KEY, LLM_BASE_URL, LLM_MAX_TOKENS, LLM_MODEL, LLM_MODEL_DISPLAY, LLM_TEMPERATURE, RULES_PATH
from evaluation.schema import FullEvaluation, NivelGeneral

# ── Token estimation ──────────────────────────────────────────────────
try:
    import tiktoken
    _enc = tiktoken.get_encoding("o200k_base")  # GPT-4o family; close enough for budget estimation
    def _estimate_tokens(text: str) -> int:
        return len(_enc.encode(text))
except ImportError:
    def _estimate_tokens(text: str) -> int:
        return len(text) // 3  # conservative heuristic for Spanish

# Minimum output tokens needed for a full evaluation JSON
_MIN_OUTPUT_TOKENS = 4000

MAX_RETRIES = 3
REQUIRED_TOP_KEYS = {"metadata", "parte_2_datos_presentacion", "resumen_ejecutivo"}


class _TruncatedResponseError(Exception):
    """Raised when the LLM response was cut short (finish_reason == 'length')."""


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

    async def _call_llm(self, plan_text: str, *, retry_tier: int = 0) -> str:
        """Single LLM call. retry_tier escalates conciseness constraints."""
        user_msg = (
            "Analiza la siguiente planeacion didactica y responde UNICAMENTE con el "
            "JSON completo del schema (metadata, parte_1_contexto, parte_2_datos_presentacion, "
            "... hasta resumen_ejecutivo). Sin texto adicional, solo el JSON.\n\n"
            "---\n\n" + plan_text
        )

        # Tier 1: moderate conciseness
        if retry_tier >= 1:
            user_msg += (
                "\n\n⚠️ IMPORTANTE: Tu respuesta anterior fue cortada por exceder el "
                "limite de tokens. Sé CONCISO: observaciones de 1 oración, evidencia "
                "máximo 1 cita corta. NO omitas secciones ni criterios."
            )

        # Tier 2: aggressive word limits
        if retry_tier >= 2:
            user_msg += (
                "\n\n🔴 CRITICO: Segunda vez cortada. Máximo 15 palabras por observacion. "
                "Evidencia: solo número de página o 'No se encontró'. "
                "Fortalezas y areas_mejora: máximo 3 items de 10 palabras cada uno."
            )

        # Temperature: reduce on retries for tighter output
        temperature = LLM_TEMPERATURE if retry_tier == 0 else max(LLM_TEMPERATURE - 0.1, 0.0)

        response = await self._client.chat.completions.create(
            model=LLM_MODEL,
            temperature=temperature,
            max_tokens=LLM_MAX_TOKENS,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_msg},
            ],
            response_format={"type": "json_object"},
        )
        choice = response.choices[0]
        content = choice.message.content or ""

        # Log token usage for diagnostics
        if response.usage:
            print(
                f"[{self.meta.key}] tokens: "
                f"prompt={response.usage.prompt_tokens} "
                f"completion={response.usage.completion_tokens} "
                f"finish={choice.finish_reason}"
            )

        # Detect truncation BEFORE attempting to parse
        if choice.finish_reason == "length":
            raise _TruncatedResponseError(
                f"Response truncated (finish_reason='length', "
                f"{len(content)} chars). Last 80 chars: ...{content[-80:]}"
            )

        return content

    async def evaluate(self, plan_text: str) -> FullEvaluation:
        """Send the plan text to the LLM and return a parsed FullEvaluation.

        Retries up to MAX_RETRIES times with escalating conciseness tiers.
        Pre-flight token estimation detects tight budgets and starts concise.
        """
        # Pre-flight: estimate if output budget is dangerously tight
        input_estimate = (
            _estimate_tokens(self.system_prompt)
            + _estimate_tokens(plan_text)
            + 200  # message overhead
        )
        start_tier = 0
        if LLM_MAX_TOKENS < _MIN_OUTPUT_TOKENS:
            print(
                f"[{self.meta.key}] ⚠ LLM_MAX_TOKENS={LLM_MAX_TOKENS} "
                f"may be insufficient for full eval"
            )
        if input_estimate > 10_000:
            print(
                f"[{self.meta.key}] ⚠ Large input (~{input_estimate} tokens), "
                f"starting with concise mode"
            )
            start_tier = 1

        last_error = None
        tier = start_tier
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                raw = await self._call_llm(plan_text, retry_tier=tier)
            except _TruncatedResponseError as e:
                last_error = e
                tier = min(tier + 1, 2)  # escalate tier for next retry
                print(f"[{self.meta.key}] Attempt {attempt}/{MAX_RETRIES} truncated: {e}")
                if attempt < MAX_RETRIES:
                    print(f"[{self.meta.key}] Retrying with tier={tier}...")
                    continue
                raise ValueError(
                    f"Agent '{self.meta.key}' failed after {MAX_RETRIES} attempts. "
                    f"Response was truncated every time — the document may be too large."
                ) from last_error

            try:
                evaluation = self._parse(raw)
                break
            except Exception as e:
                last_error = e
                print(f"[{self.meta.key}] Attempt {attempt}/{MAX_RETRIES} parse failed: {e}")
                if attempt < MAX_RETRIES:
                    print(f"[{self.meta.key}] Retrying...")
                    continue
                preview = raw[:500] if raw else "(empty)"
                raise ValueError(
                    f"Agent '{self.meta.key}' failed after {MAX_RETRIES} attempts. "
                    f"Last error: {last_error}. Response preview: {preview}"
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
