# Agents Guide

Guidelines for Claude when developing and maintaining plugins in this repository.

## Repository Purpose

A collection of Claude Code plugins focused on Git workflow automation. All plugins are Git/version control related.

## Platform Requirements

Plugins must support macOS, Linux, and Windows. You can assume:

- Node.js LTS is installed
- Git Bash is available on Windows via the Bash tool
- The `claude` CLI runs from PowerShell on Windows

Use Node.js scripts for cross-platform operations rather than shell-specific commands.

## Development Tooling

Use the `plugin-dev` Claude plugin to create and maintain plugins:

```
/plugin install plugin-dev@claude-plugins-official
```

## Plugin Architecture

### Directory Structure

Each plugin follows this structure:

```
plugins/<plugin-name>/
├── .claude-plugin/
│   └── plugin.json        # Plugin metadata and version
├── README.md              # User-facing documentation
├── agents/                # AI agent definitions
├── commands/              # Slash commands
├── hooks/
│   ├── hooks.json         # Hook configuration
│   └── scripts/           # Hook implementation scripts
└── skills/
    └── <skill-name>/
        ├── SKILL.md       # Skill definition
        ├── references/    # Reference documentation
        └── examples/      # Usage examples
```

### Conventions

**Tool Restrictions**: Commands should use `allowed-tools` to restrict available tools and prevent unintended modifications.

**Arguments**: Use `argument-hint` to document expected arguments. Parse values from `$ARGUMENTS`.

**Safety**: Always create backup branches before destructive operations using UTC timestamps: `backup/<operation>-YYYYMMDD-HHMMSS`

**Output Formatting**: Use fenced markdown code blocks with language identifiers for syntax highlighting.

**File Type Awareness**: Handle different file types appropriately (source code, config files, lock files, etc.).

## Code Style

- Use Node.js for scripts requiring cross-platform compatibility
- Prefer semantic analysis over pattern matching when resolving conflicts
- Flag uncertain situations for human review rather than guessing
- Keep commands focused on single responsibilities

## Testing Changes

After modifying plugin files, verify:

1. Scripts execute correctly on the current platform
2. Hook configurations are valid JSON
3. Markdown files render correctly
4. Commands work with expected arguments
