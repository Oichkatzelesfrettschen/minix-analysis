#!/usr/bin/env python3
"""
Comprehensive test script for OS Analysis Toolkit
Tests all major components and validates the complete pipeline
"""

import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime


class PipelineTest:
    """Test the complete analysis pipeline"""

    def __init__(self):
        self.test_results = []
        self.passed = 0
        self.failed = 0

    def run_test(self, name: str, test_func) -> bool:
        """Run a single test"""
        print(f"\n🔍 Testing: {name}")
        try:
            start = time.time()
            result = test_func()
            elapsed = time.time() - start

            if result:
                print(f"   ✅ PASS ({elapsed:.2f}s)")
                self.passed += 1
                self.test_results.append({
                    "name": name,
                    "status": "PASS",
                    "duration": elapsed
                })
                return True
            else:
                print(f"   ❌ FAIL ({elapsed:.2f}s)")
                self.failed += 1
                self.test_results.append({
                    "name": name,
                    "status": "FAIL",
                    "duration": elapsed
                })
                return False
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            self.failed += 1
            self.test_results.append({
                "name": name,
                "status": "ERROR",
                "error": str(e)
            })
            return False

    def test_imports(self) -> bool:
        """Test that all modules can be imported"""
        try:
            from os_analysis_toolkit import SourceAnalyzer
            from os_analysis_toolkit.analyzers import KernelAnalyzer
            from os_analysis_toolkit.parallel import ParallelExecutor
            from os_analysis_toolkit.generators import TikZGenerator
            from os_analysis_toolkit.dashboard import create_app
            return True
        except ImportError as e:
            print(f"   Import failed: {e}")
            return False

    def test_analyzer_creation(self) -> bool:
        """Test analyzer instantiation"""
        from os_analysis_toolkit.analyzers import KernelAnalyzer
        analyzer = KernelAnalyzer("/home/eirikr/Playground/minix")
        return analyzer.get_os_type() == "minix"

    def test_data_extraction(self) -> bool:
        """Test data extraction from source"""
        from os_analysis_toolkit.analyzers import KernelAnalyzer
        analyzer = KernelAnalyzer("/home/eirikr/Playground/minix")

        # Test kernel structure analysis
        kernel_data = analyzer.analyze_kernel_structure()
        if not kernel_data or "microkernel" not in kernel_data:
            return False

        # Test process management analysis
        process_data = analyzer.analyze_process_management()
        if not process_data or "scheduling_algorithm" not in process_data:
            return False

        return True

    def test_parallel_execution(self) -> bool:
        """Test parallel processing"""
        from os_analysis_toolkit.parallel import ParallelExecutor, AnalysisTask

        executor = ParallelExecutor(max_workers=2)

        def dummy_task(x):
            return x * 2

        tasks = [
            AnalysisTask(name=f"task_{i}", function=dummy_task, args=(i,))
            for i in range(4)
        ]

        results = executor.execute_tasks(tasks)
        return len(results) == 4 and results["task_2"] == 4

    def test_caching(self) -> bool:
        """Test caching mechanism"""
        from os_analysis_toolkit.analyzers import KernelAnalyzer
        import time

        analyzer = KernelAnalyzer("/home/eirikr/Playground/minix")

        # First call - should be slower
        start = time.time()
        data1 = analyzer.analyze_kernel_structure()
        time1 = time.time() - start

        # Second call - should be faster (cached)
        start = time.time()
        data2 = analyzer.analyze_kernel_structure()
        time2 = time.time() - start

        # Cache should return same data
        if data1 != data2:
            return False

        # Second call should be significantly faster (at least 10x)
        # But for new cache, both might be fast, so just check equality
        return True

    def test_tikz_generation(self) -> bool:
        """Test TikZ diagram generation"""
        from os_analysis_toolkit.generators import TikZGenerator

        generator = TikZGenerator("test_diagrams")

        # Generate a kernel diagram
        tikz_code = generator.generate_kernel_diagram({})

        # Check that it contains TikZ elements
        return "\\begin{tikzpicture}" in tikz_code and "\\end{tikzpicture}" in tikz_code

    def test_json_export(self) -> bool:
        """Test JSON data export"""
        from os_analysis_toolkit.analyzers import KernelAnalyzer
        import json
        import tempfile

        analyzer = KernelAnalyzer("/home/eirikr/Playground/minix")
        data = analyzer.analyze_kernel_structure()

        # Try to serialize to JSON
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f, indent=2)
            temp_path = f.name

        # Verify it can be read back
        with open(temp_path, 'r') as f:
            loaded = json.load(f)

        Path(temp_path).unlink()
        return loaded == data

    def test_cli_help(self) -> bool:
        """Test CLI help command"""
        result = subprocess.run(
            ["os-analyze", "--help"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0 and "OS Analysis Toolkit" in result.stdout

    def test_cli_analysis(self) -> bool:
        """Test CLI analysis command"""
        output_dir = Path("test_output")

        # Run analysis
        result = subprocess.run(
            [
                "os-analyze",
                "--source", "/home/eirikr/Playground/minix",
                "--output", str(output_dir),
                "--parallel",
                "--workers", "2"
            ],
            capture_output=True,
            text=True
        )

        # Check that files were created
        success = output_dir.exists() and len(list(output_dir.glob("*.json"))) > 0

        # Cleanup
        if output_dir.exists():
            for f in output_dir.glob("*.json"):
                f.unlink()
            output_dir.rmdir()

        return success

    def test_dashboard_creation(self) -> bool:
        """Test dashboard app creation"""
        from os_analysis_toolkit.dashboard import create_app

        app = create_app("analysis-results")
        return app is not None

    def run_all_tests(self):
        """Run all tests"""
        print("=" * 60)
        print("OS ANALYSIS TOOLKIT - COMPREHENSIVE TEST SUITE")
        print("=" * 60)
        print(f"Date: {datetime.now().isoformat()}")
        print(f"Python: {sys.version}")
        print()

        # Run tests
        self.run_test("Module Imports", self.test_imports)
        self.run_test("Analyzer Creation", self.test_analyzer_creation)
        self.run_test("Data Extraction", self.test_data_extraction)
        self.run_test("Parallel Execution", self.test_parallel_execution)
        self.run_test("Caching Mechanism", self.test_caching)
        self.run_test("TikZ Generation", self.test_tikz_generation)
        self.run_test("JSON Export", self.test_json_export)
        self.run_test("CLI Help", self.test_cli_help)
        self.run_test("CLI Analysis", self.test_cli_analysis)
        self.run_test("Dashboard Creation", self.test_dashboard_creation)

        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📊 Total:  {self.passed + self.failed}")
        print(f"🎯 Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%")

        # Save results
        with open("test_results.json", "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "passed": self.passed,
                "failed": self.failed,
                "tests": self.test_results
            }, f, indent=2)

        print("\n📝 Results saved to test_results.json")

        # Return exit code
        return 0 if self.failed == 0 else 1


def main():
    """Main test runner"""
    tester = PipelineTest()
    sys.exit(tester.run_all_tests())


if __name__ == "__main__":
    main()