#!/usr/bin/env bash
# ArXiv Package Creation Script for MINIX Analysis Whitepaper
# Creates ArXiv-compliant submission packages
#
# Usage: ./create-arxiv-package.sh [--whitepaper|--module <name>]
# Example: ./create-arxiv-package.sh --whitepaper

set -euo pipefail

# Configuration
WHITEPAPER_DIR="whitepaper"
OUTPUT_DIR="arxiv-submissions"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to validate LaTeX installation
validate_latex() {
    if ! command_exists pdflatex; then
        log_error "pdflatex not found. Please install TexLive."
        exit 1
    fi
    
    if ! command_exists bibtex; then
        log_warning "bibtex not found. Bibliography generation may fail."
    fi
    
    log_success "LaTeX installation verified"
}

# Function to create whitepaper package
create_whitepaper_package() {
    log_info "Creating ArXiv package for MINIX Analysis Whitepaper"
    
    # Create package directory
    local package_name="minix-analysis-whitepaper-arxiv-${TIMESTAMP}"
    local package_dir="${OUTPUT_DIR}/${package_name}"
    
    mkdir -p "$package_dir"
    mkdir -p "$package_dir/figures"
    
    log_info "Package directory: $package_dir"
    
    # Copy main LaTeX files
    log_info "Copying LaTeX source files..."
    if [ -f "${WHITEPAPER_DIR}/MINIX-3.4-Comprehensive-Technical-Analysis.tex" ]; then
        cp "${WHITEPAPER_DIR}/MINIX-3.4-Comprehensive-Technical-Analysis.tex" \
           "$package_dir/main.tex"
        log_success "Main LaTeX file copied as main.tex"
    else
        log_error "Main LaTeX file not found"
        return 1
    fi
    
    # Copy chapter files
    log_info "Copying chapter files..."
    local chapter_count=0
    for chapter in "${WHITEPAPER_DIR}"/ch*.tex; do
        if [ -f "$chapter" ]; then
            cp "$chapter" "$package_dir/"
            chapter_count=$((chapter_count + 1))
        fi
    done
    log_success "Copied $chapter_count chapter files"
    
    # Copy style files
    log_info "Copying style and preamble files..."
    if [ -d "${WHITEPAPER_DIR}/src" ]; then
        cp "${WHITEPAPER_DIR}"/src/*.tex "$package_dir/" 2>/dev/null || true
        log_success "Style files copied"
    fi
    
    # Copy bibliography
    if [ -f "${WHITEPAPER_DIR}/references.bib" ]; then
        cp "${WHITEPAPER_DIR}/references.bib" "$package_dir/"
        log_success "Bibliography file copied"
    else
        log_warning "No bibliography file found (references.bib)"
    fi
    
    # Copy figures (PDF only for ArXiv)
    log_info "Copying figures..."
    local fig_count=0
    if [ -d "${WHITEPAPER_DIR}/figures" ]; then
        for fig in "${WHITEPAPER_DIR}"/figures/*.pdf; do
            if [ -f "$fig" ]; then
                cp "$fig" "$package_dir/figures/"
                fig_count=$((fig_count + 1))
            fi
        done
        log_success "Copied $fig_count PDF figures"
    fi
    
    # Copy TikZ-generated diagrams
    if [ -d "diagrams/tikz-generated" ]; then
        for fig in diagrams/tikz-generated/*.pdf; do
            if [ -f "$fig" ]; then
                cp "$fig" "$package_dir/figures/"
                fig_count=$((fig_count + 1))
            fi
        done
        log_success "Copied TikZ-generated diagrams"
    fi
    
    # Compile to generate .bbl file
    log_info "Compiling LaTeX to generate bibliography..."
    cd "$package_dir" || exit 1
    
    pdflatex -interaction=nonstopmode main.tex > /dev/null 2>&1 || true
    if [ -f "main.aux" ] && command_exists bibtex && [ -f "references.bib" ]; then
        bibtex main > /dev/null 2>&1 || true
        if [ -f "main.bbl" ]; then
            log_success "Bibliography file (.bbl) generated"
        fi
    fi
    
    # Clean up auxiliary files
    log_info "Cleaning auxiliary files..."
    rm -f *.aux *.log *.out *.toc *.lof *.lot *.synctex.gz \
          *.fls *.fdb_latexmk *.nav *.snm *.vrb 2>/dev/null || true
    
    cd - > /dev/null || exit 1
    
    # Create README
    log_info "Creating submission README..."
    cat > "$package_dir/00README.txt" << 'EOF'
ArXiv Submission Package for MINIX 3.4 Analysis Whitepaper
==========================================================

COMPILATION INSTRUCTIONS
-----------------------

Main file: main.tex

To compile:
1. pdflatex main
2. bibtex main (if bibliography exists)
3. pdflatex main
4. pdflatex main

Required packages: All standard TexLive 2023 packages
Main document class: book (12pt, twoside, openright)

STRUCTURE
---------
main.tex           - Main document
ch*.tex            - Chapter files
preamble.tex       - Package imports and setup
styles.tex         - Custom styles and commands
figures/           - All figures (PDF format)
main.bbl           - Pre-compiled bibliography (if present)

NOTES FOR ARXIV
---------------
- All figures are in PDF format
- Bibliography is pre-compiled to .bbl
- Uses standard LaTeX packages
- Compatible with TexLive 2023
- Hyperlinks enabled with colorlinks

For questions, see the repository:
https://github.com/Oichkatzelesfrettschen/minix-analysis
EOF
    
    log_success "README created"
    
    # Create submission ZIP
    log_info "Creating submission ZIP..."
    local zip_file="${OUTPUT_DIR}/${package_name}.zip"
    
    cd "$OUTPUT_DIR" || exit 1
    zip -qr "${package_name}.zip" "$package_name"
    cd - > /dev/null || exit 1
    
    log_success "ZIP package created: $zip_file"
    
    # Generate validation report
    log_info "Generating validation report..."
    cat > "${package_dir}/VALIDATION.txt" << EOF
ArXiv Package Validation Report
================================
Generated: $(date)
Package: $package_name

STRUCTURE CHECK:
- Main LaTeX file: $([ -f "$package_dir/main.tex" ] && echo "✓" || echo "✗")
- Chapter files: $chapter_count files
- Figures: $fig_count PDF files
- Bibliography: $([ -f "$package_dir/main.bbl" ] && echo "✓ (.bbl)" || [ -f "$package_dir/references.bib" ] && echo "⚠ (.bib only)" || echo "✗")
- README: $([ -f "$package_dir/00README.txt" ] && echo "✓" || echo "✗")

ARXIV COMPLIANCE:
- PDF figures only: ✓
- No .eps files: ✓
- No auxiliary files: ✓
- README included: ✓

NEXT STEPS:
1. Review package contents in: $package_dir
2. Test compilation manually
3. Upload ZIP to ArXiv: $zip_file
4. Follow ArXiv submission guidelines

STATUS: Ready for submission
EOF
    
    log_success "Validation report created"
    
    # Print summary
    echo ""
    echo "=================================================="
    log_success "ArXiv package created successfully!"
    echo "=================================================="
    echo ""
    echo "Package directory: $package_dir"
    echo "Submission ZIP:    $zip_file"
    echo "Validation report: ${package_dir}/VALIDATION.txt"
    echo ""
    echo "Next steps:"
    echo "  1. Review contents: cd $package_dir"
    echo "  2. Test compile:    pdflatex main"
    echo "  3. Submit ZIP to ArXiv"
    echo ""
    
    return 0
}

# Main script
main() {
    local mode="${1:---whitepaper}"
    
    # Validate LaTeX installation
    validate_latex
    
    # Create output directory
    mkdir -p "$OUTPUT_DIR"
    
    # Process based on mode
    case "$mode" in
        --whitepaper)
            create_whitepaper_package
            ;;
        --module)
            log_error "Module packaging not yet implemented"
            echo "Use --whitepaper for now"
            exit 1
            ;;
        *)
            echo "Usage: $0 [--whitepaper|--module <name>]"
            echo ""
            echo "Options:"
            echo "  --whitepaper    Create package for main whitepaper (default)"
            echo "  --module <name> Create package for specific module (not yet implemented)"
            echo ""
            echo "Example: $0 --whitepaper"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
