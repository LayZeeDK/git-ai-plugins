---
description: Interactively resolve conflicts in a single file (alias for /lz-git.conflict-resolver:resolve-conflict)
allowed-tools: Read, Write, Edit, Bash(git:*), AskUserQuestion
argument-hint: <file-path>
---

Interactively resolve merge conflicts in a single file: $1

Use the lz-git.merge-conflicts skill for resolution strategies.

## Step 1: Validate File

Check that the file has conflicts by listing conflicted files:
!`git diff --name-only --diff-filter=U`

If the target file $1 is NOT in the list, inform user and suggest using `/lz-git.cr:status` to see conflicted files.

## Step 2: Create Backup

Create backup branch if not already created. Generate the actual timestamp value (e.g., 20260127-143052) and use it directly in the command. Do NOT use shell interpolation like $(date).
Example: `git branch backup/conflict-resolution-20260127-143052`

## Step 3: Read and Analyze File

Read the file: @$1

For each conflict section found (marked by `<<<<<<<`):

1. **Show the conflict clearly**: Display HEAD and incoming versions
2. **Propose a resolution**: Analyze semantically and suggest how to combine
3. **Ask for approval**: Use AskUserQuestion for user decision
4. **Apply the chosen resolution**

## Step 4: Validate and Stage

After all conflicts resolved:
1. Verify no conflict markers remain
2. Stage the resolved file with `git add`

Report summary and remaining conflicts.
