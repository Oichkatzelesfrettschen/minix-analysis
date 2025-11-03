# Editor Configuration for Ctags

Quick setup guides for popular editors to use ctags in this project.

## Vim/Neovim

### Basic Setup

Add to your `.vimrc` or `~/.config/nvim/init.vim`:

```vim
" Set tags file search path
set tags=./tags,tags;$HOME

" Enable tag-based completion
set complete+=t

" Show tag preview in completion menu
set completeopt+=preview

" Key mappings
nnoremap <leader>] :tag <C-R><C-W><CR>
nnoremap <leader>[ :pop<CR>
```

### Advanced Setup with Plugins

Using **vim-plug**:

```vim
Plug 'ludovicchabant/vim-gutentags'  " Automatic tag management
Plug 'majutsushi/tagbar'              " Tag browser sidebar
Plug 'universal-ctags/ctags'          " Ctags integration

" Gutentags configuration
let g:gutentags_ctags_tagfile = 'tags'
let g:gutentags_cache_dir = expand('~/.cache/vim/ctags/')

" Tagbar configuration
nmap <F8> :TagbarToggle<CR>
let g:tagbar_autofocus = 1
let g:tagbar_width = 30
```

### Navigation Commands

| Command | Action |
|---------|--------|
| `Ctrl-]` | Jump to definition |
| `Ctrl-T` | Jump back |
| `g]` | Show list if multiple matches |
| `:tag <name>` | Jump to tag by name |
| `:tn` | Next tag match |
| `:tp` | Previous tag match |
| `:ts` | List all tag matches |

## VS Code

### Extension

Install **ctags** extension:

```
ext install hank.ctags
```

### Settings

Add to `settings.json`:

```json
{
  "ctags.file": "${workspaceFolder}/tags",
  "ctags.languages": ["javascript", "shellscript", "markdown"],
  "ctags.regenerateOnSave": true
}
```

### Keybindings

Add to `keybindings.json`:

```json
[
  {
    "key": "ctrl+]",
    "command": "ctags.navigateToDefinition"
  },
  {
    "key": "ctrl+t",
    "command": "workbench.action.navigateBack"
  }
]
```

## Emacs

### Setup

Add to `~/.emacs` or `~/.emacs.d/init.el`:

```elisp
;; Auto-load tags file from project root
(defun my-find-tags-file ()
  "Find and load tags file in project root."
  (let ((tag-file (locate-dominating-file default-directory "tags")))
    (when tag-file
      (setq tags-file-name (expand-file-name "tags" tag-file))
      (visit-tags-table tags-file-name))))

(add-hook 'find-file-hook 'my-find-tags-file)

;; Enhanced tag navigation
(global-set-key (kbd "M-.") 'xref-find-definitions)
(global-set-key (kbd "M-*") 'pop-tag-mark)
(global-set-key (kbd "M-,") 'xref-pop-marker-stack)

;; Tag completion
(setq tags-add-tables t)
(setq tags-revert-without-query t)
```

### With Counsel/Ivy

```elisp
(use-package counsel
  :config
  (global-set-key (kbd "M-.") 'counsel-etags-find-tag-at-point))
```

### Navigation

| Binding | Action |
|---------|--------|
| `M-.` | Find definition |
| `M-*` | Pop back |
| `M-,` | Pop marker stack |
| `M-x tags-search` | Search in tags |

## Sublime Text

### Package Installation

1. Install Package Control (if needed)
2. `Ctrl+Shift+P` → "Package Control: Install Package"
3. Search for "CTags"
4. Install

### Project Settings

Create `.sublime-project`:

```json
{
  "folders": [
    {
      "path": "."
    }
  ],
  "settings": {
    "ctags": {
      "tag_file": "tags",
      "command": "ctags",
      "opts": ["--options=.ctags.d/config.ctags"]
    }
  }
}
```

### Keybindings

| Binding | Action |
|---------|--------|
| `Ctrl+T, Ctrl+T` | Navigate to definition |
| `Ctrl+T, Ctrl+B` | Jump back |
| `Ctrl+T, Ctrl+R` | Rebuild tags |
| `Ctrl+T, Ctrl+S` | Show symbols |

## Atom

### Installation

```bash
apm install atom-ctags
```

### Configuration

Settings → Packages → atom-ctags:

- Tag file: `tags`
- Auto-generate on save: `true`
- Build on project open: `true`

### Keybindings

Add to `keymap.cson`:

```cson
'atom-workspace atom-text-editor':
  'ctrl-]': 'atom-ctags:go-to-declaration'
  'ctrl-t': 'atom-ctags:return-from-declaration'
  'ctrl-alt-down': 'atom-ctags:toggle-file-symbols'
```

## JetBrains IDEs (WebStorm, IntelliJ)

### Built-in Support

JetBrains IDEs have built-in ctags support:

1. File → Settings → Editor → General → Smart Keys
2. Enable "Jump to source" navigation

### External Tags

Settings → Editor → Code Editing → Ctags:

- Enable ctags support
- Set tags file path: `${PROJECT_DIR}/tags`

### Navigation

| Shortcut | Action |
|----------|--------|
| `Ctrl+B` | Go to declaration |
| `Ctrl+Alt+Left` | Navigate back |
| `Ctrl+N` | Go to class |
| `Ctrl+Shift+N` | Go to file |

## Helix

### Configuration

Add to `~/.config/helix/config.toml`:

```toml
[editor]
gutters = ["diagnostics", "line-numbers", "spacer", "diff"]

[editor.lsp]
enable = true

# Ctags integration
[editor.file-picker]
hidden = false
```

Helix uses LSP primarily, but can integrate with ctags through custom scripts.

## Common Workflows

### Jump to Definition

All editors support jumping to definition:

1. Place cursor on symbol
2. Press jump-to-definition key
3. Editor opens file at definition

### Navigate Back

Return to previous location after jumping:

- Most editors: `Ctrl+T` or `Alt+Left`
- Stack-based navigation through multiple jumps

### Search for Symbol

Find all occurrences:

1. Open tag search (varies by editor)
2. Type symbol name
3. Select from list

### Update Tags

After code changes:

```bash
npm run tags:incremental
```

Or set up auto-update (see main CTAGS.md guide).

## Tips

1. **Multiple matches**: When multiple definitions exist, most editors show a list
2. **Fuzzy search**: Many editors support fuzzy tag matching
3. **Tag stack**: Navigate through jump history with back/forward
4. **Preview**: Some editors show definition preview before jumping
5. **Auto-complete**: Tags enable symbol completion in many editors

## Troubleshooting

### Tags not working

1. Verify tags file exists: `ls -lh tags`
2. Check editor settings point to correct tags file
3. Reload/restart editor after generating tags
4. Check editor documentation for ctags support

### Slow navigation

1. Use incremental updates: `npm run tags:incremental`
2. Exclude more directories in `.ctags.d/config.ctags`
3. Consider using LSP for large projects

### Conflicts with LSP

Most editors can use both ctags and LSP:

- LSP for intelligent completion and refactoring
- Ctags for fast, reliable navigation
- Configure keybindings to avoid conflicts

---

For more information, see [docs/CTAGS.md](CTAGS.md) in the project documentation.
