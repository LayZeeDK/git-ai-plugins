---
description: Resolve all Git merge conflicts (alias for /lz-git.conflict-resolver:resolve-conflicts)
allowed-tools: Read, Write, Edit, Bash(git status:*), Bash(git diff:*), Bash(git branch:*), Bash(git add:*), Bash(node:*), Glob, Grep
argument-hint: [--mode=autonomous|interactive|batch]
---

Resolve all Git merge conflicts in the current repository.

Use the lz-git.merge-conflicts skill for conflict resolution strategies.

## Step 1: Create Backup Branch

Create a backup branch before making changes.

**IMPORTANT: Run the timestamp script first. Do NOT use placeholder values like 000000.**

First, get the UTC timestamp:
```
node $CLAUDE_PLUGIN_ROOT/scripts/utc-timestamp.js
```

Then create the backup branch using the output:
```
git branch backup/conflict-resolution-<timestamp>
```

## Step 2: Identify All Conflicts

List all files with conflicts:
!`git diff --name-only --diff-filter=U`

If no output (empty list), inform the user there are no conflicts and exit.

## Step 3: Determine Resolution Mode

Parse arguments from: $ARGUMENTS

- If `--mode=autonomous`: Resolve all conflicts automatically, report at end
- If `--mode=interactive`: For each conflict, show both versions and ask user approval
- If `--mode=batch` or no mode specified: Analyze all conflicts, show proposed resolutions, wait for approval

## Step 4: For Each Conflicted File

1. Read the entire file to understand context
2. Identify all conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`)
3. Analyze each conflict semantically
4. Apply smart merge strategy based on file type

## Step 5: Validate and Stage

After resolving each file:
1. Ensure all conflict markers are removed
2. Stage resolved files with `git add`

Report summary of resolutions and next steps.
