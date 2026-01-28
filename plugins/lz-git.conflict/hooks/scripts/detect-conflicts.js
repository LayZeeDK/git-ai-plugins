#!/usr/bin/env node
// Detect merge conflicts after git operations
// Cross-platform (works on Windows, macOS, Linux)
// Returns JSON with decision:block to prompt Claude when conflicts are detected

const chunks = [];

process.stdin.on('data', chunk => chunks.push(chunk));
process.stdin.on('end', () => {
  try {
    const input = JSON.parse(Buffer.concat(chunks).toString());

    const command = input.tool_input?.command || '';
    // Handle both input formats: tool_result (string) or tool_response.stdout
    const result = input.tool_result || input.tool_response?.stdout || '';

    // Check if this is a relevant git command
    const gitOpPattern = /^git\s+(merge|pull|rebase|cherry-pick)/i;
    if (!gitOpPattern.test(command)) {
      // Not a git merge/pull/rebase command, exit silently
      process.exit(0);
    }

    // Check for conflict indicators in the output
    const conflictPattern = /CONFLICT|Automatic merge failed|error: could not apply|MERGING|REBASING|CHERRY-PICKING/i;
    if (conflictPattern.test(result)) {
      // Conflicts detected - use decision:block to prompt Claude directly
      console.log(JSON.stringify({
        decision: 'block',
        reason: 'Merge conflicts detected. Inform the user they can use /lz-git.conflict:resolve-all to resolve all conflicts, or /lz-git.conflict:resolve <file> for a single file.'
      }));
    }

    process.exit(0);
  } catch (err) {
    // On error, allow operation to continue
    process.exit(0);
  }
});
