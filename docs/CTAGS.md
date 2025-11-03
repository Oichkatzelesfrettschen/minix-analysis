# Ctags Integration Guide

This document describes the ctags integration in the project and how to use it for efficient code navigation.

## Overview

Universal Ctags is integrated into this project to provide powerful code navigation capabilities. Tags are automatically generated for JavaScript, Shell scripts, Markdown, JSON, YAML, and Dockerfiles.

## Features

- **Automatic tag generation** on `npm install` via postinstall hook
- **Incremental updates** for faster tag regeneration
- **Multi-language support** for all project file types
- **Editor integration** with Vim, Emacs, VS Code, and more
- **Custom patterns** for project-specific constructs (Gemini test suites)

## Quick Start

### Generate Tags

```bash
# Generate tags file (from scratch)
npm run tags

# Generate with verbose output
npm run tags:verbose

# Incremental update (faster)
npm run tags:incremental

# Or use the script directly
./scripts/generate-tags.sh [--verbose] [--incremental]
```

### Tag Statistics

After generation, you'll see output like:

```
[ctags] Tags generated successfully!
[ctags]   Tags file: /path/to/project/tags
[ctags]   Total tags: 491
[ctags]   Time: 0s
```

## Editor Integration

### Vim/Neovim

Tags work out of the box in Vim:

```vim
" Jump to tag under cursor
Ctrl-]

" Jump back
Ctrl-T

" Search for tag
:tag <name>

" List all tags
:tags

" Split window and jump to tag
Ctrl-W ]
```

Add to your `.vimrc` for enhanced navigation:

```vim
" Set tags file location
set tags=./tags,tags;$HOME

" Enable tag completion
set complete+=t

" Show tag preview window
set completeopt+=preview
```

### VS Code

Install the **ctags** extension:

1. Open VS Code
2. Press `Ctrl+P` (or `Cmd+P` on macOS)
3. Type: `ext install hank.ctags`
4. Reload VS Code

Usage in VS Code:

- `Ctrl+T` - Search for tag
- `Alt+.` - Jump to definition
- `Alt+,` - Jump back

### Emacs

Add to your `.emacs` or `init.el`:

```elisp
;; Load tags file
(setq tags-file-name "/path/to/project/tags")

;; Or auto-find tags in project
(defun my-find-tag ()
  "Find TAGS file in current directory tree."
  (let ((tag-file (locate-dominating-file default-directory "tags")))
    (when tag-file
      (visit-tags-table (expand-file-name "tags" tag-file)))))

(add-hook 'find-file-hook 'my-find-tag)
```

Usage:

- `M-.` - Find tag
- `M-*` - Pop back to previous location
- `M-x tags-search` - Search for regexp in tagged files

### Sublime Text

1. Install **CTags** package via Package Control
2. Open project settings: `Project > Edit Project`
3. Add:

```json
{
  "settings": {
    "ctags": {
      "tag_file": "tags"
    }
  }
}
```

Usage:

- `Ctrl+T, Ctrl+T` - Jump to definition
- `Ctrl+T, Ctrl+B` - Jump back
- `Ctrl+T, Ctrl+R` - Rebuild tags

### Atom

Install the **atom-ctags** package:

```bash
apm install atom-ctags
```

Usage:

- `Ctrl+Alt+Down` - Go to declaration
- `Ctrl+Alt+Up` - Return from declaration

## Configuration

### Custom Patterns

The `.ctags.d/config.ctags` file contains custom patterns for this project:

- **Gemini test suites**: Recognizes `gemini.suite()` calls
- **Arrow functions**: Enhanced detection of ES6 arrow functions
- **Module exports**: Captures CommonJS exports

### Excluded Files/Directories

The following are automatically excluded from tagging:

- `node_modules/` - Dependencies
- `.git/` - Git metadata
- `dist/`, `build/` - Build artifacts
- `coverage/`, `.nyc_output/` - Test coverage
- `gemini-report/` - Test reports
- `logs/` - Log files
- `*.min.js`, `*.map` - Minified/source map files
- `package-lock.json` - Lock files

## Tag File Format

The generated `tags` file uses the extended ctags format with additional fields:

- **Line numbers**: Quick jump to exact location
- **Signatures**: Function parameters for better context
- **Scopes**: Class/module membership information
- **Kinds**: Tag types (function, class, method, etc.)

Example tag entry:

```
buildUrl	drivers/example-driver.js	/^  buildUrl(path) {$/;"	m	line:53	language:JavaScript	class:ExampleDriver	signature:(path)
```

