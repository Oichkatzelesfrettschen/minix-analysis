# TeXplosion FAQ - Frequently Asked Questions

## General Questions

### What is TeXplosion?

**TeXplosion** is a GitHub Actions CI/CD pipeline that automatically transforms your repository into a live publication platform. Every push can update:
- Publication-quality PDF whitepaper
- Interactive documentation website
- Diagram galleries
- Analysis reports

Think of it as "Continuous Publication" - your research becomes publicly accessible the moment you commit.

### Where did the name come from?

The term "TeXplosion" captures the moment when your CI **explodes** your **TeX** (LaTeX) sources into a fully rendered publication site. It's colloquially known as:

- **TeXplosion** - Our preferred name
- **BLAMTeX** - Informal, dramatic
- **PDFOps** - Tongue-in-cheek DevOps reference
- **CI TeXForge** - Emphasizing automation
- **Continuous Publication** - Formal academic term

The concept: *"When your repository stops being just code and turns itself into math art on the web."*

### Is this really free?

**Yes!** For public repositories:
- GitHub Actions: Unlimited minutes
- GitHub Pages: Free hosting
- All tools: Open source (TexLive, MkDocs, etc.)

For private repositories:
- GitHub Actions: Generous free tier (2,000 minutes/month)
- GitHub Pages: Free but site will be public
- No additional costs

### How long does it take?

**Without MINIX build:** ~15 minutes total
- Diagram generation: 3-5 minutes
- LaTeX compilation: 5-10 minutes
- Pages build: 2-3 minutes
- Deployment: 1-2 minutes

**With MINIX build:** ~90 minutes total
- MINIX build in QEMU: 60-90 minutes
- Everything else: ~15 minutes

**Recommendation:** Only run MINIX builds when you need fresh system metrics, not on every commit.

## Setup Questions

### How do I enable GitHub Pages?

1. Go to your repository on GitHub
2. Click **Settings** (top menu)
3. Click **Pages** (left sidebar)
4. Under "Source", select **GitHub Actions**
5. Click **Save**

That's it! No branches, no directories to configure.

### Do I need any secrets or tokens?

**No!** The pipeline uses GitHub's built-in `GITHUB_TOKEN` which is automatically available. You don't need to configure:
- API keys
- Personal access tokens
- Deploy keys
- Secrets

Everything "just works" with default permissions.

### What if I have a private repository?

The pipeline works fine with private repos, but note:
- The GitHub Pages site will still be **public**
- Anyone with the URL can access your documentation
- If you need private docs, consider:
  - Using a different hosting platform
  - Restricting access with authentication
  - Serving PDFs from a password-protected server

### Can I use a custom domain?

**Yes!** To use a custom domain like `docs.yourproject.com`:

1. Add a `CNAME` file to your repository root:
   ```
   docs.yourproject.com
   ```

2. Configure DNS at your domain registrar:
   ```
   CNAME docs.yourproject.com username.github.io
   ```

3. In GitHub Settings → Pages, enter your custom domain

4. Enable HTTPS (recommended)

GitHub handles SSL certificates automatically via Let's Encrypt.

## Usage Questions

### How do I trigger the pipeline?

**Automatically:**
Just push to `main` or `master`:
```bash
git push origin main
```

The pipeline only runs if you change files in:
- `whitepaper/`
- `latex/`
- `diagrams/`
- `tools/`
- `src/`
- `docs/`

**Manually:**
1. Go to **Actions** tab
2. Click **TeXplosion - LaTeX Continuous Publication**
3. Click **Run workflow**
4. Choose options (Build MINIX: yes/no)
5. Click **Run workflow**

### Can I test locally before pushing?

**Yes!** Test each component:

**LaTeX compilation:**
```bash
cd whitepaper
pdflatex MINIX-3.4-Comprehensive-Technical-Analysis.tex
```

**Python tools:**
```bash
python tools/minix_source_analyzer.py
python tools/tikz_generator.py
```

