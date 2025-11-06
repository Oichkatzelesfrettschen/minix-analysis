# TeXplosion Complete Example

This document walks through a complete example of using the TeXplosion pipeline to add new content and publish it automatically.

## Scenario

You want to add a new chapter about MINIX memory management to the whitepaper, complete with diagrams showing page table structures.

## Step-by-Step Walkthrough

### Step 1: Create the New Chapter

Create a new LaTeX file for your chapter:

```bash
cd whitepaper
vim ch13-memory-management.tex
```

**File content:**

```latex
\chapter{Memory Management in MINIX}
\label{ch:memory}

\section{Introduction}

MINIX 3.4 on i386 uses a two-level paging hierarchy for virtual memory
management. This chapter explores the page table structure, TLB management,
and memory allocation strategies.

\section{Page Table Architecture}

The i386 architecture uses a two-level page table:

\begin{itemize}
    \item \textbf{Page Directory:} Top-level table with 1024 entries
    \item \textbf{Page Tables:} Second-level tables, each with 1024 entries
    \item \textbf{Page Size:} 4 KB (standard) or 4 MB (with PSE)
\end{itemize}

\subsection{Address Translation}

Figure~\ref{fig:page-translation} shows the virtual to physical address
translation process.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.8\textwidth]{figures/page-translation.pdf}
\caption{Virtual to physical address translation in i386}
\label{fig:page-translation}
\end{figure}

\section{TLB Management}

The Translation Lookaside Buffer (TLB) caches recent address translations
for performance. MINIX must explicitly flush the TLB when:

\begin{enumerate}
    \item Switching processes (CR3 reload)
    \item Modifying page table entries
    \item Changing CR3 or CR4 flags
\end{enumerate}

\subsection{Performance Impact}

TLB misses significantly impact system performance. Our measurements show:

\begin{itemize}
    \item TLB hit: 1-2 cycles
    \item TLB miss: 10-20 cycles (plus page table walk)
    \item Context switch TLB flush: 50-100 cycles overhead
\end{itemize}

\section{Conclusion}

Understanding MINIX's memory management is crucial for both performance
optimization and system security. The two-level paging hierarchy provides
a good balance between memory overhead and translation speed for 32-bit
systems.
```

### Step 2: Add Chapter to Main Document

Edit the main whitepaper file:

```bash
vim MINIX-3.4-Comprehensive-Technical-Analysis.tex
```

Add the new chapter to the document body:

```latex
% ... existing content ...

\include{ch12-implementation}
\include{ch13-memory-management}  % NEW CHAPTER
\include{ch14-appendices}

% ... rest of document ...
```

### Step 3: Create TikZ Diagram for Page Translation

Create a new TikZ diagram template:

```bash
cd ../diagrams/tikz
vim page-translation.tex
```

**File content:**

```latex
\documentclass[tikz,border=10pt]{standalone}
\usepackage{tikz}
\usetikzlibrary{arrows,positioning,shapes}

\begin{document}
\begin{tikzpicture}[
    box/.style={rectangle,draw,minimum width=2cm,minimum height=0.8cm},
    arrow/.style={->,thick,>=stealth}
]

% Virtual Address
\node[box] (va) {Virtual Address};
\node[below=0.2cm of va,font=\small] {32 bits};

% Address breakdown
\node[box,right=2cm of va] (dir) {Dir (10)};
\node[box,right=0.1cm of dir] (table) {Table (10)};
\node[box,right=0.1cm of table] (offset) {Offset (12)};

% Page Directory
\node[box,below=2cm of dir] (pd) {Page Directory};
\node[below=0.1cm of pd,font=\small] {1024 entries};

% Page Table
\node[box,below=2cm of table] (pt) {Page Table};
\node[below=0.1cm of pt,font=\small] {1024 entries};

% Physical Page
\node[box,below=2cm of offset] (pp) {Physical Page};
\node[below=0.1cm of pp,font=\small] {4 KB};

% Physical Address
\node[box,below=1cm of pp] (pa) {Physical Address};

% Arrows
\draw[arrow] (va) -- (dir);
\draw[arrow] (dir) -- (pd);
\draw[arrow] (table) -- (pt);
\draw[arrow] (pd) -- (pt);
\draw[arrow] (pt) -- (pp);
\draw[arrow] (offset) -- (pp);
\draw[arrow] (pp) -- (pa);

% Labels
\node[right=0.5cm of pd,text width=3cm,font=\small] {
    CR3 points to\\
    Page Directory
};

\end{tikzpicture}
\end{document}
```

### Step 4: Update Analysis Tools (Optional)

If you want data-driven diagrams, update the generator:

```bash
cd ../../tools
vim tikz_generator.py
```

Add a new diagram generation function:

