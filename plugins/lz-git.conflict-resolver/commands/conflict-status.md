---
description: Show current Git conflict status
allowed-tools: Bash(git:*), Read
---

Show the current Git merge conflict status.

## Step 1: Check Repository State

Get current git status (includes merge/rebase state):
!`git status`

## Step 2: List Conflicted Files

Get all files with unresolved conflicts:
!`git diff --name-only --diff-filter=U`

## Step 3: Check Conflict Details

Show conflict markers in files:
!`git diff --check`

## Step 4: Analyze and Report

Based on the git status output, report:
- Whether in MERGING, REBASING, or normal state
- Total files with conflicts
- Current operation and branches involved

For each conflicted file, identify:
- File path
- File type (code, config, lock file, etc.)
- Brief description of conflict nature

## Step 5: Suggest Next Steps

Based on the conflict state, suggest:
- `/lz-git.conflict-resolver:resolve-conflicts` (or `/lz-git.cr:resolve-all`) for batch resolution
- `/lz-git.conflict-resolver:resolve-conflict <file>` (or `/lz-git.cr:resolve <file>`) for single file
- Relevant git commands (abort, continue, etc.)
