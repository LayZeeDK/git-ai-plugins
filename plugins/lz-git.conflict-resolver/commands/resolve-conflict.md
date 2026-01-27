---
description: Interactively resolve conflicts in a single file
allowed-tools: Read, Write, Edit, Bash(git status:*), Bash(git diff:*), Bash(git branch:*), Bash(git branch --list:*), Bash(git add:*), AskUserQuestion
argument-hint: <file-path>
---

Interactively resolve merge conflicts in a single file: $1

## Step 1: Validate File

Check that the file has conflicts by listing conflicted files:
!`git diff --name-only --diff-filter=U`

If the target file $1 is NOT in the list, inform user and suggest using `/lz-git.conflict-resolver:conflict-status` (or `/lz-git.cr:status`) to see conflicted files.

## Step 2: Create Backup

Create a backup branch before making changes.

1. First, list existing backup branches to find a unique name:
   !`git branch --list backup/conflict-resolution-*`

2. Create a new backup branch with today's date (YYYYMMDD format).
   - If `backup/conflict-resolution-YYYYMMDD` doesn't exist, use that
   - If it exists, append `-2`, `-3`, etc. until finding an unused name
   - Example: `backup/conflict-resolution-20260128` or `backup/conflict-resolution-20260128-2`

Do NOT use shell interpolation like $(date). Use today's date from context.

## Step 3: Read and Analyze File

Read the file: @$1

For each conflict section found (marked by `<<<<<<<`):

1. **Show the conflict clearly** using markdown code blocks:
   - Display HEAD version (current branch) in a fenced code block with appropriate language
   - Display incoming version in a separate fenced code block
   - Explain what each side appears to be doing

   Example format:
   ```
   **HEAD version (current branch):**
   ```js
   // code here
   ```

   **Incoming version:**
   ```js
   // code here
   ```
   ```

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

Stage the resolved file using `git add` with the filename.

Report:
- Number of conflicts resolved in this file
- Summary of resolutions applied
- Remaining conflicted files (if any)
- Next steps

Use the lz-git.merge-conflicts skill for resolution strategies.
