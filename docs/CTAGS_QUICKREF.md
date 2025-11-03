# Ctags Quick Reference

Quick command reference for ctags integration in this project.

## Generate Tags

```bash
# Full regeneration
npm run tags

# Incremental update (faster)
npm run tags:incremental

# With verbose output
npm run tags:verbose

# Direct script usage
./scripts/generate-tags.sh [--incremental] [--verbose]
```

## Install Git Hook (Auto-update)

```bash
# Copy hook to .git/hooks
cp scripts/hooks/post-commit .git/hooks/post-commit
chmod +x .git/hooks/post-commit

# Tags will now auto-update after each commit
```

## Vim Navigation

```vim
Ctrl-]          " Jump to definition
Ctrl-T          " Jump back
g]              " List if multiple matches
:tag <name>     " Jump to tag by name
:tn             " Next match
:tp             " Previous match
```

## VS Code

1. Install: `ext install hank.ctags`
2. Usage:
   - `Ctrl+]` - Jump to definition
   - `Ctrl+T` - Navigate back

## Emacs

```elisp
M-.             ; Find definition
M-*             ; Pop back
```

## Tag Statistics

Current project:
- **Total tags**: ~570+
- **Languages**: JavaScript, Shell, Markdown, JSON, YAML
- **Special**: Gemini test suites tagged

## Search Tags

```bash
# Find all functions
grep -E $'\t''f'$'\t' tags

# Find specific symbol
grep "^ExampleDriver" tags

# Find in specific file
grep "example-driver.js" tags
```

## Useful Tag Kinds

| Kind | Type | Example |
|------|------|---------|
| `c` | Class | `ExampleDriver` |
| `f` | Function | `buildUrl` |
| `m` | Method | `initialize` |
| `C` | Constant | `IMAGE_NAME` |
| `v` | Variable | `config` |
| `t` | Test Suite | `'Homepage'` |

## Common Issues

**Tags not found?**
```bash
# Regenerate
npm run tags

# Check file
ls -lh tags
wc -l tags
```

**Editor not working?**
- Check editor ctags plugin installed
- Verify tags file path in settings
- See [docs/EDITOR_CTAGS.md](EDITOR_CTAGS.md)

**Slow updates?**
```bash
# Use incremental mode
npm run tags:incremental
```

## Documentation

- [CTAGS.md](CTAGS.md) - Comprehensive guide
- [EDITOR_CTAGS.md](EDITOR_CTAGS.md) - Editor setup
- [.ctags.d/config.ctags](../.ctags.d/config.ctags) - Configuration

## Examples

### Jump to Gemini test suite
```bash
# In Vim, with cursor on test name:
Ctrl-]
```

### Find all test suites
```bash
grep -E "gemini\.suite" tags
```

### List all exported functions
```bash
grep -E "module\.exports|exports\." tags
```

---

**Pro tip**: Combine ctags with your editor's LSP for best results!