**MkDocs site:**
```bash
mkdocs serve
# Visit http://localhost:8000
```

**Workflow syntax:**
```bash
# Requires yamllint
yamllint .github/workflows/texplosion-pages.yml
```

### How do I add a new chapter to the whitepaper?

1. Create new chapter file:
   ```bash
   vim whitepaper/ch12-new-topic.tex
   ```

2. Add to main document:
   ```latex
   % In MINIX-3.4-Comprehensive-Technical-Analysis.tex
   \include{ch12-new-topic}
   ```

3. Commit and push:
   ```bash
   git add whitepaper/ch12-new-topic.tex whitepaper/MINIX-3.4-Comprehensive-Technical-Analysis.tex
   git commit -m "Add chapter 12: New Topic"
   git push
   ```

Pipeline automatically recompiles the PDF!

### How do I add new diagrams?

**Option 1: Manual TikZ diagram**

1. Create TikZ file:
   ```bash
   vim diagrams/tikz/my-diagram.tex
   ```

2. Reference in LaTeX:
   ```latex
   \begin{figure}
   \input{diagrams/tikz/my-diagram.tex}
   \caption{My new diagram}
   \end{figure}
   ```

**Option 2: Generated from data**

1. Update analysis tool:
   ```python
   # In tools/minix_source_analyzer.py
   # Add code to export new data
   ```

2. Update diagram generator:
   ```python
   # In tools/tikz_generator.py
   # Add code to create TikZ from data
   ```

3. Push changes - pipeline generates diagram automatically

### Can I skip the MINIX build?

**Yes!** The MINIX build is optional and off by default.

It only runs when:
- You manually trigger the workflow with "Build MINIX" = true
- Or you set `build_minix: 'true'` in the workflow dispatch

For normal documentation updates, the MINIX build is skipped to save time.

## Troubleshooting

### My LaTeX won't compile

**Check the logs:**
1. Go to failed workflow run
2. Click "Compile LaTeX Whitepaper" job
3. Expand "Compile main whitepaper" step
4. Look for error messages

**Download full logs:**
1. Scroll to "Artifacts" section
2. Download "latex-pdfs" artifact
3. Check `.log` files for details

**Common issues:**

**Missing package:**
```
! LaTeX Error: File `somepackage.sty' not found
```
Add to workflow's LaTeX installation:
```yaml
sudo apt-get install -y texlive-<package-collection>
```

**Undefined reference:**
```
LaTeX Warning: Reference `fig:example' undefined
```
Need multiple compilation passes - workflow already does this, but complex documents may need adjustments.

**Image not found:**
```
! Package pdftex.def Error: File `diagram.pdf' not found
```
Verify diagram was generated in previous stage. Check diagram paths are correct.

### Diagrams aren't generating

**Check analysis logs:**
Download "generated-diagrams" artifact and check:
- `analysis.log` - Data generation output
- `tikz-gen.log` - TikZ compilation output

**Common issues:**

**Python errors:**
Check tool output for syntax errors or missing dependencies.

**Missing data:**
Analysis tools may need source files that aren't available. Check paths.

**TikZ syntax errors:**
Check diagram `.tex` files for LaTeX syntax issues.

### Pages aren't deploying

**Verify Pages is enabled:**
Settings → Pages → Source should be "GitHub Actions"

**Check workflow permissions:**
The workflow needs `pages: write` permission, which is set in the workflow file.

**Branch protection:**
If you have branch protection on `main`, verify the workflow can run.

**Wait a bit:**
Deployment can take 2-5 minutes. Check again after a few minutes.

**Force redeploy:**
Re-run the workflow from the Actions tab.

### The site shows a 404

**First deployment:**
First time Pages deployment can take up to 10 minutes to propagate.

**Wrong URL:**
Verify you're using the correct URL format:
```
https://USERNAME.github.io/REPOSITORY-NAME/
```

**Custom domain:**
If using a custom domain, verify:
- CNAME file is in place
- DNS is configured correctly
- SSL certificate has been issued (can take an hour)

### Artifacts aren't uploading

**Check storage limits:**
Free tier: 500 MB artifact storage. Check your usage:
Settings → Billing → Storage and bandwidth

**Large files:**
Consider compressing artifacts or reducing retention days.

**Upload failures:**
Temporary GitHub infrastructure issues. Re-run the workflow.

## Customization Questions

### Can I change the landing page design?

**Yes!** Edit the workflow file's "Generate index page" step:

```yaml
- name: Generate index page
  run: |
    cat > ${{ env.PAGES_OUTPUT_DIR }}/index.html << 'EOF'
    <!DOCTYPE html>
    <html>
    <!-- Your custom HTML here -->
    </html>
    EOF
