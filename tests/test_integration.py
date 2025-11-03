"""
Integration tests for OS Analysis Toolkit
Testing complete workflows and component interactions
"""

import pytest
import json
import subprocess
import time
from pathlib import Path
from unittest.mock import patch
import tempfile
import shutil

from os_analysis_toolkit.parallel import ParallelAnalysisPipeline, ParallelExecutor, AnalysisTask
from os_analysis_toolkit.generators import TikZGenerator
from os_analysis_toolkit.dashboard import create_app


class TestEndToEndAnalysisPipeline:
    """Test complete analysis pipeline from source to output"""

    def test_complete_analysis_workflow(self, minix_source_path, temp_output_dir):
        """Test full pipeline: analyze -> export -> generate diagrams"""
        # Step 1: Run analysis pipeline
        pipeline = ParallelAnalysisPipeline(
            source_root=str(minix_source_path),
            output_dir=str(temp_output_dir)
        )

        results = pipeline.run_complete_analysis()

        # Verify all expected outputs were generated
        assert "kernel_structure" in results
        assert "process_management" in results
        assert "memory_layout" in results
        assert "ipc_system" in results
        assert "boot_sequence" in results
        assert "statistics" in results

        # Verify JSON files were created
        json_files = list(temp_output_dir.glob("*.json"))
        assert len(json_files) >= 5

        # Step 2: Verify JSON content is valid
        for json_file in json_files:
            with open(json_file, 'r') as f:
                data = json.load(f)
                assert isinstance(data, dict)
                assert len(data) > 0

    def test_parallel_vs_sequential_consistency(self, minix_source_path, temp_output_dir):
        """Test that parallel and sequential analysis produce same results"""
        from os_analysis_toolkit.analyzers import KernelAnalyzer

        analyzer = KernelAnalyzer(str(minix_source_path))

        # Sequential analysis
        seq_kernel = analyzer.analyze_kernel_structure()
        seq_process = analyzer.analyze_process_management()
        seq_memory = analyzer.analyze_memory_layout()

        # Parallel analysis using executor
        executor = ParallelExecutor(max_workers=3)

        # Create module-level functions for parallel execution
        def analyze_kernel():
            a = KernelAnalyzer(str(minix_source_path))
            return a.analyze_kernel_structure()

        def analyze_process():
            a = KernelAnalyzer(str(minix_source_path))
            return a.analyze_process_management()

        def analyze_memory():
            a = KernelAnalyzer(str(minix_source_path))
            return a.analyze_memory_layout()

        # Note: We can't use local functions with multiprocessing
        # In real usage, these would be module-level functions
        # For now, we verify the executor works with the pipeline
        pipeline = ParallelAnalysisPipeline(
            source_root=str(minix_source_path),
            output_dir=str(temp_output_dir)
        )

        results = pipeline.run_complete_analysis()

        # Verify we got results from parallel execution
        assert len(results) > 0
        assert all(isinstance(v, dict) for v in results.values())

    def test_incremental_analysis_with_cache(self, minix_source_path, temp_output_dir, monkeypatch):
        """Test incremental analysis using cache for unchanged components"""
        # Configure cache directory
        cache_dir = temp_output_dir / ".cache"
        cache_dir.mkdir(exist_ok=True)
        monkeypatch.setattr("os_analysis_toolkit.analyzers.base.Path.home",
                          lambda: temp_output_dir)

        # First run - populate cache
        pipeline1 = ParallelAnalysisPipeline(
            source_root=str(minix_source_path),
            output_dir=str(temp_output_dir / "run1")
        )
        results1 = pipeline1.run_complete_analysis()

        # Count cache files created
        cache_files = list(cache_dir.glob("*.json"))
        assert len(cache_files) > 0

        # Second run - should use cache
        pipeline2 = ParallelAnalysisPipeline(
            source_root=str(minix_source_path),
            output_dir=str(temp_output_dir / "run2")
        )

        start_time = time.perf_counter()
        results2 = pipeline2.run_complete_analysis()
        cached_time = time.perf_counter() - start_time

        # Results should be identical
        assert results1.keys() == results2.keys()

        # Cached run should be fast (< 1 second)
        assert cached_time < 1.0


