---
description: Abort conflict resolution and restore pre-conflict state
allowed-tools: Bash(git branch *), Bash(git merge --abort *), Bash(git rebase --abort *), Bash(git cherry-pick --abort *), Bash(git rev-parse *), Bash(test *), Bash(git status *), Bash(git reset *), Bash(git log *), AskUserQuestion
---

Abort the current conflict resolution and restore the repository to its pre-conflict state.

## Step 1: Detect Operation Type

Determine what operation caused the conflicts:

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

If none of these files exist, inform user there's no operation in progress to abort.

## Step 2: Find Backup Branch

Look for the most recent backup branch created by this plugin:

```bash
git branch --list "lz-git/conflict/*/backup-*" --sort=-committerdate
```

Parse the output to find the most recent backup branch matching pattern `lz-git/conflict/*/backup-*`.

## Step 3: Confirm Abort

Use AskUserQuestion to confirm the abort action. Present:

1. **Detected operation**: What will be aborted (merge, rebase, or cherry-pick)
2. **Backup branch**: If found, show the backup branch name and its commit info:
   ```bash
   git log -1 --oneline <backup-branch>
   ```
3. **Options**:
   - Abort operation only (recommended) - Uses git's native abort
   - Abort and hard reset to backup - Also resets to backup branch state
   - Cancel - Don't abort, keep resolving

Explain what each option does.

## Step 4: Execute Abort

Based on user's choice:

### Option: Abort Operation Only (Recommended)

Execute the appropriate abort command based on detected operation:

**For MERGING:**
```bash
git merge --abort
```

**For REBASING:**
```bash
git rebase --abort
```

**For CHERRY-PICKING:**
```bash
git cherry-pick --abort
```

### Option: Abort and Hard Reset to Backup

First abort the operation (as above), then:

```bash
git reset --hard <backup-branch>
```

**Warning:** This discards all changes since the backup was created.

## Step 5: Verify and Report

Check the repository status:
```bash
git status
```

Report:
- What operation was aborted
- Current branch state
- If backup was used, which backup branch
- Suggest cleaning up old backup branches if desired:
  - Show list of backup branches: `git branch --list "lz-git/conflict/*/backup-*"`
  - Note: `git branch -d <branch>` to delete individual backups