```python
def generate_page_translation_diagram(output_dir):
    """Generate page translation diagram with real data"""
    
    # In a real scenario, you'd extract this from MINIX source
    data = {
        'page_size': 4096,
        'page_directory_entries': 1024,
        'page_table_entries': 1024,
        'address_bits': 32,
    }
    
    tikz_code = f"""
\\documentclass[tikz,border=10pt]{{standalone}}
% ... TikZ code using {data} ...
\\end{{document}}
"""
    
    output_path = os.path.join(output_dir, 'page-translation.tex')
    with open(output_path, 'w') as f:
        f.write(tikz_code)
    
    print(f"Generated {output_path}")

# In main():
if __name__ == '__main__':
    # ... existing code ...
    generate_page_translation_diagram(args.output)
```

### Step 5: Commit Your Changes

```bash
cd ../..
git add whitepaper/ch13-memory-management.tex
git add whitepaper/MINIX-3.4-Comprehensive-Technical-Analysis.tex
git add diagrams/tikz/page-translation.tex
git add tools/tikz_generator.py  # if you updated it

git commit -m "Add chapter 13: Memory Management

- Created new chapter on MINIX memory management
- Added page translation diagram
- Covered 2-level paging, TLB, and performance
- Updated main document to include new chapter"
```

### Step 6: Push to Trigger Pipeline

```bash
git push origin main
```

### Step 7: Monitor the Pipeline

1. Go to your repository on GitHub
2. Click the **Actions** tab
3. See your commit message in the workflow list
4. Click on it to watch progress

You'll see these stages execute:

```
⏳ Generate Diagrams (3-5 min)
   ├─ Install LaTeX
   ├─ Run analysis tools
   ├─ Generate TikZ diagrams
   ├─ Compile page-translation.tex → PDF
   └─ Convert to PNG and SVG

⏳ Compile LaTeX (5-10 min)
   ├─ Download diagrams
   ├─ Copy LaTeX sources
   ├─ Run latexmk on main document
   ├─ Include new chapter 13
   └─ Generate final PDF

⏳ Build Pages (2-3 min)
   ├─ Download compiled PDFs
   ├─ Build MkDocs site
   ├─ Create landing page
   └─ Assemble diagram gallery

⏳ Deploy (1-2 min)
   ├─ Upload to GitHub Pages
   └─ Update site

✅ TeXplosion Complete!
```

### Step 8: View Your Published Work

After ~15 minutes, visit your site:

```
https://YOUR-USERNAME.github.io/minix-analysis/
```

You'll see:

1. **Landing Page:**
   - Link to updated whitepaper
   - New chapter is included
   
2. **PDF Download:**
   - Click "Main Whitepaper"
   - Chapter 13 is in the table of contents
   - Navigate to new chapter
   - See your diagram (Figure XX)
   
3. **Diagram Gallery:**
   - Click "Diagrams & Visualizations"
   - Scroll to find `page-translation.png`
   - Click to view full resolution
   - SVG version available for scaling

### Step 9: Share Your Work

The whitepaper is now live! Share it:

```bash
# Get the direct PDF link
echo "https://YOUR-USERNAME.github.io/minix-analysis/pdfs/MINIX-Analysis-Whitepaper.pdf"

# Share on social media, in papers, etc.
```

## What Just Happened?

The TeXplosion pipeline automatically:

1. ✅ Detected your changes to LaTeX and diagrams
2. ✅ Generated the page translation diagram
3. ✅ Compiled a 300+ page PDF including your new chapter
4. ✅ Created web versions of all diagrams
5. ✅ Built a searchable documentation site
6. ✅ Published everything to GitHub Pages
7. ✅ Made it accessible to the world

**Time elapsed:** ~15 minutes  
**Manual work:** Just writing the content  
**Infrastructure:** Fully automated

## Advanced: Iterating on the Chapter

### Quick Fix to Text

If you notice a typo:

```bash
vim whitepaper/ch13-memory-management.tex
# Fix the typo
git commit -am "Fix typo in chapter 13"
git push
```

Pipeline re-runs automatically. Only stages that need updating will execute.

### Adding More Diagrams

Create another diagram:

```bash
cd diagrams/tikz
vim tlb-architecture.tex
# Create TikZ code
```

Reference it in your chapter:

```latex
\begin{figure}[htbp]
\centering
\includegraphics[width=0.8\textwidth]{figures/tlb-architecture.pdf}
\caption{TLB architecture in i386}
\label{fig:tlb}
\end{figure}
```

Commit and push:

```bash
git add diagrams/tikz/tlb-architecture.tex
git add whitepaper/ch13-memory-management.tex
git commit -m "Add TLB architecture diagram"
git push
```

### Testing Locally First

Before pushing, test compilation locally:

