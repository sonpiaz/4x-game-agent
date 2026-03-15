.PHONY: setup test lint clean

setup:
	pip install -e ".[all,dev]"

test:
	pytest agent/tests/ -v

lint:
	ruff check agent/ games/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
