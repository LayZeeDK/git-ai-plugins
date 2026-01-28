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

## Hooks

### Environment Variables

`${CLAUDE_PLUGIN_ROOT}` is substituted by the plugin system in `hooks.json` but **NOT** in command markdown files with `!` backtick syntax. For commands, use inline approaches or the `date` command (available via Git Bash on all platforms).

### PostToolUse Hook Output

Two approaches for adding information after tool execution:

| Approach | Behavior |
|----------|----------|
| `additionalContext` | Claude "considers" it but may paraphrase |
| `decision: "block"` with `reason` | Claude is automatically prompted and acts on it |

Use `decision: "block"` when you need Claude to take specific action:

```json
{
  "decision": "block",
  "reason": "Describe what Claude should do or tell the user."
}
```

### Hook Input Formats

PostToolUse hooks may receive different input formats. Handle both:

```javascript
const result = input.tool_result || input.tool_response?.stdout || '';
```

### Cross-Platform Timestamps

For backup branches, use `date -u` which works on macOS, Linux, and Windows (via Git Bash):

```bash
git branch backup/operation-$(date -u +"%Y%m%d-%H%M%S")
```

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
