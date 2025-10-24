# Quick Start Guide: Math & Science Research Hub

This guide provides a concise, step-by-step process to get your development environment set up for the Math & Science Research Hub. For detailed instructions, troubleshooting, and optional configurations, please refer to the comprehensive `INSTALLATION_REQUIREMENTS.md` in the project root.

## 1. System Requirements

*   **Operating System:** Windows 11 (64-bit)
*   **RAM:** 8 GB minimum (16 GB recommended)
*   **Disk Space:** 10 GB minimum
*   **CPU:** Dual-core (quad-core recommended)
*   **PowerShell:** 5.1+ (Execution Policy: `RemoteSigned` or `Unrestricted`)

## 2. Core Dependencies Installation

### 2.1 Python 3.10+

1.  **Download:** Visit [https://www.python.org/downloads/](https://www.python.org/downloads/) and download the latest Python 3.10+ Windows installer (64-bit).
2.  **Install:** Run the installer. **CRITICAL:** Check "Add Python to PATH" at the bottom of the installer window. Click "Install Now".
3.  **Verify:** Open a new PowerShell window and run:
    ```powershell
    python --version
    pip --version
    ```
    Expected: Python 3.10.x+ and pip 24.x+.

### 2.2 LaTeX Distribution (Choose One: MiKTeX or TeX Live)

#### Option A: MiKTeX

1.  **Download:** Visit [https://miktex.org/download](https://miktex.org/download) and download the 64-bit Basic Installer.
2.  **Install:** Run the installer. During setup, ensure "Install missing packages on-the-fly: Yes" is selected (CRITICAL).
3.  **Configure (MiKTeX Console):**
    *   Open MiKTeX Console (search in Start Menu).
    *   Go to the "Updates" tab and install all available updates.
    *   Go to the "Settings" tab and ensure "Install missing packages on-the-fly: Yes" is set.
4.  **Verify:** Open PowerShell and run:
    ```powershell
    pdflatex --version
    mpm --version
    ```

#### Option B: TeX Live

1.  **Download:** Visit [https://www.tug.org/texlive/acquire-netinstall.html](https://www.tug.org/texlive/acquire-netinstall.html) and download `install-tl-windows.exe`.
2.  **Install:** Run the installer **as Administrator**. In the GUI, select "full" installation scheme and ensure "Add TeX Live to system PATH" is checked (CRITICAL).
3.  **Verify:** Open PowerShell and run:
    ```powershell
    pdflatex --version
    tlmgr --version
    ```

## 3. Repository Setup

1.  **Clone Repository:**
    ```powershell
    # Navigate to your desired parent directory (e.g., C:\Users\YourUser\Git-Projects)
    cd C:\Users\YourUser\Git-Projects

    # Clone the repository (replace with actual URL if public, or use local path)
    git clone https://github.com/username/Math_Science.git
    cd Math_Science
    ```
    *(If Git is not installed, refer to `INSTALLATION_REQUIREMENTS.md` for Git installation options.)*

## 4. Initial Verification

Navigate to the repository root in PowerShell and run the following commands to ensure core functionality:

```powershell
# Test Python stdlib imports
python -c "import re, os, csv, argparse, pathlib, collections, subprocess, sys; print('Python stdlib modules: OK')"

# Test LaTeX compilation (requires synthesis/preamble.tex and main.tex to exist)
# This assumes you have already cloned the repository and are in its root.
cd synthesis
pdflatex -interaction=nonstopmode main.tex
# Check for main.pdf in synthesis/ directory
```

## 5. Next Steps

*   **Full Details & Troubleshooting:** For any issues, detailed troubleshooting, optional Python packages (e.g., for PDF/OCR), VS Code setup, or virtual environments, consult the comprehensive `INSTALLATION_REQUIREMENTS.md` file.
*   **Project Usage:** Refer to the main `README.md` for an overview of the project, build commands, and development conventions.