## Automated Updates

### Post-install Hook

Tags are automatically generated after `npm install`:

```json
"postinstall": "npm run tags || true"
```

The `|| true` ensures installation doesn't fail if ctags isn't available.

### Git Hooks (Recommended)

For automatic tag updates on file changes, add a post-commit hook:

```bash
# .git/hooks/post-commit
#!/bin/sh
npm run tags:incremental > /dev/null 2>&1 &
```

Make it executable:

```bash
chmod +x .git/hooks/post-commit
```

### Watch Mode (Development)

For continuous tag updates during development:

```bash
# Install inotify-tools (Linux) or fswatch (macOS)
# Ubuntu/Debian:
sudo apt-get install inotify-tools

# macOS:
brew install fswatch

# Watch and update tags
while inotifywait -r -e modify,create,delete .; do
  npm run tags:incremental
done
```

## Supported Tag Types

### JavaScript

- `c` - Classes
- `f` - Functions (named, arrow, async)
- `m` - Methods (including getters/setters)
- `v` - Variables
- `C` - Constants
- `M` - Module exports
- `t` - Test suites (Gemini-specific)

### Shell Scripts

- `f` - Functions
- `v` - Variables

### Markdown

- `c` - Chapters (level 1 headers)
- `s` - Sections (level 2+ headers)
- `S` - Subsections
- `t` - Subsubsections

### JSON

- `o` - Objects
- `a` - Arrays
- `s` - String values

### YAML

- `a` - Anchors

### Dockerfile

- Standard Dockerfile constructs

## Troubleshooting

### Tags not generating

Check if Universal Ctags is installed:

```bash
ctags --version
```

Should show "Universal Ctags". If not, install it:

```bash
# Ubuntu/Debian
sudo apt-get install universal-ctags

# macOS
brew install universal-ctags

# From source
git clone https://github.com/universal-ctags/ctags.git
cd ctags
./autogen.sh
./configure
make
sudo make install
```

### Editor not finding tags

1. Ensure tags file exists: `ls -lh tags`
2. Check editor configuration (see Editor Integration above)
3. Try absolute path to tags file in editor settings

### Tags outdated

Regenerate tags:

```bash
npm run tags
```

Or enable automatic updates (see Automated Updates above).

### Performance issues

For large projects, use incremental updates:

```bash
npm run tags:incremental
```

This is much faster than regenerating all tags.

## Advanced Usage

### Search Tags

Search for specific tags:

```bash
# Find all functions named 'test'
grep -E "^test.*\tf\t" tags

# Find all classes
grep -E "\tc\t" tags

# Find tags in specific file
grep "example-driver.js" tags
```

### Multiple Tag Files

Use multiple tag files for project dependencies:

```vim
" In .vimrc
set tags=./tags,tags,../tags,../../tags
```

### Tag Stack Navigation

Most editors maintain a tag stack for navigation history:

- Jump to tag: adds to stack
- Jump back: pops from stack
- Multiple jumps create navigation history

## Integration with Build Tools

### Webpack/Build Process

Add to package.json scripts:

```json
{
  "scripts": {
    "prebuild": "npm run tags",
    "build": "webpack --config webpack.config.js"
  }
}
```

### CI/CD Pipeline

Generate tags in CI for documentation:

```yaml
# .github/workflows/docs.yml
- name: Generate tags
  run: |
    sudo apt-get install -y universal-ctags
    npm run tags
    # Upload tags file as artifact
```

## Best Practices

1. **Commit `.ctags.d/config.ctags`** - Share configuration with team
2. **Don't commit `tags` file** - Add to `.gitignore` (already done)
3. **Update regularly** - Run `npm run tags:incremental` frequently
4. **Use with LSP** - Ctags complements Language Server Protocol
5. **Configure editor** - Set up keybindings for efficient navigation

## Resources

- [Universal Ctags](https://ctags.io/) - Official documentation
- [Vim Tags Guide](https://vim.fandom.com/wiki/Browsing_programs_with_tags)
- [Ctags Patterns](http://ctags.sourceforge.net/ctags.html) - Pattern syntax

## Project-Specific Tags

### Gemini Test Suites

Gemini test suites are tagged with type `t`:

```bash
# Find all test suites
grep -E "\tt\t.*gemini/tests" tags
```

Jump to test suite by name in your editor!

---

**Note**: Tags enhance code navigation but don't replace modern LSP features. Use them together for the best experience.