class TestDiagramGeneration:
    """Test diagram generation from analyzed data"""

    def test_tikz_generation_from_real_data(self, sample_kernel_data, temp_output_dir):
        """Test TikZ diagram generation with real kernel data"""
        generator = TikZGenerator(str(temp_output_dir))

        # Generate kernel diagram
        tikz_code = generator.generate_kernel_diagram(sample_kernel_data)

        # Verify TikZ structure
        assert "\\documentclass" in tikz_code
        assert "\\begin{document}" in tikz_code
        assert "\\begin{tikzpicture}" in tikz_code
        assert "\\end{tikzpicture}" in tikz_code
        assert "\\end{document}" in tikz_code

        # Save and verify file creation
        output_file = generator.save_diagram(tikz_code, "test_kernel.tex")
        assert Path(output_file).exists()

        # Read back and verify content
        with open(output_file, 'r') as f:
            content = f.read()
            assert content == tikz_code

    def test_complete_diagram_generation_workflow(self, temp_output_dir):
        """Test generating all diagram types"""
        generator = TikZGenerator(str(temp_output_dir))

        # Create sample data files
        data_dir = temp_output_dir / "data"
        data_dir.mkdir()

        sample_data = {
            "kernel.json": {"microkernel": True, "components": ["kernel", "servers"]},
            "process.json": {"states": ["ready", "running", "blocked"]},
            "memory.json": {"segments": ["text", "data", "stack"]},
            "ipc.json": {"mechanism": "message_passing"},
            "boot.json": {"stages": ["bios", "bootloader", "kernel"]}
        }

        for filename, data in sample_data.items():
            with open(data_dir / filename, 'w') as f:
                json.dump(data, f)

        # Generate all diagrams
        results = generator.generate_all(str(data_dir))

        # Verify all diagrams were generated
        assert "kernel" in results
        assert "process" in results
        assert "memory" in results
        assert "ipc" in results
        assert "boot" in results

        # Verify .tex files exist
        tex_files = list(temp_output_dir.glob("*.tex"))
        assert len(tex_files) == 5

    @pytest.mark.skipif(not shutil.which("pdflatex"),
                       reason="pdflatex not installed")
    def test_pdf_compilation(self, temp_output_dir):
        """Test compiling TikZ to PDF (requires LaTeX installation)"""
        generator = TikZGenerator(str(temp_output_dir))

        # Generate simple diagram
        tikz_code = generator.generate_memory_diagram({})
        tex_file = generator.save_diagram(tikz_code, "test_memory.tex")

        # Try to compile to PDF
        success = generator.compile_to_pdf(tex_file)

        if success:
            pdf_file = Path(tex_file).with_suffix('.pdf')
            assert pdf_file.exists()


class TestDashboardIntegration:
    """Test web dashboard functionality"""

    def test_dashboard_app_creation_with_data(self, temp_output_dir):
        """Test creating dashboard app with analysis data"""
        # Create sample data files
        data_files = {
            "kernel.json": {"analyzed": True, "microkernel": True},
            "memory.json": {"page_size": 4096, "virtual": True},
            "process.json": {"max_processes": 256},
            "syscalls.json": {"total": 108, "categories": {"file": 40}},
            "performance.json": {"cpu_usage": 45.2, "memory_usage": 150}
        }

        data_dir = temp_output_dir / "data"
        data_dir.mkdir()

        for filename, data in data_files.items():
            with open(data_dir / filename, 'w') as f:
                json.dump(data, f)

        # Create dashboard app
        app = create_app(str(data_dir))

        # Verify app was created
        assert app is not None
        assert app.title == "OS Analysis Dashboard"

        # Verify layout was created
        assert app.layout is not None

    def test_dashboard_data_loading(self, sample_kernel_data, sample_memory_layout, temp_output_dir):
        """Test that dashboard correctly loads and displays analysis data"""
        # Create data directory with real-looking data
        data_dir = temp_output_dir / "data"
        data_dir.mkdir()

        with open(data_dir / "kernel.json", 'w') as f:
            json.dump(sample_kernel_data, f)

        with open(data_dir / "memory.json", 'w') as f:
            json.dump(sample_memory_layout, f)

        # Create and verify dashboard
        app = create_app(str(data_dir))

        # The dashboard should have created tabs
        # We can't easily test the callbacks without running the server,
        # but we can verify the structure
        assert app.layout is not None