```bash
cd whitepaper

# Quick test (single pass)
pdflatex ch13-memory-management.tex

# Full test (with references)
latexmk -pdf MINIX-3.4-Comprehensive-Technical-Analysis.tex

# View result
open MINIX-3.4-Comprehensive-Technical-Analysis.pdf
```

If it compiles locally, it will compile in CI.

## Example: Data-Driven Diagram

For a more complex example, let's create a diagram that shows actual data from MINIX analysis.

### Extract Data with Python

```python
# tools/extract_memory_data.py

def analyze_minix_memory():
    """Extract memory management data from MINIX source"""
    
    # Parse source files
    kernel_path = "minix-source/minix/kernel"
    
    data = {
        'page_sizes': [],
        'memory_regions': [],
        'allocation_counts': {},
    }
    
    # ... analysis code ...
    
    # Save for diagram generation
    with open('diagrams/data/memory-stats.json', 'w') as f:
        json.dump(data, f)
    
    return data
```

### Generate Diagram from Data

```python
# tools/tikz_generator.py

def generate_memory_diagram(data_file, output_dir):
    """Create TikZ diagram from memory analysis data"""
    
    with open(data_file) as f:
        data = json.load(f)
    
    # Create TikZ code using actual data
    tikz = generate_tikz_from_template(
        'memory-regions-template.tex',
        data
    )
    
    output = os.path.join(output_dir, 'memory-regions.tex')
    with open(output, 'w') as f:
        f.write(tikz)
```

### Pipeline Automatically:

1. Runs `extract_memory_data.py` → produces JSON
2. Runs `tikz_generator.py` → creates `.tex` from JSON
3. Compiles `.tex` → creates PDF
4. Includes PDF in whitepaper
5. Publishes to web

**Result:** Your diagrams always reflect current code analysis!

## Workflow Variations

### Feature Branch Development

Work on a branch without deploying:

```bash
git checkout -b feature/advanced-memory-chapter
# Make changes
git push origin feature/advanced-memory-chapter
```

Pipeline runs but **doesn't deploy**. Review artifacts in the PR, then:

```bash
# When ready
git checkout main
git merge feature/advanced-memory-chapter
git push origin main  # NOW it deploys
```

### Rapid Iteration

For quick edits, use selective compilation:

```latex
% In main document
\includeonly{ch13-memory-management}  % Only compile this chapter
```

This speeds up local testing significantly.

### Collaboration

Multiple authors can work simultaneously:

```bash
# Author 1: Works on chapter 13
git checkout -b author1/memory-chapter
# ... commits ...

# Author 2: Works on chapter 14
git checkout -b author2/security-chapter
# ... commits ...

# Merge when ready
git checkout main
git merge author1/memory-chapter
git merge author2/security-chapter
git push  # Single deployment with both chapters
```

## Monitoring and Debugging

### View Build Logs

If something fails:

1. Click on failed job in Actions
2. Expand failed step
3. Read error messages
4. Download artifacts for full logs

### Common Issues and Fixes

**LaTeX compilation error:**
```
! Undefined control sequence
```
Fix: Check for typos in LaTeX commands

**Missing diagram:**
```
! Package pdftex.def Error: File `diagram.pdf' not found
```
Fix: Verify diagram was generated in previous stage

**Workflow syntax error:**
```
Invalid workflow file
```
Fix: Validate YAML syntax locally first

## Best Practices Learned

1. **Commit often, push when ready**
   - Make many local commits
   - Test locally before pushing
   - Each push triggers ~15min of CI

2. **Use meaningful commit messages**
   - Makes it easy to track what triggered each build
   - Helpful when reviewing workflow runs

3. **Test locally first**
   - Run `pdflatex` locally
   - Check for errors before CI
   - Saves time and CI minutes

4. **Use branches for experiments**
   - Don't deploy half-finished work
   - Review in PR before merging
   - Keep `main` branch always deployable

5. **Monitor first few runs**
   - Watch Actions tab initially
   - Verify everything works
   - Download artifacts to inspect

## Conclusion

The TeXplosion pipeline transforms your development workflow:

**Before:**
1. Edit LaTeX
2. Compile locally
3. Fix errors
4. Repeat
5. When done, manually upload PDF somewhere
6. Email link to collaborators
7. Update when you remember

**After:**
1. Edit LaTeX
2. Push to GitHub
3. ☕ Get coffee (15 min)
4. Share live link: `https://you.github.io/repo/`
5. Updates automatically on every push

**The magic:** Your repository IS your publication platform.

---

## Next Steps

Try it yourself:

1. Create a small test chapter
2. Add a simple diagram
3. Commit and push
4. Watch the TeXplosion happen
5. Share your live documentation!

**Happy Publishing!** 🎉📚✨
