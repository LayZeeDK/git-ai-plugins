---
description: Show current Git conflict status
allowed-tools: Bash(git status *), Bash(git diff *), Read
---

Show the current Git merge conflict status.

## Step 1: Check Repository State

Get current git status (includes merge/rebase state):
!`git status`

## Step 2: List Conflicted Files

Get all files with unresolved conflicts:
!`git diff --name-only --diff-filter=U`

## Step 3: Analyze and Report

Based on the git status output, report:
- Whether in MERGING, REBASING, or normal state
- Total files with conflicts
- Current operation and branches involved

For each conflicted file:
1. Use Read tool to read the file content
2. Display each conflict section using fenced code blocks with the language derived from file extension:
   - `.ts` → `typescript`
   - `.js` → `javascript`
   - `.py` → `python`
   - `.json` → `json`
   - `.yaml`/`.yml` → `yaml`
   - etc.

Example output format:

````
**Conflict in `path/to/file.ts`:**

HEAD (current branch):
```typescript
// current branch code here
```

Incoming (feature branch):
```typescript
// incoming branch code here
```
````

This format ensures proper syntax highlighting for the conflicting code sections.

## Step 4: Suggest Next Steps

Based on the conflict state, suggest:
- `/lz-git.conflict:resolve-all` for batch resolution
- `/lz-git.conflict:resolve <file>` for single file
- Relevant git commands (abort, continue, etc.)
