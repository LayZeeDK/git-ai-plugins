#!/bin/bash
# Detect merge conflicts after git operations
# Returns JSON with systemMessage if conflicts are detected

set -euo pipefail

# Read JSON input from stdin
input=$(cat)

# Extract tool_input (the command) and tool_result (the output)
tool_input=$(echo "$input" | jq -r '.tool_input.command // ""')
tool_result=$(echo "$input" | jq -r '.tool_result // ""')

# Check if this is a relevant git command
if [[ ! "$tool_input" =~ ^git\ (merge|pull|rebase|cherry-pick) ]]; then
  # Not a git merge/pull/rebase command, exit silently
  echo '{"continue": true, "suppressOutput": true}'
  exit 0
fi

# Check for conflict indicators in the output
if echo "$tool_result" | grep -qi "CONFLICT\|Automatic merge failed\|error: could not apply\|MERGING\|REBASING\|CHERRY-PICKING"; then
  # Conflicts detected
  echo '{"continue": true, "suppressOutput": false, "systemMessage": "Merge conflicts detected. Use /lz-git.conflict-resolver:resolve-conflicts or /lz-git.cr:resolve-all to resolve them."}'
  exit 0
fi

# No conflicts
echo '{"continue": true, "suppressOutput": true}'
exit 0
