#!/usr/bin/env python3
"""
TikZ Converter - DOT to LaTeX/TikZ via dot2tex
"""

import subprocess
from pathlib import Path
from typing import Optional


class TikZConverter:
    """Convert Graphviz DOT files to TikZ for LaTeX"""

    def __init__(self, dot2tex_path: str = "dot2tex"):
        self.dot2tex = dot2tex_path

    def convert(
        self,
        dot_file: Path,
        output_file: Path,
        prog: str = "dot",
        template: Optional[str] = None,
        standalone: bool = True
    ) -> bool:
        """
        Convert DOT to TikZ

        Args:
            dot_file: Input .dot file
            output_file: Output .tex file
            prog: Graphviz layout program (dot, neato, circo, fdp)
            template: Optional dot2tex template
            standalone: Generate standalone LaTeX document

        Returns:
            True if successful
        """
        cmd = [
            self.dot2tex,
            f"--prog={prog}",
            "--tikzedgelabels",  # Use TikZ for edge labels
            "--autosize",  # Auto-scale to fit
            f"--output={output_file}",
        ]

        if template:
            cmd.append(f"--template={template}")

        if standalone:
            # Generate complete compilable document
            cmd.append("--format=tikz")
            cmd.append("--tikzedgelabels")
            cmd.append("--crop")  # Crop to content
            cmd.append("--codeonly")  # Only TikZ code, no preamble - we provide our own

        cmd.append(str(dot_file))

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            if standalone:
                # Wrap in standalone document
                tikz_content = output_file.read_text()
                wrapped = self._wrap_standalone(tikz_content)
                output_file.write_text(wrapped)

            print(f"✅ Converted {dot_file.name} → {output_file.name}")
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ dot2tex failed: {e.stderr}")
            return False
        except FileNotFoundError:
            print(f"❌ dot2tex not found. Install with: sudo pacman -S dot2tex")
            return False

    def _wrap_standalone(self, tikz_code: str) -> str:
        """Wrap TikZ code in standalone document"""
        return f"""\\documentclass[tikz,border=5pt]{{standalone}}
\\usepackage{{tikz}}
\\usepackage{{lmodern}}  % Latin Modern fonts
\\usetikzlibrary{{shapes,arrows,positioning,calc}}

\\begin{{document}}
\\begin{{tikzpicture}}
{tikz_code}
\\end{{tikzpicture}}
\\end{{document}}
"""

    def compile_pdf(self, tex_file: Path, output_dir: Optional[Path] = None) -> bool:
        """Compile TikZ .tex to PDF using pdflatex"""
        if output_dir is None:
            output_dir = tex_file.parent

        cmd = [
            "pdflatex",
            "-interaction=nonstopmode",
            "-halt-on-error",
            f"-output-directory={output_dir}",
            str(tex_file)
        ]

        try:
            # Don't use check=True - pdflatex may return non-zero on warnings
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=output_dir)
            pdf_file = tex_file.with_suffix('.pdf')

            # Check if PDF was actually created (success criterion)
            if pdf_file.exists():
                print(f"✅ Compiled {tex_file.name} → {pdf_file.name}")
                return True
            else:
                print(f"❌ PDF not generated: {result.stderr[:500] if result.stderr else 'no error output'}")
                return False

        except Exception as e:
            print(f"❌ pdflatex exception: {str(e)[:500]}")
            return False

    def dot_to_pdf(self, dot_file: Path, output_pdf: Path, prog: str = "dot") -> bool:
        """
        Complete pipeline: DOT → TikZ → PDF

        Args:
            dot_file: Input .dot file
            output_pdf: Output .pdf file
            prog: Graphviz layout program

        Returns:
            True if successful
        """
        tex_file = output_pdf.with_suffix('.tex')

        # Convert DOT → TikZ
        if not self.convert(dot_file, tex_file, prog=prog, standalone=True):
            return False

        # Compile TikZ → PDF
        if not self.compile_pdf(tex_file, output_pdf.parent):
            return False

        return True


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Convert DOT graphs to TikZ/PDF")
    parser.add_argument("dot_file", type=Path, help="Input .dot file")
    parser.add_argument("-o", "--output", type=Path, help="Output .tex or .pdf file", required=True)
    parser.add_argument("-p", "--prog", default="dot", choices=['dot', 'neato', 'circo', 'fdp'],
                        help="Graphviz layout program")
    parser.add_argument("--pdf", action='store_true', help="Generate PDF (not just .tex)")
    parser.add_argument("--no-standalone", action='store_true', help="Don't wrap in standalone document")

    args = parser.parse_args()

    converter = TikZConverter()

    if args.pdf or args.output.suffix == '.pdf':
        # Full pipeline: DOT → TikZ → PDF
        success = converter.dot_to_pdf(args.dot_file, args.output, prog=args.prog)
    else:
        # Just DOT → TikZ
        success = converter.convert(
            args.dot_file,
            args.output,
            prog=args.prog,
            standalone=not args.no_standalone
        )

    exit(0 if success else 1)


if __name__ == "__main__":
    main()
