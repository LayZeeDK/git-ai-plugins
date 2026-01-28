---
description: Interactively resolve conflicts in a single file
allowed-tools: Read, Write, Edit, Bash(git status *), Bash(git diff *), Bash(git branch *), Bash(git add *), Bash(git rev-parse *), Bash(date *), Bash(test *), AskUserQuestion
argument-hint: <file-path>
---

Interactively resolve merge conflicts in a single file: $1

## Step 1: Validate File and Detect Operation

Check that the file has conflicts by listing conflicted files:
!`git diff --name-only --diff-filter=U`

If the target file $1 is NOT in the list, inform user and suggest using `/lz-git.conflict:status` to see conflicted files.

Detect the Git operation type by checking state files:

```bash
test -f .git/MERGE_HEAD && echo "MERGING"
```

```bash
test -d .git/rebase-merge && echo "REBASING"
```

```bash
test -d .git/rebase-apply && echo "REBASING"
```

```bash
test -f .git/CHERRY_PICK_HEAD && echo "CHERRY-PICKING"
```

Remember the detected operation type for the final report.

## Step 2: Create Backup

Create a backup branch before making changes.

First, get the current branch name:
```bash
git rev-parse --abbrev-ref HEAD
```

Then get the UTC timestamp:
```bash
date -u +"%Y%m%d-%H%M%SZ"
```

Then create the backup branch using the branch name and timestamp:
```bash
git branch lz-git/conflict/<BRANCH_NAME>/backup-<TIMESTAMP>
```

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

## Step 5: Stage and Report

Stage the resolved file using `git add` with the filename.

Report:
- Number of conflicts resolved in this file
- Summary of resolutions applied
- Remaining conflicted files (if any)
- Next steps based on detected operation type:
  - **MERGING**: If no remaining conflicts, `git commit` to complete the merge
  - **REBASING**: If no remaining conflicts, `git rebase --continue` to continue
  - **CHERRY-PICKING**: If no remaining conflicts, `git cherry-pick --continue` to continue
  - If conflicts remain, suggest `/lz-git.conflict:resolve <file>` for next file

Use the merge-conflicts skill for resolution strategies.
