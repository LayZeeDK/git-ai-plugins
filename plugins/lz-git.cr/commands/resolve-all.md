---
description: Resolve all Git merge conflicts (alias for /lz-git.conflict-resolver:resolve-conflicts)
allowed-tools: Read, Write, Edit, Bash(git:*), Glob, Grep
argument-hint: [--mode=autonomous|interactive|batch]
---

Resolve all Git merge conflicts in the current repository.

Use the lz-git.merge-conflicts skill for conflict resolution strategies.

## Step 1: Create Backup Branch

Before any resolution, create a backup branch. Generate the actual timestamp value (e.g., 20260127-143052) and use it directly in the command. Do NOT use shell interpolation like $(date).
Example: `git branch backup/conflict-resolution-20260127-143052`

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
