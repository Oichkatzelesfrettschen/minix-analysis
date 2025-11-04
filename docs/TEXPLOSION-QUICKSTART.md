# 🚀 TeXplosion Quick Start Guide

## What is This?

A GitHub Actions workflow that automatically:
1. Generates diagrams from MINIX analysis
2. Compiles a LaTeX whitepaper
3. Publishes everything to GitHub Pages

## One-Time Setup

### 1. Enable GitHub Pages

1. Go to your repo's **Settings**
2. Click **Pages** (left sidebar)
3. Under "Source", select **GitHub Actions**
4. Click **Save**

That's it! No other configuration needed.

### 2. Verify Repository Structure

Your repo should have:

```
minix-analysis/
├── .github/workflows/
│   └── texplosion-pages.yml    # The workflow
├── whitepaper/
│   ├── *.tex                   # LaTeX sources
│   └── *.bib                   # Bibliography
├── latex/                       # Alternative LaTeX location
├── diagrams/
│   ├── tikz/                   # TikZ templates
│   └── tikz-generated/         # Output (created by pipeline)
├── tools/
│   ├── minix_source_analyzer.py
│   └── tikz_generator.py
└── docs/
    └── *.md                     # Documentation
```

## Triggering the Pipeline

### Automatic (Recommended)

Just push to `main`:

```bash
git add .
git commit -m "Update whitepaper chapter 3"
git push origin main
```

The pipeline runs automatically!

### Manual

1. Go to **Actions** tab
2. Click **TeXplosion - LaTeX Continuous Publication**
3. Click **Run workflow**
4. Choose options:
   - **Build MINIX:** Only if you need fresh metrics (takes 90 min)
   - **Deploy Pages:** Usually "yes"
5. Click **Run workflow**

## Watching Progress

### Actions Tab

1. Go to **Actions** tab
2. Click on the running workflow
3. Watch each stage complete:
   - ✅ Generate Diagrams (~5 min)
   - ✅ Compile LaTeX (~10 min)
   - ✅ Build Pages (~3 min)
   - ✅ Deploy (~2 min)

### Notifications

Enable notifications:
1. Click **Watch** → **Custom**
2. Check **Actions**
3. Get alerts when builds complete

## Viewing Results

### Your Documentation Site

Once deployed, visit:

```
https://YOUR-USERNAME.github.io/minix-analysis/
```

Replace `YOUR-USERNAME` with your GitHub username.

### Site Contents

- **Landing Page:** Beautiful animated homepage
- **PDFs:** `/pdfs/MINIX-Analysis-Whitepaper.pdf`
- **Diagrams:** `/diagrams/` (gallery view)
- **Docs:** `/docs/` (searchable documentation)

### Artifacts

Even if deployment is disabled, you can download:

1. Go to completed workflow run
2. Scroll to **Artifacts** section
3. Download:
   - `latex-pdfs` - Compiled documents
   - `generated-diagrams` - All diagrams
   - `minix-build-artifacts` - MINIX build output (if run)

## Common Workflows

### 1. Update Whitepaper Text

```bash
# Edit LaTeX source
vim whitepaper/ch01-introduction.tex

# Commit and push
git add whitepaper/ch01-introduction.tex
git commit -m "Add section on memory management"
git push
```

Pipeline automatically:
- Recompiles PDF
- Updates website
- Done in ~15 minutes

### 2. Add New Diagram

```bash
# Create TikZ template
vim diagrams/tikz/new-diagram.tex

# Update generator
vim tools/tikz_generator.py  # Add new diagram logic

# Push
git add diagrams/tikz/new-diagram.tex tools/tikz_generator.py
git commit -m "Add syscall flow diagram"
git push
```

Pipeline automatically:
- Generates diagram
- Includes in PDF
- Adds to gallery
- Updates website

### 3. Quick Documentation Update

```bash
# Edit markdown
vim docs/architecture/memory.md

# Push
git add docs/architecture/memory.md
git commit -m "Document page table structure"
git push
```

Pipeline automatically:
- Rebuilds MkDocs site
- Updates documentation
- No LaTeX recompilation needed (fast!)

### 4. Full System Analysis

```bash
# Update analysis tools
vim tools/minix_source_analyzer.py

# Push and trigger MINIX build
git add tools/minix_source_analyzer.py
git commit -m "Enhanced boot sequence analysis"
git push

# Then manually run workflow with "Build MINIX" enabled
```

This does everything:
- Runs MINIX in QEMU
- Collects fresh metrics
- Regenerates all diagrams
- Recompiles whitepaper
- Updates website

Time: ~90 minutes (mostly MINIX build)

## Customization

### Change LaTeX Document

Edit `texplosion-pages.yml`:

```yaml
# Line ~286
MAIN_TEX="your-document.tex"
```

### Change Diagram Location

Edit `texplosion-pages.yml`:

```yaml
# Line ~32
DIAGRAMS_OUTPUT_DIR: your/diagrams/path
```

### Customize Landing Page

Edit the `Generate index page` step in the workflow to create your own HTML.

### Add More Formats

Want EPUB or HTML from LaTeX?

Add to the `compile-latex` job:

```yaml
- name: Generate EPUB
  run: |
    pandoc -f latex -t epub3 \
      -o output.epub \
      your-main.tex
```

## Troubleshooting

### Build Fails

1. Check **Actions** tab for the failed run
2. Click on the failed job
3. Expand failed step to see error
4. Download artifacts for logs

### Common Issues

