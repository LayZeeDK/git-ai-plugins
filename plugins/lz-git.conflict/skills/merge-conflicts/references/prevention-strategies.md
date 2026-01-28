# Conflict Prevention Strategies

When conflicts occur frequently, consider these practices.

**Note**: This plugin focuses on resolution, not enforcement. These are recommendations users can adopt as appropriate for their workflow.

## Development Workflow

### Sync Frequently

- Pull/rebase frequently to stay synchronized with the target branch
- The longer a branch lives, the more likely conflicts become
- Consider daily syncs for active development

### Keep Branches Short-Lived

- Smaller, focused branches mean fewer opportunities for conflicts
- Aim for branches that can be merged within days, not weeks
- Break large features into smaller, mergeable increments

### Avoid Mixing Concerns

- Don't combine unrelated changes on a single branch
- Formatting changes + feature changes = conflict magnets
- Refactoring + new features = difficult merges

## Team Coordination

### Communicate About Shared Files

- Let teammates know when you're modifying heavily-used files
- Coordinate timing for significant refactors
- Use feature flags to merge incomplete work safely

### Establish Code Ownership

- Clear ownership reduces conflicting modifications
- When multiple people need to edit the same area, coordinate

## Git Settings (User Choice)

Users may find these settings helpful:

### Default to Rebase on Pull

```bash
git config --global pull.rebase true
```

Keeps history linear, reduces merge commits that can cause conflicts.

### Enable rerere

```bash
git config --global rerere.enabled true
```

Git remembers conflict resolutions and can reapply them automatically.

### Use diff3 Conflict Style

```bash
git config --global merge.conflictstyle diff3
```

Shows the common ancestor in conflicts, making resolution easier.

## Architecture Decisions

### Modular Code Structure

- Smaller, focused modules have fewer cross-cutting changes
- Clear interfaces reduce ripple effects from changes

### Automated Formatting

- Use tools like Prettier, Black, gofmt
- Run formatters automatically via pre-commit hooks
- Eliminates whitespace/formatting conflicts entirely

### Lock File Strategy

- Commit lock files to avoid dependency conflicts
- Have clear policy on when to regenerate vs. merge

## When Conflicts Are Unavoidable

Some conflicts are inherent to the work:
- Multiple people genuinely need to modify the same code
- Large refactors that touch many files
- Infrastructure changes that affect shared configurations

In these cases, the goal shifts from prevention to **efficient resolution** - which is what this plugin provides.
