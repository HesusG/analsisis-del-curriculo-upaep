"""Base evaluator agent that calls GPT-4o and returns structured JSON."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from openai import AsyncOpenAI

from config import AGENT_PROMPTS_DIR, LLM_MODEL, LLM_TEMPERATURE, RULES_PATH
from evaluation.schema import FullEvaluation


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
        self._client = AsyncOpenAI()

    @property
    def system_prompt(self) -> str:
        persona = self._prompt_path.read_text(encoding="utf-8")
        rules = self._rules_path.read_text(encoding="utf-8")
        return f"{persona}\n\n---\n\n{rules}"

    async def evaluate(self, plan_text: str) -> FullEvaluation:
        """Send the plan text to GPT-4o and return a parsed FullEvaluation."""
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
        return self._parse(raw)

    @staticmethod
    def _parse(raw: str) -> FullEvaluation:
        """Parse JSON, stripping markdown fences if present."""
        text = raw.strip()
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        data = json.loads(text)
        return FullEvaluation(**data)
