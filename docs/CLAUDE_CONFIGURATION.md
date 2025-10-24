# Claude Code Configuration Guide

This document explains the Claude Code configuration used in this project.

## Overview

Claude Code is used to assist with development tasks in this repository. The configuration is split between two locations:

1. **Root Configuration** (`/home/eirikr/Playground/.claude/settings.local.json`)
2. **Drivers Configuration** (`/home/eirikr/Playground/drivers/.claude/settings.local.json`)

## Configuration Files

### Root Configuration

**Location**: `.claude/settings.local.json`

```json
{
  "permissions": {
    "allow": [
      "Read(//mnt/**)",
      "Bash(mount:*)",
      "Read(//etc/**)",
      "Bash(lsblk:*)",
      "mcp__desktop-commander__list_directory",
      "Read(//home/eirikr/Projects/**)"
    ],
    "deny": [],
    "ask": []
  }
}
```

**Purpose**: Broad permissions for system-level operations

**Allowed Operations**:
- Read mounted filesystems (`/mnt/**`)
- Execute mount commands
- Read system configuration (`/etc/**`)
- List block devices (`lsblk`)
- Use Desktop Commander MCP server
- Read Projects directory

### Drivers Configuration

**Location**: `drivers/.claude/settings.local.json`

```json
{
  "permissions": {
    "allow": [
      "Read(//home/eirikr/**)"
    ],
    "deny": [],
    "ask": []
  }
}
```

**Purpose**: Restricted permissions for driver-specific work

**Allowed Operations**:
- Read files in home directory only

## Why Two Configurations?

### Separation of Concerns

1. **Root level**: System administration and broad project management
2. **Drivers level**: Focused on driver implementation only

### Security

- Drivers directory has more restrictive permissions
- Prevents accidental system modifications from driver context
- Follows principle of least privilege

## Permission Patterns

### Read Permissions

```json
"Read(//path/pattern/**)"
```

- Allows reading files matching the pattern
- `**` = recursive wildcard

### Bash Permissions

```json
"Bash(command:*)"
```

- Allows executing specific bash commands
- `*` = any arguments

### MCP Server Permissions

```json
"mcp__server-name__tool-name"
```

- Allows using specific MCP server tools
- Format: `mcp__<server>__<tool>`

## Best Practices

### 1. Principle of Least Privilege

Only grant permissions that are actually needed:

```json
// Good: Specific path
"Read(//home/eirikr/Playground/**)"

// Avoid: Too broad
"Read(//**)"
```

### 2. Use Deny for Sensitive Areas

```json
{
  "permissions": {
    "allow": ["Read(//home/eirikr/**)"],
    "deny": [
      "Read(//home/eirikr/.ssh/**)",
      "Read(//home/eirikr/.gnupg/**)"
    ]
  }
}
```

### 3. Ask for Dangerous Operations

```json
{
  "permissions": {
    "ask": [
      "Bash(rm:*)",
      "Bash(mv:*)",
      "Write(/etc/**)"
    ]
  }
}
```

## Common Permission Sets

### Development Project

```json
{
  "permissions": {
    "allow": [
      "Read(//home/user/project/**)",
      "Write(//home/user/project/**)",
      "Bash(npm:*)",
      "Bash(git:*)",
      "Bash(docker:*)"
    ],
    "deny": [
      "Write(//home/user/project/.git/config)"
    ],
    "ask": [
      "Bash(rm:*)"
    ]
  }
}
```

### Documentation Only

```json
{
  "permissions": {
    "allow": [
      "Read(//home/user/docs/**)",
      "Write(//home/user/docs/**)"
    ],
    "deny": [],
    "ask": []
  }
}
```

### System Analysis

```json
{
  "permissions": {
    "allow": [
      "Read(//etc/**)",
      "Read(//var/log/**)",
      "Bash(systemctl:status *)",
      "Bash(journalctl:*)",
      "Bash(df:*)",
      "Bash(free:*)"
    ],
    "deny": [
      "Bash(systemctl:start *)",
      "Bash(systemctl:stop *)"
    ],
    "ask": []
  }
}
```

## MCP Server Integration

### Desktop Commander

This project uses the Desktop Commander MCP server for enhanced file operations.

**Enabled Tools**:
- `list_directory` - List directory contents with enhanced formatting

**Configuration**:
```json
"allow": [
  "mcp__desktop-commander__list_directory"
]
```

### Adding More MCP Tools

To allow additional MCP tools:

```json
"allow": [
  "mcp__desktop-commander__read_file",
  "mcp__desktop-commander__write_file",
  "mcp__desktop-commander__search_files"
]
```

## Updating Configuration

### Local Changes

1. Edit `.claude/settings.local.json`
2. Changes take effect immediately
3. Not tracked in git (in `.gitignore`)

### Project Defaults

To set project-wide defaults:

1. Create `.claude/settings.json` (without `.local`)
2. Commit to repository
3. Team members can override locally

## Troubleshooting

### Permission Denied Errors

**Symptom**: Claude reports permission denied

**Solution**:
1. Check which operation failed
2. Add permission to `allow` array
3. Reload Claude Code

### Too Permissive

**Symptom**: Security concerns about broad permissions

**Solution**:
1. Review permissions regularly
2. Move sensitive operations to `ask`
3. Use more specific path patterns

### Conflicting Configurations

**Symptom**: Unclear which configuration applies

**Resolution Order**:
1. Most specific path wins
2. `.local.json` overrides `.json`
3. Child directory config overrides parent

## Security Considerations

### Sensitive Files

Always deny access to:
- SSH keys (`~/.ssh/**`)
- GPG keys (`~/.gnupg/**`)
- Password stores (`~/.password-store/**`)
- Environment files with secrets (`.env`)

### Destructive Commands

Use `ask` permission for:
- `rm` - Delete files
- `mv` - Move files
- `chmod` - Change permissions
- `chown` - Change ownership

### Network Operations

Consider restricting:
- `curl` - Network requests
- `wget` - File downloads
- `ssh` - Remote connections

## Example Scenarios

### Scenario 1: New Developer Onboarding

```json
{
  "permissions": {
    "allow": [
      "Read(//home/newdev/playground/**)",
      "Bash(git:status)",
      "Bash(git:log)",
      "Bash(npm:install)",
      "Bash(docker:ps)"
    ],
    "deny": [
      "Bash(git:push *)"
    ],
    "ask": [
      "Bash(git:commit *)"
    ]
  }
}
```

**Rationale**: Read-only + safe commands, ask before commits

### Scenario 2: Refactoring Task

```json
{
  "permissions": {
    "allow": [
      "Read(//home/dev/playground/**)",
      "Write(//home/dev/playground/src/**)",
      "Bash(npm:test)"
    ],
    "deny": [
      "Write(//home/dev/playground/package.json)",
      "Write(//home/dev/playground/.git/**)"
    ],
    "ask": []
  }
}
```

**Rationale**: Can modify source but not configuration

### Scenario 3: Documentation Work

```json
{
  "permissions": {
    "allow": [
      "Read(//home/dev/playground/**)",
      "Write(//home/dev/playground/docs/**)",
      "Write(//home/dev/playground/README.md)"
    ],
    "deny": [],
    "ask": []
  }
}
```

**Rationale**: Only documentation changes allowed

## References

- [Claude Code Documentation](https://docs.claude.com/claude-code)
- [MCP Protocol Specification](https://modelcontextprotocol.io)
- [Desktop Commander MCP Server](https://github.com/eirikr/desktop-commander)

---

**Last Updated**: 2025-10-24
**Version**: 1.0.0
