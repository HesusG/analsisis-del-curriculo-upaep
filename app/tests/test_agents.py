"""Tests for evaluator agents."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.base import AgentMeta, EvaluatorAgent
from evaluation.schema import FullEvaluation
from tests.conftest import SAMPLE_EVALUATION


@pytest.fixture
def mock_agent(tmp_path):
    """Create an agent with a temporary prompt file."""
    prompt_file = tmp_path / "test-prompt.md"
    prompt_file.write_text("You are a test evaluator.")

    rules_file = tmp_path / "rules.md"
    rules_file.write_text("## Rules\nEvaluate carefully.")

    meta = AgentMeta(
        key="test",
        name="Test Agent",
        color="#FF0000",
        emoji="T",
        description="Test agent",
    )

    agent = EvaluatorAgent(meta, "test-prompt.md")
    agent._prompt_path = prompt_file
    agent._rules_path = rules_file
    return agent


class TestEvaluatorAgent:
    def test_system_prompt_combines_persona_and_rules(self, mock_agent):
        prompt = mock_agent.system_prompt
        assert "You are a test evaluator." in prompt
        assert "## Rules" in prompt
        assert "---" in prompt

    def test_parse_clean_json(self):
        raw = json.dumps(SAMPLE_EVALUATION)
        result = EvaluatorAgent._parse(raw)
        assert isinstance(result, FullEvaluation)
        assert result.metadata.evaluador == "Pedagogo"

    def test_parse_json_with_fences(self):
        raw = f"```json\n{json.dumps(SAMPLE_EVALUATION)}\n```"
        result = EvaluatorAgent._parse(raw)
        assert isinstance(result, FullEvaluation)

    @pytest.mark.asyncio
    async def test_evaluate_calls_openai(self, mock_agent):
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps(SAMPLE_EVALUATION)))
        ]

        mock_agent._client = MagicMock()
        mock_agent._client.chat.completions.create = AsyncMock(return_value=mock_response)

        result = await mock_agent.evaluate("Test plan text")
        assert isinstance(result, FullEvaluation)

        call_kwargs = mock_agent._client.chat.completions.create.call_args.kwargs
        assert call_kwargs["response_format"] == {"type": "json_object"}
        assert "Test plan text" in call_kwargs["messages"][1]["content"]
