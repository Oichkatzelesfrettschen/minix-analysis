#!/usr/bin/env python3
"""
Test runner for OS Analysis Toolkit
Provides organized test execution with proper reporting
"""

import sys
import argparse
import subprocess
from pathlib import Path
from typing import List, Optional


class TestRunner:
    """Organize and run different test suites"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results = {}

    def run_command(self, cmd: List[str], description: str) -> bool:
        """Run a test command and capture results"""
        print(f"\n{'='*60}")
        print(f"Running: {description}")
        print(f"{'='*60}")

        if self.verbose:
            print(f"Command: {' '.join(cmd)}")

        result = subprocess.run(cmd, capture_output=False, text=True)
        success = result.returncode == 0

        self.results[description] = success
        return success

    def run_unit_tests(self) -> bool:
        """Run unit tests"""
        return self.run_command(
            ["pytest", "-m", "unit", "--tb=short"],
            "Unit Tests"
        )

    def run_integration_tests(self) -> bool:
        """Run integration tests"""
        return self.run_command(
            ["pytest", "-m", "integration", "--tb=short"],
            "Integration Tests"
        )

    def run_property_tests(self) -> bool:
        """Run property-based tests"""
        return self.run_command(
            ["pytest", "-m", "property", "--tb=short"],
            "Property-Based Tests"
        )

    def run_performance_tests(self) -> bool:
        """Run performance benchmarks"""
        return self.run_command(
            ["pytest", "-m", "benchmark", "--benchmark-only"],
            "Performance Benchmarks"
        )

    def run_stress_tests(self) -> bool:
        """Run stress tests"""
        return self.run_command(
            ["pytest", "-m", "stress", "-v"],
            "Stress Tests"
        )

    def run_all_tests(self) -> bool:
        """Run complete test suite"""
        return self.run_command(
            ["pytest", "--cov=src/os_analysis_toolkit", "--cov-report=term"],
            "Complete Test Suite"
        )

    def run_specific_test(self, test_path: str) -> bool:
        """Run a specific test file or test"""
        return self.run_command(
            ["pytest", test_path, "-v"],
            f"Specific Test: {test_path}"
        )

    def run_with_coverage(self) -> bool:
        """Run tests with coverage report"""
        success = self.run_command(
            [
                "pytest",
                "--cov=src/os_analysis_toolkit",
                "--cov-report=term-missing",
                "--cov-report=html",
                "--cov-branch"
            ],
            "Tests with Coverage"
        )

        if success:
            print("\n📊 Coverage report generated in htmlcov/index.html")

        return success

    def print_summary(self):
        """Print test summary"""
        print(f"\n{'='*60}")
        print("TEST SUMMARY")
        print(f"{'='*60}")

        passed = sum(1 for v in self.results.values() if v)
        failed = sum(1 for v in self.results.values() if not v)

        for test, success in self.results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status}: {test}")

        print(f"\nTotal: {passed} passed, {failed} failed")

        if failed == 0:
            print("\n🎉 All tests passed!")
            return 0
        else:
            print(f"\n⚠️ {failed} test suite(s) failed")
            return 1


def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(
        description="Run tests for OS Analysis Toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py --unit          # Run unit tests only
  python run_tests.py --all           # Run all tests
  python run_tests.py --coverage      # Run with coverage report
  python run_tests.py --benchmark     # Run performance benchmarks
  python run_tests.py --quick         # Run quick tests (exclude slow)
        """
    )

    parser.add_argument("--unit", action="store_true",
                       help="Run unit tests")
    parser.add_argument("--integration", action="store_true",
                       help="Run integration tests")
    parser.add_argument("--property", action="store_true",
                       help="Run property-based tests")
    parser.add_argument("--benchmark", action="store_true",
                       help="Run performance benchmarks")
    parser.add_argument("--stress", action="store_true",
                       help="Run stress tests")
    parser.add_argument("--all", action="store_true",
                       help="Run all tests")
    parser.add_argument("--coverage", action="store_true",
                       help="Run with coverage report")
    parser.add_argument("--quick", action="store_true",
                       help="Run quick tests only (exclude slow)")
    parser.add_argument("--test", type=str,
                       help="Run specific test file or test")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")

    args = parser.parse_args()

    # Default to running all if no specific option
    if not any([args.unit, args.integration, args.property, args.benchmark,
                args.stress, args.all, args.coverage, args.quick, args.test]):
        args.all = True

    runner = TestRunner(verbose=args.verbose)

    # Run requested test suites
    if args.test:
        runner.run_specific_test(args.test)
    else:
        if args.unit:
            runner.run_unit_tests()
        if args.integration:
            runner.run_integration_tests()
        if args.property:
            runner.run_property_tests()
        if args.benchmark:
            runner.run_performance_tests()
        if args.stress:
            runner.run_stress_tests()
        if args.all:
            runner.run_all_tests()
        if args.coverage:
            runner.run_with_coverage()
        if args.quick:
            runner.run_command(
                ["pytest", "-m", "not slow", "--tb=short"],
                "Quick Tests (excluding slow)"
            )

    # Print summary and return exit code
    exit_code = runner.print_summary()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()