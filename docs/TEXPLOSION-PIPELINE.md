# 💥 The TeXplosion Pipeline

## What is TeXplosion?

**TeXplosion** is the moment when your GitHub repository transforms from source code into *math art on the web* — a continuous publication pipeline that automatically:

1. **Analyzes** MINIX 3.4.0 source code
2. **Generates** TikZ/PGFPlots diagrams from data
3. **Compiles** LaTeX whitepaper with all visualizations
4. **Publishes** the rendered documentation to GitHub Pages

This is **"CI-as-Publication"** or **"Docs-as-Code"** taken to the extreme: every commit can potentially update a live, publication-quality technical whitepaper.

## The Pipeline Architecture

### Overview

```
┌─────────────┐
│ Git Push    │
│ (main)      │
└──────┬──────┘
       │
       ├─────────────────┬─────────────────┬──────────────────┐
       ▼                 ▼                 ▼                  ▼
┌─────────────┐   ┌─────────────┐  ┌──────────────┐  ┌──────────────┐
│ Analysis &  │   │  MINIX      │  │   LaTeX      │  │  MkDocs      │
│ Diagrams    │   │  Build      │  │ Compilation  │  │   Build      │
│             │   │  (QEMU)     │  │              │  │              │
└──────┬──────┘   └──────┬──────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │                  │
       └─────────────────┴─────────────────┴──────────────────┘
                                  │
                                  ▼
                         ┌────────────────┐
                         │  GitHub Pages  │
                         │   Deployment   │
                         └────────────────┘
                                  │
                                  ▼
                         🎉 TEXPLOSION! 🎉
```

### The Five Stages

#### Stage 1: Analysis & Diagram Generation

**Job:** `generate-diagrams`

- Runs Python analysis tools on MINIX source code
- Generates data files (JSON, CSV) with metrics
- Creates TikZ/PGFPlots `.tex` files from data
- Compiles diagrams to PDF, PNG, and SVG
- Uses ImageMagick for format conversion

**Key Technologies:**
- Python 3.9+
- TexLive (LaTeX distribution)
- TikZ/PGFPlots
- ImageMagick
- pdf2svg

**Outputs:**
- Individual diagram PDFs
- Web-optimized PNGs
- Scalable SVGs

#### Stage 2: MINIX Build (Optional)

**Job:** `build-minix`

This is the *intense* part of the workflow:

1. **Docker Container** builds the MINIX build environment
2. **QEMU i386** boots a virtual machine
3. **MINIX 3.4.0RC6** runs inside QEMU
4. **Source Build** compiles the MINIX kernel and userland
5. **Measurements** are extracted for analysis

**Why This Matters:**
- Real build data informs the whitepaper
- Boot metrics are captured automatically
- Performance measurements are reproducible
- The analysis reflects *actual* system behavior

**Time:** 60-90 minutes (only runs on demand)

**Outputs:**
- Build logs
- Performance measurements
- Boot sequence data
- System metrics

#### Stage 3: LaTeX Compilation

**Job:** `compile-latex`

The heart of the TeXplosion:

1. Downloads generated diagrams
2. Assembles LaTeX sources from `whitepaper/` and `latex/`
3. Uses `latexmk` for comprehensive compilation
4. Handles bibliographies, cross-references, TikZ includes
5. Generates publication-quality PDF

**Features:**
- Multiple LaTeX documents supported
- Automatic reference resolution
- Bibliography management (BibTeX/Biber)
- Error tolerance with detailed logs

**Main Document:**
- `MINIX-3.4-Comprehensive-Technical-Analysis.tex`
- 300+ pages of technical analysis
- Integrated TikZ diagrams
- Professional typography

**Outputs:**
- `MINIX-Analysis-Whitepaper.pdf` (main output)
- Additional PDFs for modular documents
- Compilation report with metadata

#### Stage 4: GitHub Pages Site Build

**Job:** `build-pages`

Creates a beautiful landing page:

1. Builds MkDocs documentation site
2. Copies compiled PDFs to `/pdfs/`
3. Creates diagram gallery at `/diagrams/`
4. Generates animated landing page
5. Assembles complete site structure

**Site Structure:**
```
pages/
├── index.html          # Animated landing page
├── pdfs/
│   └── MINIX-Analysis-Whitepaper.pdf
├── diagrams/
│   ├── index.html      # Diagram gallery
│   ├── *.png
│   ├── *.svg
│   └── *.pdf
└── docs/               # MkDocs output
    └── ...
```

**Design:**
- Gradient background
- Glassmorphism effects
- Responsive layout
- Animated elements
- Fast loading

#### Stage 5: Deployment

**Job:** `deploy-pages`

Final stage that makes everything live:

1. Takes Pages artifact from Stage 4
2. Deploys to GitHub Pages
3. Updates site URL
4. Announces completion

