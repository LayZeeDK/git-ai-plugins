---
description: Resolve all Git merge conflicts with batch preview
allowed-tools: Read, Write, Edit, Bash(git status *), Bash(git diff *), Bash(git branch *), Bash(git add *), Bash(node *), Glob, Grep
argument-hint: [--mode=autonomous|interactive|batch]
---

Resolve all Git merge conflicts in the current repository.

## Step 1: Create Backup Branch

Create a backup branch before making changes. **IMPORTANT**: Run this exact command as-is (do NOT substitute with PowerShell or other alternatives - the Bash tool uses Git Bash on Windows):

```bash
git branch backup/conflict-resolution-$(date -u +"%Y%m%d-%H%M%S")
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
3. Analyze each conflict and display using markdown code blocks:
   - What does the current branch's code do?
   - What does the incoming branch's code do?
   - Can changes be combined semantically?

When showing conflicts to the user, use fenced code blocks with the appropriate language:
```
**HEAD version:**
```js
// current branch code
```

**Incoming version:**
```js
// incoming branch code
```
```

## Step 5: Apply Smart Merge Strategy

For code files (JS, TS, Python, etc.):
- Import statements: combine unique imports
- Function changes: merge if non-conflicting logic
- Class modifications: include additions from both sides

For config files (JSON, YAML):
- Merge object properties from both sides
- For version conflicts, prefer higher version
- For arrays, union when order doesn't matter

For lock files (package-lock.json, yarn.lock, pnpm-lock.yaml):
- Accept incoming version
- Recommend regenerating with package manager

## Step 6: Validate Resolutions

After resolving each file:
1. Ensure all conflict markers are removed
2. Check syntax validity where possible
3. Report what was combined from each side

## Step 7: Stage and Report

Stage all resolved files using `git add <filename>` for each resolved file.

Report:
- Number of files resolved
- Summary of changes per file
- Any files that need human review
- Next steps (commit or continue rebase)

Use the merge-conflicts skill for detailed resolution strategies.