```

You can:
- Change colors and styles
- Add your own branding
- Modify layout and content
- Add analytics or tracking

### Can I add more output formats?

**Yes!** Add conversion steps to the workflow:

**EPUB from LaTeX:**
```yaml
- name: Generate EPUB
  run: |
    pandoc -f latex -t epub3 \
      -o whitepaper.epub \
      MINIX-3.4-Comprehensive-Technical-Analysis.tex
```

**HTML from LaTeX:**
```yaml
- name: Generate HTML
  run: |
    pandoc -f latex -t html5 --mathjax \
      -o whitepaper.html \
      MINIX-3.4-Comprehensive-Technical-Analysis.tex
```

**Markdown from LaTeX:**
```yaml
- name: Generate Markdown
  run: |
    pandoc -f latex -t markdown \
      -o whitepaper.md \
      MINIX-3.4-Comprehensive-Technical-Analysis.tex
```

### Can I use a different LaTeX compiler?

**Yes!** The workflow currently uses `pdflatex` via `latexmk`, but you can switch to:

**XeLaTeX** (better font support):
```yaml
latexmk -xelatex main.tex
```

**LuaLaTeX** (modern, fast):
```yaml
latexmk -lualatex main.tex
```

**Tectonic** (self-contained, fast):
```yaml
tectonic main.tex
```

Just modify the compilation step in the workflow.

### Can I deploy to somewhere other than GitHub Pages?

**Yes!** Replace the `deploy-pages` job with your preferred deployment:

**AWS S3:**
```yaml
- name: Deploy to S3
  run: |
    aws s3 sync build/pages/ s3://my-bucket/ --delete
```

**Netlify:**
```yaml
- name: Deploy to Netlify
  uses: nwtgck/actions-netlify@v2
  with:
    publish-dir: './build/pages'