**Result:**
Your repository now has a live URL serving:
- ✅ Publication-quality whitepaper (PDF)
- ✅ Interactive documentation (HTML)
- ✅ Diagram gallery (PNG/SVG/PDF)
- ✅ Beautiful landing page

## Workflow Triggers

### Automatic Triggers

The pipeline runs automatically on:

```yaml
push:
  branches: [main, master]
  paths:
    - 'whitepaper/**'
    - 'latex/**'
    - 'diagrams/**'
    - 'tools/**'
    - 'src/**'
    - 'docs/**'
```

**Smart Path Filtering:** Only rebuilds when relevant files change.

### Manual Triggers

Use GitHub's "Run workflow" button with options:

- **Build MINIX:** Enable time-intensive QEMU build
- **Deploy Pages:** Control whether to deploy

## Configuration

### Environment Variables

```yaml
LATEX_OUTPUT_DIR: build/latex
DIAGRAMS_OUTPUT_DIR: build/diagrams
PAGES_OUTPUT_DIR: build/pages
MINIX_BUILD_DIR: build/minix
PYTHON_VERSION: '3.9'
```

### Required Secrets

None! The pipeline uses:
- GitHub's built-in `GITHUB_TOKEN`
- No external API keys needed
- All tools are open source

### Repository Settings

Enable GitHub Pages in your repo:

1. Go to **Settings** → **Pages**
2. Source: **GitHub Actions**
3. Save

That's it!

## The TeXplosion Moment

When the pipeline completes, you get:

### Before
```
repository/
├── whitepaper/
│   └── *.tex        # LaTeX source
├── diagrams/
│   └── *.py         # Analysis tools
└── docs/
    └── *.md         # Documentation
```

### After
```
https://yourname.github.io/minix-analysis/

📄 Live PDF whitepaper
📊 Interactive diagram gallery  
📖 Searchable documentation
✨ Beautiful landing page
```

### The Transformation

> **"The scientific equivalent of a chrysalis opening mid-build."**

Your repository has *metamorphosed*:

- **Code** → **Publication**
- **Data** → **Diagrams**
- **Markdown** → **Website**
- **LaTeX** → **Math Art**

## Advanced Features

### Modular Compilation

The pipeline supports selective LaTeX compilation:

```latex
% In your .tex file:
\includeonly{ch01-introduction,ch02-fundamentals}
```

Only the specified chapters will be compiled, speeding up iteration.

### Multi-Format Output

Every diagram is available in three formats:

- **PDF:** Print quality, vector graphics
- **PNG:** Web viewing, fast loading
- **SVG:** Scalable, accessible

### Caching and Efficiency

The pipeline uses GitHub Actions caching:

- Python dependencies cached by `pip`
- Docker layers cached by buildx
- Incremental builds when possible

### Error Handling

All stages use `continue-on-error` strategically:

- Diagram generation failures don't block compilation
- LaTeX warnings don't fail the build
- Logs are always uploaded for debugging

## Use Cases

### Research Publication

Every commit updates your live paper:

1. Add new data to analysis tools
2. Push to `main`
3. Pipeline regenerates diagrams
4. PDF recompiles automatically
5. Updated whitepaper goes live

**Perfect for:** Iterative research, collaborative writing, arxiv.org preparation

### Course Materials

Maintain a living textbook:

1. Update lecture notes in `docs/`
2. Add new diagrams for concepts
3. Push changes
4. Students see updates immediately

**Perfect for:** OS courses, kernel development workshops

### Technical Documentation

Keep docs synced with code:

1. Code changes update analysis
2. Diagrams reflect new architecture
3. Documentation stays current
4. Everything deploys together

**Perfect for:** Open source projects, internal documentation

## Customization

### Adding New Diagrams

1. Create data generation script in `tools/`
2. Add TikZ template to `diagrams/tikz/`
3. Update `tikz_generator.py` to use new data
4. Push → automatic compilation

### Adding LaTeX Chapters

1. Create new `chXX-name.tex` in `whitepaper/`
2. Add `\include{chXX-name}` to main document
3. Push → automatic compilation

### Customizing the Landing Page

Edit the `index.html` generation in the workflow:

```yaml
- name: Generate index page
  run: |
    cat > ${{ env.PAGES_OUTPUT_DIR }}/index.html << 'EOF'
    # Your custom HTML here
    EOF
```

## Performance

### Build Times

| Stage | Duration | Can Skip |
|-------|----------|----------|
| Diagrams | 3-5 min | No |
| MINIX Build | 60-90 min | Yes (optional) |
| LaTeX | 5-10 min | No |
| Pages Build | 2-3 min | No |
| Deployment | 1-2 min | No |

**Total (without MINIX):** ~15 minutes
**Total (with MINIX):** ~90 minutes

### Optimization Tips

1. **Skip MINIX builds** unless you need fresh metrics
2. **Use `\includeonly`** for faster LaTeX iteration
3. **Cache Docker layers** for consistent builds
4. **Parallel jobs** where possible (already configured)

