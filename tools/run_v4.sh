#!/usr/bin/env bash
# v0.4 non-Claude targets: one provider switch, the same scorer and sample sets.
#
#   PROVIDER=openai  MODEL=gpt-6-astra tools/run_v4.sh smoke   # 2 samples
#   PROVIDER=openai  MODEL=gpt-6-astra tools/run_v4.sh full    # v2 120, then v3 68
#   PROVIDER=bedrock MODEL=deepseek.v3.2 tools/run_v4.sh full
#   PROVIDER=ollama  MODEL=qwen3.5:27b SANDBOXES=1 tools/run_v4.sh full
#   PROVIDER=google  MODEL=<gemini id> tools/run_v4.sh smoke
#   PROVIDER=openai  MODEL=gpt-6-luna tools/run_v4.sh control  # positive control
#
# Environment each provider needs (checked for presence here, never printed):
#   openai   OPENAI_API_KEY
#   google   GOOGLE_API_KEY
#   bedrock  AWS_BEARER_TOKEN_BEDROCK and AWS_DEFAULT_REGION
#   ollama   none; a local server at OLLAMA_BASE_URL (default 127.0.0.1:11434)
#
# Sample errors are kept in the log instead of stopping the run, so a model
# whose tool calling fails on some samples still gets a complete, scored record.
# Extra arguments are passed to `inspect eval`.
set -euo pipefail
cd "$(dirname "$0")/.."

PROVIDER="${PROVIDER:?set PROVIDER to openai, google, bedrock or ollama}"
MODEL="${MODEL:?set MODEL to the provider model id}"
need=()
extra=()
case "$PROVIDER" in
  openai) need=(OPENAI_API_KEY) ;;
  google) need=(GOOGLE_API_KEY) ;;
  bedrock)
    need=(AWS_BEARER_TOKEN_BEDROCK AWS_DEFAULT_REGION)
    # Nova rejects the cachePoint Inspect adds to tool-result messages.
    case "$MODEL" in *amazon.nova*) extra=(--cache-prompt=false) ;; esac
    ;;
  ollama)
    # The local settings of the parent project's August run, longer timeouts for
    # larger models, and one model connection at a time.
    export OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://127.0.0.1:11434/v1}"
    extra=(--temperature 0 --seed 1729 --max-connections 1 --timeout 600)
    ;;
  *) echo "PROVIDER must be openai, google, bedrock or ollama (got '$PROVIDER')" >&2; exit 2 ;;
esac
for var in "${need[@]:-}"; do
  if [ -n "$var" ] && [ -z "${!var:-}" ]; then
    echo "$var is not set in this environment; nothing was run." >&2
    exit 3
  fi
done

MODE="${1:-smoke}"
shift || true
SANDBOXES="${SANDBOXES:-4}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
SLUG="$(printf '%s' "$MODEL" | tr -c 'A-Za-z0-9.-' '-')"
TASK="tool_effect_bench/tool_effect_bench"

run() {
  local suite="$1" name="$2"; shift 2
  echo "== $(date -u +%FT%TZ) $PROVIDER/$MODEL suite=$suite -> logs/$name"
  uv run --group baselines inspect eval "$TASK" --model "$PROVIDER/$MODEL" \
    --log-dir "logs/$name" --no-log-realtime --no-fail-on-error \
    -T "suite=$suite" -T "evidence_dir=evidence/$name" \
    --max-sandboxes "$SANDBOXES" --max-samples "$SANDBOXES" \
    ${extra[@]+"${extra[@]}"} "$@"
}

case "$MODE" in
  smoke) run v3 "v4-smoke-$SLUG-$STAMP" --limit 2 "$@" ;;
  full)
    run v2 "v4-$SLUG-v2-$STAMP" "$@"
    run v3 "v4-$SLUG-v3-$STAMP" "$@"
    ;;
  v2 | v3) run "$MODE" "v4-$SLUG-$MODE-$STAMP" "$@" ;;
  control) run v3 "v4-control-$SLUG-$STAMP" -T prompt=obey "$@" ;;
  *) echo "mode must be smoke, full, v2, v3 or control (got '$MODE')" >&2; exit 2 ;;
esac
