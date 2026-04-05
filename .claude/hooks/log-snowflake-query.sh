#!/bin/bash
# PostToolUse hook: auto-logs every Snowflake MCP query to the JSONL query log.
# Receives tool call JSON on stdin from Claude Code.
# Feeds into the same log that validation agent checks for coverage.

set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"

# Read hook input from stdin
INPUT=$(cat)

# Extract SQL statement from tool input
SQL=$(echo "$INPUT" | jq -r '.tool_input.statement // empty')
if [ -z "$SQL" ]; then
  exit 0  # No SQL found, skip
fi

# Extract result row count
ROW_COUNT=$(echo "$INPUT" | jq -r '.tool_response | if type == "array" then length else 0 end' 2>/dev/null || echo "0")

# Get dataset name from .knowledge/active.yaml
DATASET="unknown"
ACTIVE_FILE="$PROJECT_DIR/.knowledge/active.yaml"
if [ -f "$ACTIVE_FILE" ]; then
  DATASET=$(grep -E '^dataset_id:|^active:' "$ACTIVE_FILE" | head -1 | sed 's/.*: *//' | tr -d '"' || echo "unknown")
fi

# Current date
DATE=$(date '+%Y-%m-%d')

# Extract table names from SQL (basic grep for FROM/JOIN clauses)
TABLES=$(echo "$SQL" | grep -oiE '(FROM|JOIN)\s+[A-Za-z0-9_.]+' | sed 's/^[A-Za-z]* //' | tr '\n' ' ' | xargs || echo "")

# Build a brief result summary
RESULT_SUMMARY="${ROW_COUNT} rows returned"

# Log via the CLI wrapper (same log the validation agent reads)
python3 "$PROJECT_DIR/scripts/log_query.py" \
  --dataset "$DATASET" \
  --date "$DATE" \
  --agent "auto-hook" \
  --step 0 \
  --purpose "Auto-logged by PostToolUse hook" \
  --sql "$SQL" \
  --dialect snowflake \
  --connection snowflake_mcp \
  --tables $TABLES \
  --result "$RESULT_SUMMARY" \
  --rows "$ROW_COUNT" \
  2>/dev/null || true  # Never block Claude on log failure

exit 0
