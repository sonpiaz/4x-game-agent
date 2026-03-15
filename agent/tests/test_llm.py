"""Tests for the LLM module (JSON parsing only, no API calls)."""
from agent.llm import LLMVision


def test_parse_json_clean():
    result = LLMVision._parse_json('{"action": "tap", "x": 100, "y": 200}')
    assert result["action"] == "tap"
    assert result["x"] == 100


def test_parse_json_markdown_block():
    raw = '```json\n{"action": "done", "reason": "completed"}\n```'
    result = LLMVision._parse_json(raw)
    assert result["action"] == "done"


def test_parse_json_with_text_around():
    raw = 'Here is the result: {"action": "wait", "seconds": 3} end'
    result = LLMVision._parse_json(raw)
    assert result["action"] == "wait"


def test_parse_json_failure():
    result = LLMVision._parse_json("not json at all")
    assert result["target"] == "parse_error"