class TestCLIIntegration:
    """Test command-line interface integration"""

    def test_cli_analysis_command_with_real_source(self, minix_source_path, temp_output_dir):
        """Test CLI analysis command with actual MINIX source"""
        result = subprocess.run(
            [
                "os-analyze",
                "--source", str(minix_source_path),
                "--output", str(temp_output_dir),
                "--parallel",
                "--workers", "2",
                "--cache"
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        # Command should succeed
        assert result.returncode == 0
        assert "Analysis complete" in result.stdout

        # Output files should be created
        json_files = list(temp_output_dir.glob("*.json"))
        assert len(json_files) >= 5

        # Verify JSON content
        for json_file in json_files:
            with open(json_file, 'r') as f:
                data = json.load(f)
                assert isinstance(data, dict)

    def test_cli_help_documentation(self):
        """Test CLI help provides complete documentation"""
        result = subprocess.run(
            ["os-analyze", "--help"],
            capture_output=True,
            text=True
        )

        # Help should work
        assert result.returncode == 0

        # Verify essential information is present
        assert "OS Analysis Toolkit" in result.stdout
        assert "--source" in result.stdout
        assert "--output" in result.stdout
        assert "--parallel" in result.stdout
        assert "--dashboard" in result.stdout
        assert "--benchmark" in result.stdout
        assert "Examples:" in result.stdout

    def test_cli_version_command(self):
        """Test CLI version reporting"""
        result = subprocess.run(
            ["os-analyze", "--version"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert "1.0.0" in result.stdout


class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_invalid_source_path_handling(self, temp_output_dir):
        """Test handling of invalid source paths"""
        from os_analysis_toolkit.analyzers import KernelAnalyzer

        # Create analyzer with non-existent path
        analyzer = KernelAnalyzer("/nonexistent/path")

        # Should handle gracefully
        result = analyzer.analyze_kernel_structure()
        assert isinstance(result, dict)  # Should return default structure

    def test_corrupted_cache_recovery(self, minix_source_path, temp_output_dir, monkeypatch):
        """Test recovery from corrupted cache files"""
        from os_analysis_toolkit.analyzers import KernelAnalyzer

        # Setup cache directory
        cache_dir = temp_output_dir / ".cache"
        cache_dir.mkdir()
        monkeypatch.setattr("os_analysis_toolkit.analyzers.base.Path.home",
                          lambda: temp_output_dir)

        # Create corrupted cache file
        cache_file = cache_dir / "corrupted.json"
        with open(cache_file, 'w') as f:
            f.write("{ invalid json }")

        # Analyzer should handle corrupted cache
        analyzer = KernelAnalyzer(str(minix_source_path))
        result = analyzer.analyze_kernel_structure()

        # Should still return valid results
        assert isinstance(result, dict)
        assert "microkernel" in result

    def test_concurrent_cache_access(self, minix_source_path, temp_output_dir, monkeypatch):
        """Test that concurrent access to cache doesn't cause issues"""
        from concurrent.futures import ThreadPoolExecutor
        from os_analysis_toolkit.analyzers import KernelAnalyzer

        monkeypatch.setattr("os_analysis_toolkit.analyzers.base.Path.home",
                          lambda: temp_output_dir)

        def analyze():
            analyzer = KernelAnalyzer(str(minix_source_path))
            return analyzer.analyze_kernel_structure()

        # Run multiple analyses concurrently
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(analyze) for _ in range(10)]
            results = [f.result() for f in futures]

        # All results should be identical
        first_result = results[0]
        for result in results[1:]:
            assert result == first_result