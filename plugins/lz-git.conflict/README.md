# LZ Git Conflict Resolver

A Claude Code plugin for autonomously resolving Git merge conflicts with smart semantic analysis.

## Features

- **Smart Merge Resolution**: Analyzes code semantically to intelligently combine changes
- **Multiple Resolution Modes**: Autonomous, interactive per-conflict, or batch with preview
- **Quick Resolution Commands**: Accept ours/theirs for entire branch when you know which is correct
- **Proactive Detection**: Automatically detects conflicts after git merge/pull/rebase
- **Safety First**: Creates backup branches before any resolution
- **Research-Based**: Conflict taxonomy based on academic research (ISSTA 2022, Ghiotto et al.)
- **Code-Focused**: Prioritizes source code with config file support
- **Lock File Handling**: Suggests regeneration for package-lock.json and similar files

## Commands

| Command | Description |
|---------|-------------|
| `/lz-git.conflict:resolve` | Resolve all conflicts with batch preview mode (default) |
| `/lz-git.conflict:resolve <file>` | Interactively resolve a single file's conflicts |
| `/lz-git.conflict:resolve -a` | Resolve all conflicts autonomously |
| `/lz-git.conflict:resolve -i` | Resolve all conflicts interactively (ask per conflict) |
| `/lz-git.conflict:accept-ours [file]` | Accept current branch version for all/specific conflicts |
| `/lz-git.conflict:accept-theirs [file]` | Accept incoming branch version for all/specific conflicts |
| `/lz-git.conflict:abort` | Abort conflict resolution and restore pre-conflict state |
| `/lz-git.conflict:status` | Show current conflict status |

### Resolution Modes

- **batch** (default): Show all proposed resolutions, ask for approval, then apply all at once
- **interactive** (`-i`): Ask for approval on each individual conflict before moving to next
- **autonomous** (`-a`): Resolve all conflicts automatically, report at end (no prompts)

## Agent

The `lz-git.conflict:conflict-resolver` agent can:
- Detect conflicts proactively after git operations
- Analyze conflict patterns and determine best resolution strategy
- Create backup branches before making changes
- Resolve conflicts autonomously or with user guidance

## Installation

Add to your Claude Code plugins:

```bash
claude --plugin-dir /path/to/lz-git.conflict
```

Or copy to your project's `.claude-plugin/` directory.

## Configuration

Create `.claude/lz-git.conflict.local.md` for custom settings:

```markdown
---
resolution-mode: batch
backup-branch-prefix: lz-git/conflict
lock-file-strategy: regenerate
enabled: true
---

# Conflict Resolution Preferences

Additional instructions for the conflict resolver agent.
```

### Configuration Options

| Setting | Values | Description |
|---------|--------|-------------|
| `resolution-mode` | `autonomous`, `interactive`, `batch` | How conflicts are resolved |
| `backup-branch-prefix` | String | Prefix for backup branches |
| `lock-file-strategy` | `skip`, `regenerate`, `simple` | How to handle lock files |
| `enabled` | `true`, `false` | Enable/disable proactive detection |

**Note:** After editing settings, restart Claude Code for changes to take effect.

## How It Works

1. **Detection**: After git operations (merge, pull, rebase), the plugin's hook detects if conflicts occurred
2. **Backup**: Before any resolution, a backup branch is created automatically
3. **Analysis**: Each conflict is analyzed semantically to understand what both branches intended
4. **Resolution**: Smart merge strategy combines changes intelligently based on file type
5. **Validation**: Resolved code is checked for remaining conflict markers and basic validity

## Conflict Types

Based on academic research, the plugin handles:

### Textual Conflicts (Immediate)
- **Content**: Same lines modified differently
- **Disjoint**: Parallel additions to same structure
- **Whitespace**: Formatting differences only

### Semantic Conflicts (Post-Merge)
- **Rename/Refactor**: Symbol renamed upstream, used downstream
- **API Change**: Method signatures changed
- **Structural**: File moves vs content changes
- **Entangled**: Complex intertwined changes (flagged for human review)

## Supported Git Operations

- `git merge`
- `git pull`
- `git rebase`
- `git cherry-pick`

## File Type Support

- **Source Code**: JS, TS, Python, Go, Rust, Java, C#, etc.
- **Config Files**: package.json, tsconfig.json, .env files
- **Lock Files**: package-lock.json, yarn.lock, pnpm-lock.yaml (regeneration suggested)

## Attribution

This plugin incorporates insights from:
- Zhang et al. (ISSTA 2022) - Textual and semantic merge conflict research
- Ghiotto et al. (IEEE TSE 2018) - Large-scale study of merge conflicts
- CuriousLearner/devkit - Conflict resolution patterns

See [ATTRIBUTIONS.md](ATTRIBUTIONS.md) for full details.

## License

MIT