```

**Your server:**
```yaml
- name: Deploy via SCP
  run: |
    scp -r build/pages/* user@server:/var/www/html/
```

### Can I add automated tests?

**Yes!** Add a testing job before deployment:

```yaml
test-pdf:
  name: Test PDF Quality
  runs-on: ubuntu-latest
  needs: compile-latex
  
  steps:
    - name: Download PDF
      uses: actions/download-artifact@v4
      with:
        name: latex-pdfs
    
    - name: Check PDF integrity
      run: |
        pdfinfo MINIX-Analysis-Whitepaper.pdf
        
    - name: Count pages
      run: |
        PAGES=$(pdfinfo MINIX-Analysis-Whitepaper.pdf | grep Pages | awk '{print $2}')
        if [ $PAGES -lt 100 ]; then
          echo "Error: PDF only has $PAGES pages"
          exit 1
        fi
```

## Performance Questions

### How can I speed up the pipeline?

**1. Skip MINIX builds** (saves 75 minutes)
- Only run when you need fresh metrics
- Default behavior already skips them

**2. Use selective LaTeX compilation:**
```latex
\includeonly{ch03-methodology}  % Only compile one chapter
```

**3. Cache dependencies:**
The workflow already caches pip packages. You can add:
```yaml
- name: Cache LaTeX packages
  uses: actions/cache@v3
  with:
    path: ~/.texlive
    key: texlive-${{ hashFiles('whitepaper/*.tex') }}
```

**4. Reduce diagram generation:**
Comment out diagrams you're not actively working on in `tikz_generator.py`.

**5. Use draft mode:**
```latex
\documentclass[draft]{book}  % Faster compilation, no images
```

### Why does LaTeX compilation take so long?

Multiple passes are needed to resolve:
- Cross-references (`\ref`)
- Citations (`\cite`)
- Table of contents
- Index generation

The workflow runs `latexmk` which automatically determines the minimum number of passes needed.

For a 300+ page document with hundreds of references, this typically requires:
- 2-3 LaTeX passes
- 1 BibTeX/Biber pass
- 1-2 final LaTeX passes

Total: 5-7 minutes for a large document.

### Can I run jobs in parallel?

**Partially.** The workflow already parallelizes:
- Stage 2 (MINIX) and Stage 3 (LaTeX) run simultaneously
- Both feed into Stage 4 (Pages)

You can't parallelize:
- Stages that depend on previous outputs
- LaTeX compilation itself (sequential by nature)

### How much does this cost in Actions minutes?

**Public repos:** Free (unlimited)

**Private repos:** Approximately 15-90 minutes per run, charged at:
- Linux: 1x multiplier (15-90 minutes counted)
- Windows: 2x multiplier (if you switch to Windows runners)
- macOS: 10x multiplier (if you switch to macOS runners)

Free tier: 2,000 minutes/month
- ~130 runs without MINIX build
- ~22 runs with MINIX build

## Advanced Questions

### Can I integrate this with Overleaf?

**Not directly**, but you can:

1. **Overleaf → GitHub → TeXplosion:**
   - Write in Overleaf
   - Use Overleaf's Git integration to push to GitHub
   - TeXplosion publishes automatically

2. **GitHub → Overleaf (reverse):**
   - Write in GitHub (or local editor)
   - Pull into Overleaf for collaborative editing
   - Push back to GitHub for publication

3. **Hybrid approach:**
   - Use Overleaf for drafting
   - Export final version to GitHub
   - Let TeXplosion handle publication

### How do I version my publications?

**Git tags** create permanent snapshots:

```bash
git tag -a v1.0 -m "Publication version 1.0"
git push origin v1.0
```

**GitHub Releases** for distribution:
```bash
gh release create v1.0 \
  build/latex/MINIX-Analysis-Whitepaper.pdf \
  --title "MINIX Analysis v1.0" \
  --notes "First public release"
```

**Zenodo integration** for DOIs:
1. Link repository to Zenodo
2. Create GitHub release
3. Zenodo automatically archives and assigns DOI

### Can I submit to arXiv automatically?

**Partially automated:**

1. Pipeline creates submission package:
```yaml
- name: Create arXiv package
  run: |
    mkdir arxiv-submission
    cp whitepaper/*.tex arxiv-submission/
    cp whitepaper/*.bbl arxiv-submission/
    cp diagrams/tikz-generated/*.pdf arxiv-submission/figures/
    tar czf arxiv-submission.tar.gz arxiv-submission/
```

2. Download and submit manually:
   - Download `arxiv-submission.tar.gz` artifact
   - Upload to arXiv.org
   - arXiv doesn't allow fully automated submissions

3. For updates, repeat the process

### How do I integrate with Jupyter notebooks?

**Convert notebooks to LaTeX:**

```yaml
- name: Convert Jupyter to LaTeX
  run: |
    jupyter nbconvert --to latex analysis.ipynb
    cp analysis.tex whitepaper/
```

**Include in documentation:**

```yaml
- name: Execute and render notebooks
  run: |
    jupyter nbconvert --execute --to html *.ipynb
    cp *.html ${{ env.PAGES_OUTPUT_DIR }}/notebooks/
```

**Both approaches:**
Analysis in Jupyter → Export to LaTeX → Include in whitepaper → Publish!

### Can I add interactive diagrams?

**Yes!** Several approaches:

**1. D3.js visualizations:**
```yaml
- name: Generate D3 diagrams
  run: |
    python scripts/generate_d3_viz.py
    cp viz/*.html ${{ env.PAGES_OUTPUT_DIR }}/interactive/
```

**2. Plotly interactive plots:**
```python
import plotly.graph_objects as go
fig = go.Figure(data=go.Scatter(x=[1,2,3], y=[4,5,6]))
fig.write_html("interactive-plot.html")
```

**3. Embed in documentation:**
Link from your docs to interactive visualizations hosted alongside the PDF.

## Best Practices

### What should I commit to Git?

**DO commit:**
- ✅ LaTeX source files (`.tex`)
- ✅ Bibliography files (`.bib`)
- ✅ TikZ diagram sources
- ✅ Python analysis tools
- ✅ Documentation (`.md`)
- ✅ Configuration files

**DON'T commit:**
- ❌ Generated PDFs (artifacts from CI)
- ❌ LaTeX auxiliary files (`.aux`, `.log`)
- ❌ Generated diagrams (recreated by CI)
- ❌ Build directories
- ❌ Temporary files

The `.gitignore` file handles this automatically.

### How often should I push?

**For development:**
- Commit locally often (after each logical change)
- Push when you want to see results online
- Remember: each push triggers ~15 min of CI time

**For production:**
- Create feature branches for major changes
- Use PRs to review before merging to main
- Only `main` branch deploys to Pages

**Recommendation:**
```bash
# Work locally
git commit -m "Work in progress"  # Many times
git commit -m "Work in progress"
git commit -m "Chapter complete"

# When ready to see it online
git push origin main  # Triggers TeXplosion
```

### Should I review before deploying?

**Yes!** Use Pull Requests:

1. Create branch:
   ```bash
   git checkout -b feature/new-content
   ```

2. Make changes, commit, push:
   ```bash
   git push origin feature/new-content
   ```

3. Open PR on GitHub

4. Pipeline runs but **doesn't deploy**

5. Review artifacts in PR

6. Merge to `main` when ready

7. Automatic deployment happens

This prevents publishing incomplete work.

## Getting Help

### Where can I get support?

**Documentation:**
1. [Quick Start Guide](./TEXPLOSION-QUICKSTART.md)
2. [Full Pipeline Documentation](./TEXPLOSION-PIPELINE.md)
3. This FAQ

**GitHub:**
1. Check existing [Issues](https://github.com/Oichkatzelesfrettschen/minix-analysis/issues)
2. Open new issue with:
   - Workflow run URL
   - Error messages
   - What you were trying to do
   - What you expected vs. what happened

**Community:**
1. GitHub Discussions (if enabled)
2. Stack Overflow (tag: `github-actions`, `latex`)

### How do I contribute improvements?

**We welcome contributions!**

1. Fork the repository
2. Create feature branch
3. Make improvements
4. Test thoroughly
5. Submit Pull Request with:
   - Clear description
   - Before/after examples
   - Test results

**Areas especially welcome:**
- New diagram templates
- Performance optimizations
- Better error handling
- Documentation improvements
- Example use cases

### Can I use this for my own project?

**Absolutely!** This is open source.

**To adapt for your project:**

1. Fork or copy the workflow file
2. Adjust paths to match your structure:
   - LaTeX sources location
   - Diagram directories
   - Tool locations
3. Customize the landing page
4. Update documentation references
5. Enable Pages in your repo
6. Push and watch the magic!

**License:** Check repository LICENSE file for terms.

---

## Still have questions?

**Open an issue:** [Create New Issue](https://github.com/Oichkatzelesfrettschen/minix-analysis/issues/new)

**Check workflow runs:** See examples in the [Actions tab](https://github.com/Oichkatzelesfrettschen/minix-analysis/actions)

**Read the source:** The workflow is extensively commented - `texplosion-pages.yml`

---

*Last updated: 2025-11-04*
