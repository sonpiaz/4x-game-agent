"""Tests for the reflection module."""
import os
import json
import tempfile
import pytest
from agent.reflection import ReflectionLog


@pytest.fixture
def reflection():
    """Create a ReflectionLog with a temp file."""
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    log = ReflectionLog(filepath=path, log_fn=lambda x: None)
    yield log
    os.unlink(path)


def test_record_success(reflection):
    reflection.record_success("upgrade:wall")
    assert len(reflection.entries) == 1
    assert reflection.entries[0]["type"] == "success"
    assert reflection.entries[0]["task"] == "upgrade:wall"


def test_record_failure(reflection):
    reflection.record_failure("train:barracks", "timeout", "menu didn't open")
    assert len(reflection.entries) == 1
    assert reflection.entries[0]["type"] == "failure"
    assert reflection.entries[0]["error"] == "timeout"


def test_get_reflections_for(reflection):
    reflection.record_failure("upgrade:wall", "err1", "analysis1")
    reflection.record_success("upgrade:wall")
    reflection.record_failure("upgrade:academy", "err2", "analysis2")
    reflection.record_failure("train:barracks", "err3", "analysis3")

    # Should find failures for "upgrade" type
    results = reflection.get_reflections_for("upgrade:wall")
    assert len(results) == 2  # wall + academy (both "upgrade" type)


def test_success_rate(reflection):
    for _ in range(7):
        reflection.record_success("upgrade:wall")
    for _ in range(3):
        reflection.record_failure("upgrade:wall", "err", "analysis")

    rate = reflection.success_rate("upgrade")
    assert rate == 0.7


def test_max_entries(reflection):
    reflection.max_entries = 5
    for i in range(10):
        reflection.record_success(f"task:{i}")
    assert len(reflection.entries) == 5


def test_get_stats(reflection):
    reflection.record_success("a")
    reflection.record_failure("b", "err", "analysis")
    stats = reflection.get_stats()
    assert stats["total"] == 2
    assert stats["successes"] == 1
    assert stats["failures"] == 1
