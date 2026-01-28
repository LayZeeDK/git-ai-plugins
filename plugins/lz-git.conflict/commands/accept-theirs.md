---
description: Accept incoming branch version for all conflicts or a specific file
allowed-tools: Read, Bash(git checkout *), Bash(git add *), Bash(git diff *), Bash(git rev-parse *), Bash(date *), Bash(git branch *), Bash(test *), Bash(git status *), AskUserQuestion
argument-hint: "[file-path]"
---

Accept the incoming branch (theirs) version for all conflicts or a specific file.

This is useful when you know the incoming branch's version is correct and want to discard all current branch changes.

## Step 1: Identify Conflicts

List all files with conflicts:
!`git diff --name-only --diff-filter=U`

If no output (empty list), inform the user there are no conflicts and exit.

Parse arguments from: $ARGUMENTS

If a file path is provided, verify it's in the conflicted files list.
Set `$TARGET_FILES` to the specified file or all conflicted files if none specified.

## Step 2: Detect Git Operation Type

Determine the operation type for the final report:

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

Remember the detected operation type.

## Step 3: Confirm Action

If resolving all files (no specific file provided), use AskUserQuestion to confirm:
- Show list of files that will be resolved
- Explain that all current branch changes will be discarded in favor of incoming
- Ask for confirmation before proceeding

If resolving a single file, proceed directly.

## Step 4: Create Backup Branch

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

## Step 5: Accept Theirs

For each file in `$TARGET_FILES`:

```bash
git checkout --theirs <file>
```

Then stage the resolved file:

```bash
git add <file>
```

## Step 6: Report

Report:
- Number of files resolved
- List of files that accepted incoming branch version
- Backup branch name created
- Next steps based on detected operation type:
  - **MERGING**: `git commit` to complete the merge
  - **REBASING**: `git rebase --continue` to continue the rebase
  - **CHERRY-PICKING**: `git cherry-pick --continue` to continue
  - If conflicts remain, suggest `/lz-git.conflict:status` to see remaining files
