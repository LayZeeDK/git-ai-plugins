# Post-Resolution Validation

Checklist and strategies for validating conflict resolutions.

## 1. Conflict Marker Verification (Always Run)

Detect conflict style and search for appropriate markers:

**Standard (merge style)**:
- `<<<<<<<` - Conflict start
- `=======` - Divider
- `>>>>>>>` - Conflict end

**diff3/zdiff3 style** (also check):
- `|||||||` - Common ancestor marker

**Search command**: `git diff --check` (detects leftover markers)

**Grep pattern for all styles**:
```
<<<<<<<|[|]{7}|=======|>>>>>>>
```

This covers all `merge.conflictstyle` settings (merge, diff3, zdiff3).

## 2. Syntax, Formatting, and Type Checking

Ask user which to run:

| Check | Common Commands |
|-------|-----------------|
| Formatter | `npm run format`, `npx prettier --write .`, `cargo fmt` |
| Linter | `npm run lint`, `eslint .`, `cargo clippy` |
| Type checker | `tsc --noEmit`, `mypy .`, `cargo check` |

**Note**: Formatting should generally be run after resolution to normalize any style differences introduced during the merge.

## 3. Test Validation

Ask user which to run:

| Test Type | Common Commands |
|-----------|-----------------|
| Unit tests | `npm test`, `pytest`, `cargo test` |
| Integration tests | `npm run test:integration` |
| E2E tests | `npm run test:e2e` |

**Important**: Test failures after a textually successful merge may indicate semantic conflicts (see conflict-patterns.md).

## 4. Build Validation

Ask user:

| Check | Common Commands |
|-------|-----------------|
| Build project | `npm run build`, `cargo build --release` |
| Check for new warnings | Review build output |

**Important**: Build failures after a textually successful merge often indicate:
- Renamed symbols not updated in all locations
- API signature changes not propagated
- Missing imports or exports

## 5. Manual Verification

Suggest to user:

- Review changed files: `git diff --cached`
- Test affected functionality manually
- Verify both feature intents are preserved
- Check for unintended side effects

## Validation Workflow

### Minimum Validation (Always)

1. Run `git diff --check` to verify no conflict markers remain
2. Review resolved files visually

### Recommended Validation

1. Conflict marker check
2. Type checking (if applicable)
3. Linting
4. Unit tests

### Full Validation

1. All of the above
2. Integration tests
3. Build
4. Manual testing of affected features

## Interpreting Failures

### Type/Compilation Errors After Merge

Likely causes:
- Renamed symbol not updated (semantic conflict type 4)
- API signature change not propagated (semantic conflict type 6)
- Missing import from one branch

Resolution: Check git log for upstream changes that may need propagation.

### Test Failures After Merge

Likely causes:
- Business logic conflict (both branches changed behavior)
- Missing test updates for new functionality
- Entangled changes (semantic conflict type 8)

Resolution: Understand what both branches intended and verify the merged behavior is correct.

### Build Warnings

May indicate:
- Unused imports (one branch removed usage, another added import)
- Deprecated API usage (one branch updated, another added old usage)

Resolution: Clean up based on intended final state.
