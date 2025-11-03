#!/usr/bin/env python3
"""
Figure Extraction Tool for MINIX Whitepaper
Extract TikZ diagrams and pgfplots charts from master.pdf at 300 DPI
"""

import os
import sys
import subprocess
import csv
from pathlib import Path
from datetime import datetime

class FigureExtractor:
    """Extract and manage figures from PDF"""
    
    def __init__(self, pdf_path, output_dir):
        self.pdf_path = Path(pdf_path)
        self.output_dir = Path(output_dir)
        self.dpi = 300  # Publication standard
        self.figures = []
        
        # Create subdirectories
        (self.output_dir / "tikz-diagrams").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "pgfplots-charts").mkdir(parents=True, exist_ok=True)
        
    def get_pdf_page_count(self):
        """Get total pages in PDF"""
        try:
            result = subprocess.run(
                ["pdfinfo", str(self.pdf_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            for line in result.stdout.split('\n'):
                if 'Pages' in line:
                    return int(line.split(':')[1].strip())
        except Exception as e:
            print(f"Error getting page count: {e}")
        return None
    
    def extract_page_range(self, start_page, end_page, output_name, figure_type):
        """Extract specific page range to PNG at 300 DPI"""
        output_path = self.output_dir / figure_type / f"{output_name}.png"
        
        # Use Ghostscript for high-quality conversion
        try:
            subprocess.run([
                "gs",
                "-q",
                "-dNOPAUSE",
                "-dBATCH",
                "-sDEVICE=png16m",
                f"-r{self.dpi}",
                f"-dFirstPage={start_page}",
                f"-dLastPage={end_page}",
                f"-sOutputFile={str(output_path)}",
                str(self.pdf_path)
            ], check=True, timeout=30)
            
            file_size = output_path.stat().st_size
            print(f"✓ Extracted: {output_name} ({file_size/1024:.1f} KB)")
            return True
        except Exception as e:
            print(f"✗ Failed to extract {output_name}: {e}")
            return False
    
    def optimize_png(self, png_path):
        """Optimize PNG file size using optipng"""
        try:
            original_size = png_path.stat().st_size
            subprocess.run([
                "optipng",
                "-o2",  # Optimization level 2 (good balance)
                str(png_path)
            ], check=True, timeout=30, capture_output=True)
            
            optimized_size = png_path.stat().st_size
            reduction = ((original_size - optimized_size) / original_size) * 100
            print(f"  Optimized: {optimized_size/1024:.1f} KB (reduced {reduction:.1f}%)")
            return optimized_size
        except subprocess.CalledProcessError:
            # optipng not available, return original size
            return original_size
        except Exception as e:
            print(f"  Warning: Could not optimize {png_path.name}: {e}")
            return png_path.stat().st_size
    
    def register_figure(self, name, figure_type, chapter, description, page_num):
        """Register figure in manifest"""
        self.figures.append({
            'figure_id': len(self.figures) + 1,
            'name': name,
            'type': figure_type,
            'chapter': chapter,
            'description': description,
            'page': page_num,
            'format': 'PNG',
            'dpi': self.dpi,
            'timestamp': datetime.now().isoformat()
        })
    
    def save_manifest(self):
        """Save figure manifest as CSV"""
        manifest_path = self.output_dir / "FIGURES-MANIFEST.csv"
        
        try:
            with open(manifest_path, 'w', newline='') as f:
                fieldnames = ['figure_id', 'name', 'type', 'chapter', 'description', 
                             'page', 'format', 'dpi', 'timestamp']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.figures)
            
            print(f"\n✓ Manifest saved: {manifest_path}")
            print(f"  Total figures: {len(self.figures)}")
        except Exception as e:
            print(f"✗ Error saving manifest: {e}")
    
    def print_summary(self):
        """Print extraction summary"""
        print("\n" + "="*60)
        print("FIGURE EXTRACTION SUMMARY")
        print("="*60)
        
        by_type = {}
        for fig in self.figures:
            fig_type = fig['type']
            if fig_type not in by_type:
                by_type[fig_type] = 0
            by_type[fig_type] += 1
        
        for fig_type, count in sorted(by_type.items()):
            print(f"{fig_type}: {count} figures")
        
        print(f"Total: {len(self.figures)} figures")
        print("="*60 + "\n")

def main():
    # Configuration
    pdf_path = "../master.pdf"
    output_dir = "."
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF not found at {pdf_path}")
        sys.exit(1)
    
    extractor = FigureExtractor(pdf_path, output_dir)
    
    # Check dependencies
    required_tools = ["gs", "pdfinfo"]
    for tool in required_tools:
        try:
            subprocess.run([tool, "--version"], capture_output=True, timeout=5)
        except FileNotFoundError:
            print(f"Error: {tool} not found. Install ghostscript (apt install ghostscript)")
            sys.exit(1)
    
    print("MINIX Whitepaper Figure Extraction Tool")
    print("========================================")
    print(f"PDF: {pdf_path}")
    print(f"Output: {output_dir}")
    print(f"DPI: {extractor.dpi}")
    print()
    
    # Get PDF info
    page_count = extractor.get_pdf_page_count()
    if page_count:
        print(f"PDF pages: {page_count}")
    
    # FIGURE EXTRACTION CONFIGURATION
    # Manually specified based on document structure
    # Format: (start_page, end_page, name, type, chapter, description)
    
    figures_to_extract = [
        # Chapter 1: Introduction
        (18, 18, "fig-01-microkernel-architecture", "tikz-diagrams", 
         "Chapter 1", "MINIX 3.4 Microkernel Architecture Overview"),
        
        # Chapter 2: Fundamentals
        (29, 29, "fig-02-message-passing", "tikz-diagrams",
         "Chapter 2", "Synchronous Message Passing Sequence"),
        (32, 32, "fig-03-memory-layout", "tikz-diagrams",
         "Chapter 2", "x86 Memory Layout and CPU State"),
        
        # Chapter 3: Methodology
        (42, 42, "fig-04-data-pipeline", "tikz-diagrams",
         "Chapter 3", "Data Pipeline Architecture"),
        (45, 45, "fig-05-workflow", "tikz-diagrams",
         "Chapter 3", "Experimental Workflow"),
        
        # Chapter 4: Boot Metrics (PILOT 1)
        (55, 55, "fig-06-boot-flowchart", "tikz-diagrams",
         "Chapter 4", "MINIX 3.4 Boot Phase Flowchart"),
        (58, 58, "fig-07-cpu-registers", "pgfplots-charts",
         "Chapter 4", "CPU Register State During Boot Phases"),
        (60, 60, "fig-08-boot-durations", "pgfplots-charts",
         "Chapter 4", "Boot Phase Durations (Measured in QEMU)"),
        (62, 62, "fig-09-boot-timeline", "tikz-diagrams",
         "Chapter 4", "Boot Sequence Timeline"),
        (65, 65, "fig-10-memory-allocation", "pgfplots-charts",
         "Chapter 4", "Memory Allocation During Boot"),
        (67, 67, "fig-11-boot-detailed", "tikz-diagrams",
         "Chapter 4", "Detailed Boot Sequence Flowchart"),
        (70, 70, "fig-12-boot-distribution", "pgfplots-charts",
         "Chapter 4", "Boot Time Distribution"),
        
        # Chapter 5: Error Analysis
        (82, 82, "fig-13-error-catalog", "pgfplots-charts",
         "Chapter 5", "MINIX 3.4 Error Catalog (15-Error Registry)"),
        (85, 85, "fig-14-error-detection-algo", "tikz-diagrams",
         "Chapter 5", "Error Detection Algorithm Flowchart"),
        (87, 87, "fig-15-error-regex", "pgfplots-charts",
         "Chapter 5", "Error Detection Regex Patterns"),
        (89, 89, "fig-16-error-frequency", "pgfplots-charts",
         "Chapter 5", "Error Frequency and Impact"),
        (91, 91, "fig-17-error-graph", "tikz-diagrams",
         "Chapter 5", "Error Causal Relationship Graph"),
        
        # Chapter 6: Architecture (PILOT 2)
        (102, 102, "fig-18-syscall-selection", "pgfplots-charts",
         "Chapter 6", "System Call Mechanism Selection"),
        (105, 105, "fig-19-syscall-latency", "pgfplots-charts",
         "Chapter 6", "System Call Latency Comparison"),
        (107, 107, "fig-20-system-arch", "tikz-diagrams",
         "Chapter 6", "Complete MINIX 3.4 System Architecture"),
        (110, 110, "fig-21-process-ipc", "tikz-diagrams",
         "Chapter 6", "Process and IPC Architecture"),
        
        # Chapter 10: Error Reference
        (180, 180, "fig-22-error-recovery", "tikz-diagrams",
         "Chapter 10", "Error Detection and Recovery Flowchart"),
    ]
    
    print(f"\nExtracting {len(figures_to_extract)} figures...")
    print("-" * 60)
    
    extracted_count = 0
    for start, end, name, fig_type, chapter, desc in figures_to_extract:
        if extractor.extract_page_range(start, end, name, fig_type):
            png_path = extractor.output_dir / fig_type / f"{name}.png"
            extractor.optimize_png(png_path)
            extractor.register_figure(name, fig_type, chapter, desc, start)
            extracted_count += 1
    
    print("-" * 60)
    
    # Save manifest
    extractor.save_manifest()
    
    # Print summary
    extractor.print_summary()
    
    print(f"Extraction complete: {extracted_count}/{len(figures_to_extract)} figures")
    if extracted_count == len(figures_to_extract):
        print("✓ All figures extracted successfully!")
    else:
        print(f"⚠ {len(figures_to_extract) - extracted_count} figures failed")

if __name__ == "__main__":
    main()