**"LaTeX compilation failed"**
- Check `.tex` syntax
- Verify all `\include` files exist
- Download `latex-pdfs` artifact for logs

**"Diagrams not generated"**
- Check Python tool syntax
- Verify data files exist
- Download `generated-diagrams` artifact

**"Pages not deploying"**
- Verify GitHub Pages is enabled
- Check Pages settings (must be "GitHub Actions")
- Wait a few minutes (deployment can be slow)

**"PDF not found in website"**
- Check LaTeX compilation succeeded
- Verify main PDF was created
- Check artifact uploads

### Getting Help

1. Check workflow logs in Actions tab
2. Review [Full Documentation](./TEXPLOSION-PIPELINE.md)
3. Open an issue with:
   - Workflow run URL
   - Error message
   - What you were trying to do

## Performance Tips

### Speed Up Development

**Skip MINIX build** (default):
- Use manual trigger with "Build MINIX" = false
- Or push without special trigger (automatic runs skip it)

**Use selective compilation:**
```latex
% In your main .tex file
\includeonly{ch03-methodology}  % Only compile this chapter
```

**Cache diagrams:**
- Don't regenerate all diagrams every time
- Only update what changed
- Commit generated diagrams if they're stable

### Monitor Build Times

Check the workflow summary:
- Each job shows duration
- Optimize slowest stages first
- Consider caching strategies

## Best Practices

### 1. Meaningful Commit Messages

```bash
# Good
git commit -m "Add TLB architecture diagram to chapter 4"

# Better
git commit -m "chap4: Add TLB architecture diagram

- Created new TikZ template for TLB structure
- Updated chapter 4 to reference diagram
- Includes 4 cache levels with latencies"
```

Clear messages help track what triggered each build.

### 2. Incremental Changes

Commit often, push frequently:
- Easier to identify what broke
- Faster iteration cycles
- Better version history

### 3. Test Locally First

Before pushing:

```bash
# Test LaTeX compilation
cd whitepaper
pdflatex main.tex

# Test Python tools
python tools/minix_source_analyzer.py

# Test MkDocs
mkdocs serve
```

Catch errors before CI runs.

### 4. Use Branches for Big Changes

```bash
git checkout -b feature/new-chapter
# Make changes
git commit -am "Draft new chapter on IPC"
git push origin feature/new-chapter
# Open PR to review before merging to main
```

PRs trigger the pipeline but don't deploy.

## Advanced Usage

### Manual Artifact Downloads

Useful for local testing or offline work:

```bash
# Use GitHub CLI
gh run download RUN_ID --name latex-pdfs

# Or download from Actions tab UI
```

### Selective Diagram Generation

Edit `tools/tikz_generator.py`:

```python
# Only generate specific diagrams
if diagram_name in ['syscall-flow', 'memory-layout']:
    generate_diagram(diagram_name)
```

### Multiple LaTeX Documents

The pipeline compiles all `.tex` files in `LATEX_OUTPUT_DIR`:

```
whitepaper/
├── main-whitepaper.tex
├── appendix-only.tex
└── slides.tex
```

All three become PDFs!

### Custom MkDocs Theme

Edit `mkdocs.yml`:

```yaml
theme:
  name: material
  custom_dir: overrides/  # Your customizations
```

Pipeline uses your theme automatically.

## FAQ

**Q: How much does this cost?**
A: $0. GitHub Actions is free for public repos, and includes generous minutes for private repos.

**Q: Can I use this for private repos?**
A: Yes! Private repos can deploy to Pages. The site will be public though.

**Q: How do I password-protect the site?**
A: GitHub Pages doesn't support authentication. Consider:
- Using GitHub's private repos (restricts access to collaborators)
- Using a different hosting platform
- Serving PDFs from a password-protected server

**Q: Can I customize the URL?**
A: Yes! Set up a custom domain in Pages settings.

**Q: What if LaTeX takes too long?**
A: Use `\includeonly` to compile only changed chapters during development.

**Q: Can I deploy to somewhere other than Pages?**
A: Yes! Modify the `deploy-pages` job to use:
- AWS S3
- Netlify
- Your own server
- Any static site host

**Q: How do I add a DOI or citation?**
A: Add to your LaTeX front matter:
```latex
\doi{10.xxxxx/xxxxx}
```

Or use Zenodo to archive releases and get DOIs automatically.

**Q: Can this work with Overleaf?**
A: Not directly, but you can:
1. Use Overleaf for editing
2. Export to GitHub
3. Let TeXplosion handle publication

## Next Steps

### For Researchers

- [ ] Add your paper to arxiv.org (export from TeXplosion builds)
- [ ] Get DOI via Zenodo
- [ ] Share GitHub Pages link in publications
- [ ] Use diagrams in presentations

### For Educators

- [ ] Create course website with TeXplosion
- [ ] Add lecture notes as chapters
- [ ] Generate assignment PDFs
- [ ] Share with students via Pages URL

### For Developers

- [ ] Document architecture with TikZ
- [ ] Auto-generate API diagrams
- [ ] Create technical whitepapers
- [ ] Maintain living documentation

## Resources

- **Full Documentation:** [TEXPLOSION-PIPELINE.md](./TEXPLOSION-PIPELINE.md)
- **Workflow File:** `.github/workflows/texplosion-pages.yml`
- **LaTeX Examples:** `whitepaper/`
- **Diagram Templates:** `diagrams/tikz/`
- **GitHub Actions Docs:** https://docs.github.com/actions

---

**Ready to explode your repo into math art?** 💥

```bash
git push origin main
```

Watch the magic happen in your Actions tab! ✨
