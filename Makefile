check:
	@bash tools/run_checks.sh

test:
	uv run pytest -q

.PHONY: check test
