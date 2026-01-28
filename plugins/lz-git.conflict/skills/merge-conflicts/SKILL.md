---
name: LZ Git Merge Conflict Resolution
description: This skill should be used when the user asks to "resolve merge conflicts", "fix git conflicts", "handle rebase conflicts", "resolve conflicting files", "merge conflict help", or when Claude detects conflict markers (<<<<<<< HEAD) in files. Provides strategies for semantic code merging and conflict resolution.
version: 0.1.0
---

# Git Merge Conflict Resolution

## Overview

This skill provides knowledge and strategies for resolving Git merge conflicts intelligently. Rather than blindly choosing "ours" or "theirs", analyze conflicts semantically to produce correct, working code that incorporates intent from both sides.

## Conflict Marker Format

Git marks conflicts with these markers (standard `merge` style):

```
<<<<<<< HEAD (or current branch name)
Current branch's version of the code
=======
Incoming branch's version of the code
>>>>>>> branch-name (or commit hash)
```

With `diff3` or `zdiff3` conflict style (`merge.conflictstyle` config), a base section is included:

```
<<<<<<< HEAD
Current branch's version
||||||| base (common ancestor)
Original version before either branch changed it
=======
Incoming branch's version
>>>>>>> branch-name
```

The `zdiff3` style (Git 2.35+) is "zealous" - it trims common lines from the conflict region, making conflicts shorter.

**All conflict markers to detect:** `<<<<<<<`, `|||||||`, `=======`, `>>>>>>>`

For rebase conflicts, the meanings are reversed:
- `HEAD` contains the branch being rebased onto (the "new base")
- The incoming section contains the commits being replayed

## Resolution Strategy: Smart Merge

### Step 1: Create Backup Branch

Before any resolution, create a backup. First get the current branch name, then create backup:

```bash
git rev-parse --abbrev-ref HEAD
# Returns: <branch-name>

date -u +"%Y%m%d-%H%M%SZ"
# Returns: <timestamp>

git branch lz-git/conflict/<branch-name>/backup-<timestamp>
```

### Step 2: Identify All Conflicts

List all conflicted files:

```bash
git diff --name-only --diff-filter=U
```

### Step 3: Analyze Each Conflict

For each conflicted file:

1. **Read the entire file** to understand context
2. **Identify conflict sections** by finding `<<<<<<<` markers
3. **Understand both versions**:
   - What does the current branch's code do?
   - What does the incoming branch's code do?
   - Are they modifying the same logic or different aspects?

### Step 4: Apply Resolution Strategy

Choose the appropriate strategy based on conflict type:

| Conflict Type | Strategy |
|---------------|----------|
| Same function, different changes | Merge logic from both sides |
| Added vs modified | Include addition and modification |
| Renamed vs modified | Apply modification to renamed version |
| Formatting only | Choose either (prefer incoming for consistency) |
| Import statements | Combine unique imports |
| Config values | Prefer incoming unless clearly wrong |

### Step 5: Validate Resolution

After resolving:

1. Remove all conflict markers
2. Ensure code is syntactically valid
3. Check that both intended changes are preserved
4. Run linter/type checker if available

### Step 6: Stage and Continue

```bash
git add <resolved-file>
# For merge: git commit (or let merge complete)
# For rebase: git rebase --continue
```

## File Type Strategies

### Source Code Files

Analyze semantically:
- Function signatures: combine parameter additions
- Import statements: union of both sets
- Variable declarations: check for conflicts in usage
- Class members: merge non-overlapping additions

### Configuration Files (JSON, YAML)

- Merge object properties from both sides
- For arrays, consider if order matters
- For version bumps, take the higher version
- For dependency versions, prefer incoming (newer)

### Package Lock Files

Do not attempt to merge. Instead:

1. Accept either version (prefer incoming)
2. Delete the lock file
3. Regenerate: `npm install`, `yarn install`, or `pnpm install`

### Markdown/Documentation

- For prose: carefully read both and combine
- For lists: union of items
- For code examples: ensure they match actual code

## Common Conflict Patterns

### Pattern 1: Parallel Feature Additions

Both branches added different features to the same file location.

**Resolution**: Include both additions in a sensible order.

### Pattern 2: Formatting vs Logic Change

One branch reformatted code, another changed logic.

**Resolution**: Apply logic change to reformatted code.

### Pattern 3: Dependency Version Conflicts

Both branches updated the same dependency to different versions.

**Resolution**: Use the higher version (unless breaking changes known).

### Pattern 4: Import Statement Conflicts

Both branches added different imports.

**Resolution**: Include all unique imports, sort alphabetically.

### Pattern 5: Function Signature Changes

Both branches modified the same function signature.

**Resolution**: Analyze parameter usage throughout codebase to determine correct signature.

## Resolution Modes

### Autonomous Mode

Resolve all conflicts without user interaction:

1. Create backup branch
2. Analyze all conflicts
3. Apply smart merge strategy
4. Stage resolved files
5. Report what was done

### Interactive Mode

For each conflict:

1. Show both versions with context
2. Explain what each side does
3. Propose resolution
4. Wait for user approval or adjustment
5. Apply approved resolution

### Batch Preview Mode

1. Analyze all conflicts
2. Generate proposed resolutions
3. Present summary of all proposed changes
4. Apply after user approves entire batch

## Error Handling

### When Smart Merge Fails

If unable to determine correct resolution:

1. Flag the conflict as needing human review
2. Explain why automatic resolution isn't safe
3. Show both versions clearly
4. Suggest possible approaches

### Validation Failures

If resolved code doesn't pass validation:

1. Report the specific error
2. Re-analyze the conflict
3. Propose alternative resolution
4. Ask for user guidance if still failing

## Additional Resources

### Reference Files

For detailed patterns and edge cases:
- **`references/conflict-patterns.md`** - Comprehensive conflict pattern catalog
- **`references/file-type-strategies.md`** - Detailed per-file-type resolution strategies

### Example Files

Working resolution examples:
- **`examples/simple-merge.md`** - Basic conflict resolution walkthrough
- **`examples/complex-rebase.md`** - Multi-file rebase conflict resolution
