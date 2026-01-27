---
description: Interactively resolve conflicts in a single file
allowed-tools: Read, Write, Edit, Bash(git:*), AskUserQuestion
argument-hint: <file-path>
---

Interactively resolve merge conflicts in a single file: $1

## Step 1: Validate File

Check that the file exists and has conflicts:
!`git diff --name-only --diff-filter=U 2>/dev/null | grep -q "^$1$" && echo "HAS_CONFLICTS" || echo "NO_CONFLICTS"`

If output is "NO_CONFLICTS", inform user and suggest using `/lz-git.conflict-resolver:conflict-status` (or `/lz-git.cr:status`) to see conflicted files.

## Step 2: Create Backup

Create backup branch if not already created:
```bash
git branch backup/conflict-resolution-$(date +%Y%m%d-%H%M%S) 2>/dev/null || true
```

## Step 3: Read and Analyze File

Read the file: @$1

For each conflict section found (marked by `<<<<<<<`):

1. **Show the conflict clearly**:
   - Display HEAD version (current branch)
   - Display incoming version
   - Explain what each side appears to be doing

2. **Propose a resolution**:
   - Analyze both versions semantically
   - Suggest how to combine or which to prefer
   - Explain reasoning

3. **Ask for approval**:
   Use AskUserQuestion to ask:
   - Accept proposed resolution
   - Prefer current (HEAD) version
   - Prefer incoming version
   - Custom resolution (user will describe)

4. **Apply the chosen resolution**

## Step 4: Validate

After all conflicts in the file are resolved:
1. Verify no conflict markers remain
2. Check basic syntax validity
3. Show the final resolved file content

## Step 5: Stage

Stage the resolved file:
```bash
git add $1
```

Report:
- Number of conflicts resolved in this file
- Summary of resolutions applied
- Remaining conflicted files (if any)
- Next steps

Use the lz-git.merge-conflicts skill for resolution strategies.
