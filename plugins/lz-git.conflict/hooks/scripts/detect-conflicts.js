#!/usr/bin/env node
// Detect merge conflicts after git operations
// Cross-platform (works on Windows, macOS, Linux)
// Returns JSON with systemMessage if conflicts are detected

const chunks = [];

process.stdin.on('data', chunk => chunks.push(chunk));
process.stdin.on('end', () => {
  try {
    const input = JSON.parse(Buffer.concat(chunks).toString());
    const command = input.tool_input?.command || '';
    const result = input.tool_result || '';

    // Check if this is a relevant git command
    const gitOpPattern = /^git\s+(merge|pull|rebase|cherry-pick)/i;
    if (!gitOpPattern.test(command)) {
      // Not a git merge/pull/rebase command, exit silently
      console.log(JSON.stringify({ continue: true, suppressOutput: true }));
      process.exit(0);
    }

    // Check for conflict indicators in the output
    const conflictPattern = /CONFLICT|Automatic merge failed|error: could not apply|MERGING|REBASING|CHERRY-PICKING/i;
    if (conflictPattern.test(result)) {
      // Conflicts detected
      console.log(JSON.stringify({
        continue: true,
        suppressOutput: false,
        systemMessage: 'Merge conflicts detected. Use /lz-git.conflict:resolve-all to resolve them.'
      }));
      process.exit(0);
    }

    // No conflicts
    console.log(JSON.stringify({ continue: true, suppressOutput: true }));
    process.exit(0);
  } catch (err) {
    // On error, allow operation to continue
    console.log(JSON.stringify({ continue: true, suppressOutput: true }));
    process.exit(0);
  }
});
