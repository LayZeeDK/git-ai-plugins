# LZ Git Conflict Resolver Plugin - Project Plan

## Plugin Identity

- **Name**: `lz-git.conflict`
- **Location**: `plugins/lz-git.conflict/`
- **Prefix**: `/lz-git.conflict:*`

## Activation Modes

| Mode | Trigger |
|------|---------|
| **On-demand** | Slash commands for manual invocation |
| **Proactive** | PostToolUse hook detects conflicts after `git merge/pull/rebase` |

## Resolution Modes

| Mode | Description |
|------|-------------|
| **Autonomous** | Resolve all conflicts automatically |
| **Interactive** | Ask for approval per conflict |
| **Batch-preview** | Show all proposed resolutions, then apply (default) |

## Commands

| Command | Description |
|---------|-------------|
| `/lz-git.conflict:status` | Show current conflict status |
| `/lz-git.conflict:resolve <file>` | Resolve single file interactively |
| `/lz-git.conflict:resolve-all` | Resolve all conflicts with batch preview |

## Components

| Type | Name | Purpose |
|------|------|---------|
| **Skill** | `merge-conflicts` | Conflict resolution strategies by file type |
| **Agent** | `conflict-resolver` | Autonomous conflict detection and resolution |
| **Hook** | PostToolUse (Bash) | Detect conflicts after git operations |

## Key Behaviors

| Behavior | Setting |
|----------|---------|
| **Merge strategy** | Smart semantic analysis (not line-level) |
| **Hook action** | Offer to resolve (not auto-start) |
| **Lock files** | Suggest regeneration |
| **Safety** | Always create backup branches before resolution |
| **Display** | Use fenced code blocks for conflict content |

## Supported File Types

- **Source code**: JS, TS, Python, Go, Rust, Java, C#, etc.
- **Config files**: package.json, tsconfig.json, .env files
- **Lock files**: package-lock.json, yarn.lock, pnpm-lock.yaml (regeneration suggested)

## Supported Git Operations

- `git merge`
- `git pull`
- `git rebase`

## Cross-Platform Compatibility

| Component | Implementation |
|-----------|----------------|
| Hook script | `hooks/scripts/detect-conflicts.js` (Node.js) |

Hook uses Node.js for Windows/PowerShell compatibility.

## Directory Structure

```
plugins/lz-git.conflict/
├── .claude-plugin/
│   └── plugin.json
├── .gitignore
├── README.md
├── PROJECT-PLAN.md
├── agents/
│   └── conflict-resolver.md
├── commands/
│   ├── resolve-all.md
│   ├── resolve.md
│   └── status.md
├── hooks/
│   ├── hooks.json
│   └── scripts/
│       └── detect-conflicts.js
└── skills/
    └── merge-conflicts/
        ├── SKILL.md
        ├── examples/
        │   ├── complex-rebase.md
        │   └── simple-merge.md
        └── references/
            ├── conflict-patterns.md
            └── file-type-strategies.md
```
