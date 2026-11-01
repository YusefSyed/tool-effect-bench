#!/usr/bin/env bash
# Run every repository check; the exit code is non-zero if any enforced check fails.
set -uo pipefail
cd "$(dirname "$0")/.."

FAILED=()
run_check() {
    local label="$1"; shift
    echo "--- ${label} ---"
    if "$@"; then echo "ok: ${label}"; else echo "FAILED: ${label}"; FAILED+=("$label"); fi
    echo
}

run_check "ruff format" uv run ruff format --check src tests
run_check "ruff lint" uv run ruff check src tests
run_check "mypy" uv run mypy
run_check "uv lock" uv lock --check
run_check "pytest" uv run pytest -q
run_check "build" uv build --out-dir dist
run_check "inspect-evals-lint" uv run inspect-evals-lint --all

if [ ${#FAILED[@]} -gt 0 ]; then
    echo "Enforced failures: ${FAILED[*]}"
    exit 1
fi
echo "All checks passed."
