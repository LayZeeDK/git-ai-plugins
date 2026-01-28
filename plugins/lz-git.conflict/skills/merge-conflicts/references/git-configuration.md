# Git Configuration Reference

Read-only reference for Git configuration options related to conflict resolution.

**Note**: This plugin does NOT modify user's Git configuration. It reads settings to inform conflict display and uses per-command `-c` overrides when needed.

## Detecting Current Conflict Style

```bash
git config --get merge.conflictstyle
```

Returns one of: `merge` (default if unset), `diff3`, or `zdiff3`

## Conflict Styles Explained

### merge (default)

The standard two-way conflict display:

```
<<<<<<< HEAD
Current branch's version
=======
Incoming branch's version
>>>>>>> branch-name
```

**Pros**: Simpler, less noise
**Cons**: No visibility into what the original code looked like

### diff3

Adds a base section showing the common ancestor:

```
<<<<<<< HEAD
Current branch's version
||||||| merged common ancestors
Original version before either change
=======
Incoming branch's version
>>>>>>> branch-name
```

**Pros**: Shows what both branches changed from, easier to understand intent
**Cons**: More verbose

### zdiff3 (Git 2.35+)

"Zealous diff3" - enhanced version that trims common lines from conflict regions:

```
<<<<<<< HEAD
Current branch's version (trimmed)
||||||| merged common ancestors
Original version (trimmed)
=======
Incoming branch's version (trimmed)
>>>>>>> branch-name
```

**Pros**: Shorter conflicts, focuses on actual differences
**Cons**: Requires Git 2.35+

## Temporary Per-Command Overrides

Use diff3 style for a specific merge without changing global config:

```bash
git -c merge.conflictstyle=diff3 merge <branch>
```

Use zdiff3 for a rebase:

```bash
git -c merge.conflictstyle=zdiff3 rebase <branch>
```

## Conflict Markers by Style

| Style | Markers to Detect |
|-------|-------------------|
| merge | `<<<<<<<`, `=======`, `>>>>>>>` |
| diff3 | `<<<<<<<`, `|||||||`, `=======`, `>>>>>>>` |
| zdiff3 | `<<<<<<<`, `|||||||`, `=======`, `>>>>>>>` |

**Universal pattern** (detects all styles):
```
<<<<<<<|[|]{7}|=======|>>>>>>>
```

## How This Plugin Uses Configuration

1. **Detects current style** when displaying conflicts to provide context
2. **Parses all marker types** to support any configuration
3. **Informs user** what conflict style is in effect
4. **Suggests diff3/zdiff3** for users who frequently have complex conflicts (recommendation only)

## Recommendations for Users

If you frequently encounter complex conflicts where understanding both branches' changes from the original is helpful, consider setting diff3 or zdiff3:

```bash
# Set diff3 globally
git config --global merge.conflictstyle diff3

# Or set zdiff3 (Git 2.35+)
git config --global merge.conflictstyle zdiff3
```

This is a user preference - the plugin works with any setting.

## Other Useful Settings

### rerere (Reuse Recorded Resolution)

Automatically records and reuses conflict resolutions:

```bash
git config --global rerere.enabled true
```

When you resolve a conflict, Git remembers it. If you encounter the same conflict again (e.g., during a rebase), Git can automatically apply the same resolution.

### merge.conflictStyle vs merge.conflictstyle

Both work - Git config keys are case-insensitive. This documentation uses lowercase for consistency.

## References

- [Git merge-config documentation](https://git-scm.com/docs/merge-config)
- [Git merge-strategies documentation](https://git-scm.com/docs/merge-strategies)
