---
description: Resolve Git merge conflicts - single file (interactive) or all files (batch/autonomous/interactive)
allowed-tools: Read, Write, Edit, Bash(git status *), Bash(git diff *), Bash(git branch *), Bash(git add *), Bash(git rev-parse *), Bash(date *), Bash(test *), Glob, Grep, AskUserQuestion
argument-hint: "[file-path] [-a|--mode=autonomous] [-i|--mode=interactive] [-b|--mode=batch]"
---

Resolve Git merge conflicts in the current repository.

## Parse Arguments

Parse arguments from: $ARGUMENTS

**Behavior:**
- **No arguments**: Resolve all files with batch mode (default)
- **`<file-path>` only**: Resolve single file interactively
- **`-a` or `--mode=autonomous`**: Resolve all files automatically, report at end
- **`-i` or `--mode=interactive`**: Resolve all files, ask per conflict
- **`-b` or `--mode=batch`**: Resolve all files, preview all then apply (default for no file)

**Mode descriptions:**
- **batch** (default for all-files): Show all proposed resolutions, ask for approval, then apply all at once
- **interactive**: Ask for approval on each individual conflict before moving to next
- **autonomous**: Resolve all conflicts automatically, report at end (no prompts)

Set `$FILE_PATH` if a file argument is provided, otherwise empty.
Set `$MODE` to one of: `autonomous`, `interactive`, `batch` (default if no mode specified and no file).

If `$FILE_PATH` is provided without a mode flag, use `interactive` mode for that single file.

## Step 1: Detect Git Operation Type

Determine whether this is a merge, rebase, or cherry-pick by checking Git state files:

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

## Step 2: Identify Conflicted Files

List all files with conflicts:
!`git diff --name-only --diff-filter=U`

If no output (empty list), inform the user there are no conflicts and exit.

If `$FILE_PATH` is set, verify it's in the conflicted files list. If not, inform user and suggest using `/lz-git.conflict:status` to see conflicted files.

## Step 3: Create Backup Branch

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

## Step 4: Resolve Conflicts

### Single File Mode (when `$FILE_PATH` is set)

Read the file: @$FILE_PATH

For each conflict section found (marked by `<<<<<<<`):

1. **Show the conflict clearly** using markdown code blocks:
   - Display HEAD version (current branch) in a fenced code block
   - Display incoming version in a separate fenced code block
   - Use the language derived from file extension (`.ts` -> `typescript`, `.js` -> `javascript`, `.py` -> `python`, etc.)
   - Explain what each side appears to be doing

   Example output format:

   ````
   **HEAD version (current branch):**
   ```typescript
   // code here
   ```

   **Incoming version:**
   ```typescript
   // code here
   ```
   ````

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

### All Files Mode (when `$FILE_PATH` is empty)

For each conflicted file:

1. Read the entire file to understand context
2. Identify all conflict markers (`<<<<<<<`, `|||||||`, `=======`, `>>>>>>>`)
3. Analyze each conflict and display using markdown code blocks:
   - What does the current branch's code do?
   - What does the incoming branch's code do?
   - Can changes be combined semantically?

When showing conflicts to the user, use fenced code blocks with the language derived from file extension:
- `.ts` -> `typescript`, `.js` -> `javascript`, `.py` -> `python`, `.json` -> `json`, `.yaml`/`.yml` -> `yaml`

#### Apply Smart Merge Strategy

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

#### Mode-Specific Behavior

**Batch mode (`-b` or default)**:
1. Analyze ALL conflicts first
2. Present summary of ALL proposed resolutions
3. Use AskUserQuestion to get approval for entire batch
4. Apply all resolutions at once

**Interactive mode (`-i`)**:
1. For EACH conflict, show both versions
2. Propose resolution
3. Use AskUserQuestion to get approval
4. Apply resolution before moving to next conflict

**Autonomous mode (`-a`)**:
1. Analyze all conflicts
2. Apply smart merge strategy without prompts
3. Report results at the end

## Step 5: Validate Resolutions

After resolving each file:
1. Use the Grep tool (not bash grep) to verify no conflict markers remain:
   - Pattern: `<<<<<<<|[|]{7}|=======|>>>>>>>`
   - This covers all `merge.conflictstyle` settings (merge, diff3, zdiff3)
   - Search each resolved file
2. Check syntax validity where possible
3. Report what was combined from each side

## Step 6: Post-Resolution Validation

1. Run `git diff --check` to verify no conflict markers remain across all files
2. Ask user which validation checks they want to run using AskUserQuestion:
   - Format checking (Prettier, eslint --fix, etc.)
   - Linting
   - Type checking (tsc --noEmit, mypy, etc.)
   - Tests
   - Build
3. Run selected checks if user approves
4. Report results

## Step 7: Stage and Report

Stage all resolved files using `git add <filename>` for each resolved file.

Report:
- Number of files resolved
- Summary of changes per file
- Any files that need human review
- Next steps based on detected operation type:
  - **MERGING**: `git commit` to complete the merge
  - **REBASING**: `git rebase --continue` to continue the rebase
  - **CHERRY-PICKING**: `git cherry-pick --continue` to continue
  - **Unknown**: Show both merge and rebase options

Use the merge-conflicts skill for detailed resolution strategies.
