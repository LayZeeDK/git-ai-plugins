---
description: Show current Git conflict status (alias for /lz-git.conflict-resolver:conflict-status)
allowed-tools: Bash(git:*), Read
---

Show the current Git merge conflict status.

## Step 1: Check Repository State

Determine current Git state:
!`git status --porcelain 2>/dev/null | head -20`

Check if in merge/rebase state:
!`test -f .git/MERGE_HEAD && echo "MERGING" || (test -d .git/rebase-merge && echo "REBASING" || echo "NORMAL")`

## Step 2: List Conflicted Files

Get all files with unresolved conflicts:
!`git diff --name-only --diff-filter=U 2>/dev/null`

## Step 3: Provide Summary

Report:
- Total files with conflicts
- Current operation (merge/rebase/cherry-pick)
- Branches involved (if determinable)

## Step 4: Suggest Next Steps

Based on the conflict state, suggest:
- `/lz-git.cr:resolve-all` for batch resolution
- `/lz-git.cr:resolve <file>` for single file
- Relevant git commands (abort, continue, etc.)
