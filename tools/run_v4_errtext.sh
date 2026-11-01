#!/usr/bin/env bash
# Bedrock rerun with tool error text delivered (Amendment 3 of paper/V03-PROTOCOL.md).
# Separate from tools/run_v4.sh so the two run sets stay apart. Only the placements whose
# attack text travels in a tool error run here:
#
#   MODEL=deepseek.v3.2 tools/run_v4_errtext.sh smoke     # 2 tool_error samples
#   MODEL=deepseek.v3.2 tools/run_v4_errtext.sh v2        # base, tool_error, 60 samples
#   MODEL=deepseek.v3.2 tools/run_v4_errtext.sh v3        # stronger, 29 samples
#   MODEL=deepseek.v3.2 tools/run_v4_errtext.sh control   # stronger, prompt=obey, 29 samples
#
# Needs AWS_BEARER_TOKEN_BEDROCK and AWS_DEFAULT_REGION (checked, never printed).
set -euo pipefail
cd "$(dirname "$0")/.."

MODEL="${MODEL:?set MODEL to the Bedrock model id}"
for var in AWS_BEARER_TOKEN_BEDROCK AWS_DEFAULT_REGION; do
  if [ -z "${!var:-}" ]; then
    echo "$var is not set in this environment; nothing was run." >&2
    exit 3
  fi
done
extra=()
# Nova rejects the cachePoint Inspect adds to tool-result messages.
case "$MODEL" in *amazon.nova*) extra=(--cache-prompt=false) ;; esac

MODE="${1:-smoke}"
shift || true
SANDBOXES="${SANDBOXES:-2}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
SLUG="$(printf '%s' "$MODEL" | tr -c 'A-Za-z0-9.-' '-')"

run() {
  local suite="$1" placement="$2" name="$3"; shift 3
  echo "== $(date -u +%FT%TZ) bedrock/$MODEL suite=$suite placement=$placement -> logs/$name"
  uv run --group baselines inspect eval tool_effect_bench/tool_effect_bench \
    --model "bedrock/$MODEL" --log-dir "logs/$name" --no-log-realtime --no-fail-on-error \
    -T "suite=$suite" -T "placement=$placement" -T tool_error_text=true \
    -T "evidence_dir=evidence/$name" \
    --max-sandboxes "$SANDBOXES" --max-samples "$SANDBOXES" \
    ${extra[@]+"${extra[@]}"} "$@"
}

case "$MODE" in
  smoke) run v3 tool_error "v4-errtext-smoke-$SLUG-$STAMP" --limit 2 "$@" ;;
  v2) run v2 tool_error "v4-errtext-$SLUG-v2-$STAMP" "$@" ;;
  v3) run v3 tool_error,multi_step "v4-errtext-$SLUG-v3-$STAMP" "$@" ;;
  control) run v3 tool_error,multi_step "v4-errtext-control-$SLUG-$STAMP" -T prompt=obey "$@" ;;
  *) echo "mode must be smoke, v2, v3 or control (got '$MODE')" >&2; exit 2 ;;
esac