## Troubleshooting

### LaTeX Compilation Fails

Check the uploaded `latex-pdfs` artifact for logs:
- `*.log` files show LaTeX errors
- `compilation-report.md` summarizes output

Common issues:
- Missing packages: Update TexLive installation
- Undefined references: Need multiple passes
- Image not found: Check diagram paths

### Diagrams Not Generated

Check `generated-diagrams` artifact:
- `analysis.log`: Data generation output
- `tikz-gen.log`: TikZ generation output

Common issues:
- Python tool errors: Check dependencies
- Missing data: Analysis tools may need updates
- TikZ compilation: Syntax errors in templates

### Pages Not Deploying

Verify GitHub Pages settings:
- Source must be "GitHub Actions"
- Branch protection rules may block deployment
- Check workflow permissions

## The Philosophy

### Why "TeXplosion"?

Traditional publishing workflow:
```
Write → Edit → Format → Submit → Review → Publish
(Weeks to months)
```

TeXplosion workflow:
```
Commit → Push → ✨ LIVE ✨
(15 minutes)
```

### The Continuous Publication Mindset

1. **Version control is publication control**
   - Every commit is a potential release
   - History preserves all versions
   - Rollback is one click

2. **Automation ensures consistency**
   - No manual compilation steps
   - Reproducible builds
   - Same output every time

3. **Integration prevents drift**
   - Code and docs stay synced
   - Diagrams reflect current data
   - No stale documentation

### The Science Art

This isn't just automation — it's transformation:

- **Data** becomes **visualization**
- **Analysis** becomes **narrative**
- **Code** becomes **publication**

The pipeline doesn't just build a document; it *creates* research outputs from your work.

## Future Enhancements

### Planned Features

- [ ] Automatic version tagging from PDF
- [ ] arxiv.org submission integration
- [ ] PDF → HTML conversion for inline viewing
- [ ] Interactive diagrams with D3.js
- [ ] Jupyter notebook integration
- [ ] Automated performance trending
- [ ] Multi-language documentation
- [ ] LaTeX diff viewing for changes

### Community Contributions

Want to improve the TeXplosion?

1. Fork the repository
2. Enhance the workflow
3. Test thoroughly
4. Submit PR with examples

We especially welcome:
- New diagram templates
- LaTeX package integrations
- Performance optimizations
- Documentation improvements

## Related Workflows

### Similar Pipelines

- **GitHub Actions Continuous Publication:** Generic term
- **LaTeX-to-Pages:** Simpler, PDF-only approach
- **Tectonic-Pages:** Using Tectonic instead of TexLive
- **Pandoc-Pages:** Markdown → HTML conversion
- **MkDocs Material:** Pure documentation site

### Our Unique Approach

TeXplosion combines:
- Data-driven visualization (TikZ/PGFPlots)
- Publication-quality typesetting (LaTeX)
- Interactive documentation (MkDocs)
- Live system metrics (MINIX in QEMU)
- Beautiful presentation (custom landing page)

No other workflow integrates all these elements.

## Credits

### Technologies Used

- **GitHub Actions:** CI/CD platform
- **TexLive:** LaTeX distribution
- **TikZ/PGFPlots:** Diagram creation
- **MkDocs Material:** Documentation theme
- **QEMU:** Virtual machine for MINIX
- **Docker:** Containerization
- **ImageMagick:** Image conversion
- **Python:** Analysis tools

### Inspiration

The TeXplosion concept draws from:

- Donald Knuth's literate programming
- Reproducible research movement
- DevOps continuous delivery
- Open science practices
- JAMstack architecture

### The Name

> **"TeXplosion"** — when your CI suddenly materializes a fully rendered publication site.

Variations seen in the wild:
- "BLAMTeX" — informal, dramatic
- "PDFOps" — mocking DevOps terminology
- "CI TeXForge" — emphasizing automation
- "Continuous Publication" — formal term

We chose **TeXplosion** because it captures both:
- The **transformation** (explosion)
- The **technology** (TeX)
- The **moment** of realization

## Conclusion

The TeXplosion pipeline represents a new paradigm:

**Your repository is not just code — it's a publishing platform.**

Every push can:
- Update live documentation
- Regenerate diagrams
- Recompile papers
- Deploy instantly

This is the future of academic and technical publishing:
- Version controlled
- Continuously integrated
- Automatically deployed
- Always accessible

Welcome to the TeXplosion. 🎉

---

**Next Steps:**

1. Enable GitHub Pages in repository settings
2. Push a change to trigger the pipeline
3. Watch the Actions tab for progress
4. Visit your new documentation site
5. Share your TeXplosion moment!

**Questions?** Check the [FAQ](./FAQ.md) or open an issue.

**Improvements?** Submit a PR — we'd love to see your enhancements!
