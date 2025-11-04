#!/usr/bin/env python3
"""
TeXplosion Pipeline Validator

This script validates your local setup for the TeXplosion pipeline.
Run this before pushing to ensure everything will work in CI.

Usage:
    python scripts/validate-texplosion-setup.py
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import List, Tuple, Dict

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def check_command(cmd: str, name: str, required: bool = True) -> Tuple[bool, str]:
    """Check if a command exists and is executable"""
    try:
        result = subprocess.run(
            [cmd, '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            # Get version from output
            version = result.stdout.split('\n')[0][:60]
            return True, version
        else:
            return False, "Command exists but --version failed"
    except FileNotFoundError:
        return False, "Command not found"
    except subprocess.TimeoutExpired:
        return False, "Command timeout"
    except Exception as e:
        return False, f"Error: {str(e)}"

def check_file_exists(path: str, name: str, required: bool = True) -> Tuple[bool, str]:
    """Check if a file exists"""
    if os.path.exists(path):
        size = os.path.getsize(path)
        return True, f"Found ({size:,} bytes)"
    else:
        return False, "File not found"

def check_directory_exists(path: str, name: str, required: bool = True) -> Tuple[bool, str]:
    """Check if a directory exists and has contents"""
    if os.path.isdir(path):
        files = list(Path(path).rglob('*'))
        file_count = len([f for f in files if f.is_file()])
        return True, f"Found ({file_count} files)"
    else:
        return False, "Directory not found"

def print_status(name: str, status: bool, message: str, required: bool = True):
    """Print a status line with color coding"""
    if status:
        symbol = f"{Colors.GREEN}✓{Colors.END}"
    elif not required:
        symbol = f"{Colors.YELLOW}⚠{Colors.END}"
    else:
        symbol = f"{Colors.RED}✗{Colors.END}"
    
    req_str = "" if required else " (optional)"
    print(f"{symbol} {name:<40} {message}{req_str}")

def validate_python_packages() -> List[Tuple[str, bool, str]]:
    """Check if required Python packages are installed"""
    packages = [
        ('matplotlib', True),
        ('pandas', True),
        ('numpy', True),
        ('pyyaml', True),
        ('plotly', False),
    ]
    
    results = []
    for package, required in packages:
        try:
            __import__(package)
            results.append((package, True, "Installed", required))
        except ImportError:
            results.append((package, False, "Not installed", required))
    
    return results

def validate_latex_packages() -> List[Tuple[str, bool, str]]:
    """Check if required LaTeX packages are available"""
    # Check if kpsewhich exists (part of TeX distribution)
    try:
        subprocess.run(['kpsewhich', '--version'], 
                      capture_output=True, check=True, timeout=5)
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return [("TeX Distribution", False, "kpsewhich not found", True)]
    
    packages = [
        ('tikz', True),
        ('pgfplots', True),
        ('amsmath', True),
        ('graphicx', True),
        ('hyperref', True),
    ]
    
    results = []
    for package, required in packages:
        try:
            result = subprocess.run(
                ['kpsewhich', f'{package}.sty'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                results.append((package, True, "Available", required))
            else:
                results.append((package, False, "Not found", required))
        except subprocess.TimeoutExpired:
            results.append((package, False, "Check timeout", required))
    
    return results

def validate_workflow_yaml() -> Tuple[bool, str]:
    """Validate the workflow YAML file"""
    workflow_path = '.github/workflows/texplosion-pages.yml'
    
    if not os.path.exists(workflow_path):
        return False, "Workflow file not found"
    
    try:
        import yaml
        with open(workflow_path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Check for required keys
        if 'jobs' not in data:
            return False, "Missing 'jobs' section"
        
        if 'name' not in data:
            return False, "Missing 'name' field"
        
        jobs = data.get('jobs', {})
        expected_jobs = ['generate-diagrams', 'compile-latex', 'build-pages']
        found_jobs = [job for job in expected_jobs if job in jobs]
        
        return True, f"Valid ({len(found_jobs)}/{len(expected_jobs)} jobs found)"
    except yaml.YAMLError as e:
        return False, f"YAML parse error: {str(e)[:50]}"
    except Exception as e:
        return False, f"Error: {str(e)[:50]}"

def main():
    """Main validation routine"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}TeXplosion Pipeline Validator{Colors.END}\n")
    print("Checking your local setup for compatibility with the CI pipeline...\n")
    
    # Check system commands
    print(f"{Colors.BOLD}System Commands:{Colors.END}")
    commands = [
        ('python3', 'Python 3', True),
        ('git', 'Git', True),
        ('pdflatex', 'LaTeX', True),
        ('latexmk', 'LaTeXmk', True),
        ('convert', 'ImageMagick', True),
        ('pdf2svg', 'pdf2svg', False),
        ('docker', 'Docker', False),
        ('qemu-system-i386', 'QEMU i386', False),
    ]
    
    for cmd, name, required in commands:
        status, message = check_command(cmd, name, required)
        print_status(name, status, message, required)
    
    # Check Python packages
    print(f"\n{Colors.BOLD}Python Packages:{Colors.END}")
    for package, status, message, required in validate_python_packages():
        print_status(f"Python: {package}", status, message, required)
    
    # Check LaTeX packages
    print(f"\n{Colors.BOLD}LaTeX Packages:{Colors.END}")
    latex_results = validate_latex_packages()
    for package, status, message, required in latex_results:
        print_status(f"LaTeX: {package}", status, message, required)
    
    # Check directory structure
    print(f"\n{Colors.BOLD}Directory Structure:{Colors.END}")
    directories = [
        ('whitepaper', 'Whitepaper sources', True),
        ('diagrams/tikz', 'TikZ templates', True),
        ('tools', 'Analysis tools', True),
        ('docs', 'Documentation', True),
        ('.github/workflows', 'GitHub workflows', True),
    ]
    
    for path, name, required in directories:
        status, message = check_directory_exists(path, name, required)
        print_status(name, status, message, required)
    
    # Check important files
    print(f"\n{Colors.BOLD}Important Files:{Colors.END}")
    files = [
        ('.github/workflows/texplosion-pages.yml', 'TeXplosion workflow', True),
        ('requirements.txt', 'Python requirements', True),
        ('README.md', 'README', True),
        ('docs/TEXPLOSION-PIPELINE.md', 'Pipeline docs', True),
    ]
    
    for path, name, required in files:
        status, message = check_file_exists(path, name, required)
        print_status(name, status, message, required)
    
    # Validate workflow YAML
    print(f"\n{Colors.BOLD}Workflow Validation:{Colors.END}")
    status, message = validate_workflow_yaml()
    print_status("Workflow YAML", status, message, True)
    
    # Check for main LaTeX document
    print(f"\n{Colors.BOLD}LaTeX Documents:{Colors.END}")
    main_docs = [
        'whitepaper/MINIX-3.4-Comprehensive-Technical-Analysis.tex',
        'whitepaper/master.tex',
        'latex/minix-complete-analysis.tex',
    ]
    
    found_main = False
    for doc in main_docs:
        if os.path.exists(doc):
            print_status(f"Main document: {doc}", True, "Found", True)
            found_main = True
            break
    
    if not found_main:
        print_status("Main LaTeX document", False, "No main document found", True)
    
    # Summary
    print(f"\n{Colors.BOLD}Summary:{Colors.END}")
    print("\nNext steps:")
    print("1. Install any missing required tools")
    print("2. Fix any errors marked with ✗")
    print("3. Consider installing optional tools marked with ⚠")
    print("4. Test LaTeX compilation locally:")
    print(f"   {Colors.BLUE}cd whitepaper && pdflatex main.tex{Colors.END}")
    print("5. Test Python tools:")
    print(f"   {Colors.BLUE}python3 tools/minix_source_analyzer.py --help{Colors.END}")
    print("6. When ready, push to trigger the pipeline:")
    print(f"   {Colors.BLUE}git push origin main{Colors.END}")
    
    print(f"\n{Colors.BOLD}Documentation:{Colors.END}")
    print("- Quick Start: docs/TEXPLOSION-QUICKSTART.md")
    print("- Full Guide:  docs/TEXPLOSION-PIPELINE.md")
    print("- FAQ:         docs/TEXPLOSION-FAQ.md")
    print()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Validation interrupted.{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Error: {str(e)}{Colors.END}")
        sys.exit(1)
