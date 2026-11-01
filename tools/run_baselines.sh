#!/usr/bin/env bash
# One-line provider switch for the model smoke test and the two register baselines.
#
#   PROVIDER=anthropic tools/run_baselines.sh smoke      # 10 samples on the small model
#   PROVIDER=anthropic tools/run_baselines.sh small      # full run, small model
#   PROVIDER=anthropic tools/run_baselines.sh large      # full run, large model
#   PROVIDER=openai    tools/run_baselines.sh all        # both full runs, back to back
#   PROVIDER=anthropic tools/run_baselines.sh frontier   # optional third run, claude-opus-5-5
#   EPOCHS=2 PROVIDER=anthropic tools/run_baselines.sh small  # variance run, two epochs
#   PROMPT=undefended PROVIDER=anthropic tools/run_baselines.sh small  # exploratory arm
#   SUITE=v3 PROVIDER=anthropic tools/run_baselines.sh frontier  # v0.3 stronger attacks
#
# PROVIDER selects the pair: anthropic = claude-haiku-5-5 + claude-sonnet-5-5,
# openai = gpt-5-nano + gpt-5-mini. The provider's key must already be in the
# environment; this script only checks that the variable is non-empty and never
# prints it. Extra arguments are passed to `inspect eval`.
set -euo pipefail
cd "$(dirname "$0")/.."

PROVIDER="${PROVIDER:-anthropic}"
case "$PROVIDER" in
  anthropic)
    SMALL="anthropic/claude-haiku-5-5"; LARGE="anthropic/claude-sonnet-5-5"
    FRONTIER="anthropic/claude-opus-5-5"
    KEY_VAR="ANTHROPIC_API_KEY" ;;
  openai)
    SMALL="openai/gpt-5-nano"; LARGE="openai/gpt-5-mini"
    FRONTIER=""
    KEY_VAR="OPENAI_API_KEY" ;;
  *)
    echo "PROVIDER must be anthropic or openai (got '$PROVIDER')" >&2; exit 2 ;;
esac
if [ -z "${!KEY_VAR:-}" ]; then
  echo "$KEY_VAR is not set in this environment; nothing was run." >&2
  exit 3
fi

MODE="${1:-smoke}"
shift || true
EPOCHS="${EPOCHS:-1}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
PROMPT="${PROMPT:-defended}"
SUFFIX=""
[ "$EPOCHS" != "1" ] && SUFFIX="-e$EPOCHS"
[ "$PROMPT" != "defended" ] && SUFFIX="$SUFFIX-$PROMPT"
SUITE="${SUITE:-v2}"
[ "$SUITE" != "v2" ] && SUFFIX="$SUFFIX-$SUITE"
SANDBOXES="${SANDBOXES:-4}"
TASK="tool_effect_bench/tool_effect_bench"

run() {
  local model="$1" logdir="$2"; shift 2
  echo "== $(date -u +%FT%TZ) $model -> $logdir"
  uv run inspect eval "$TASK" --model "$model" --epochs "$EPOCHS" \
    --log-dir "$logdir" --no-log-realtime -T "prompt=$PROMPT" -T "suite=$SUITE" "$@"
}

case "$MODE" in
  smoke)
    run "$SMALL" "logs/smoke-${SMALL##*/}-$STAMP" --limit 10 \
      --max-sandboxes 2 --max-samples 2 "$@" ;;
  small)
    run "$SMALL" "logs/baseline-${SMALL##*/}$SUFFIX-$STAMP" --max-sandboxes "$SANDBOXES" \
      --max-samples "$SANDBOXES" -T "evidence_dir=evidence/${SMALL##*/}$SUFFIX-$STAMP" "$@" ;;
  large)
    run "$LARGE" "logs/baseline-${LARGE##*/}$SUFFIX-$STAMP" --max-sandboxes "$SANDBOXES" \
      --max-samples "$SANDBOXES" -T "evidence_dir=evidence/${LARGE##*/}$SUFFIX-$STAMP" "$@" ;;
  frontier)
    if [ -z "$FRONTIER" ]; then
      echo "no frontier model configured for PROVIDER=$PROVIDER" >&2; exit 2
    fi
    run "$FRONTIER" "logs/baseline-${FRONTIER##*/}$SUFFIX-$STAMP" --max-sandboxes "$SANDBOXES" \
      --max-samples "$SANDBOXES" -T "evidence_dir=evidence/${FRONTIER##*/}$SUFFIX-$STAMP" "$@" ;;
  all)
    "$0" small "$@"
    "$0" large "$@" ;;
  *)
    echo "mode must be smoke, small, large, frontier or all (got '$MODE')" >&2; exit 2 ;;
esac
