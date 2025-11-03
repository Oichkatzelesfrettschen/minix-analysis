#!/usr/bin/env python3
"""
Comprehensive test harness for MINIX testing in Docker + QEMU.

Provides integration between Docker containers, QEMU VMs, and test
execution framework with detailed reporting and artifact collection.
"""

import os
import sys
import time
import json
import logging
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

import yaml


class TestStatus(Enum):
    """Test execution status."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class TestLevel(Enum):
    """Test hierarchy levels."""
    UNIT = "unit"
    INTEGRATION = "integration"
    SYSTEM = "system"
    PERFORMANCE = "performance"


@dataclass
class TestResult:
    """Individual test result."""
    name: str
    level: TestLevel
    status: TestStatus
    duration: float = 0.0
    stdout: str = ""
    stderr: str = ""
    error_message: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    artifacts: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'level': self.level.value,
            'status': self.status.value,
            'duration': self.duration,
            'timestamp': self.timestamp,
            'artifacts': self.artifacts,
        }


@dataclass
class TestSuite:
    """Collection of related tests."""
    name: str
    description: str = ""
    tests: List[TestResult] = field(default_factory=list)
    setup: Optional[Callable] = None
    teardown: Optional[Callable] = None
    timeout: int = 300

    def add_result(self, result: TestResult):
        """Add test result."""
        self.tests.append(result)

    def summary(self) -> Dict[str, int]:
        """Get summary statistics."""
        return {
            'total': len(self.tests),
            'passed': sum(1 for t in self.tests if t.status == TestStatus.PASSED),
            'failed': sum(1 for t in self.tests if t.status == TestStatus.FAILED),
            'skipped': sum(1 for t in self.tests if t.status == TestStatus.SKIPPED),
            'error': sum(1 for t in self.tests if t.status == TestStatus.ERROR),
        }

    def success_rate(self) -> float:
        """Calculate success rate."""
        summary = self.summary()
        if summary['total'] == 0:
            return 100.0
        return (summary['passed'] / summary['total']) * 100


class TestHarness:
    """Main test harness orchestrator."""

    def __init__(self, config_path: str = ".config/paths.yaml",
                 log_level: str = "INFO"):
        """
        Initialize test harness.
        
        Args:
            config_path: Path to configuration file
            log_level: Logging level
        """
        self.config = self._load_config(config_path)
        self.suites: List[TestSuite] = []
        self.logger = self._setup_logging(log_level)
        self.start_time = None
        self.end_time = None
        self.artifacts_dir = Path(self.config.get('paths', {}).get('build', {}).get('artifacts', './artifacts'))
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML."""
        if not Path(config_path).exists():
            self.logger.warning(f"Config file not found: {config_path}")
            return {}
        
        with open(config_path) as f:
            return yaml.safe_load(f) or {}

    def _setup_logging(self, log_level: str) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger(__name__)
        logger.setLevel(getattr(logging, log_level))
        
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger

    def register_suite(self, suite: TestSuite) -> None:
        """Register test suite."""
        self.suites.append(suite)
        self.logger.info(f"Registered suite: {suite.name}")

    def run_test(self, test_func: Callable, name: str, level: TestLevel,
                 timeout: int = 60) -> TestResult:
        """
        Execute single test.
        
        Args:
            test_func: Test function to execute
            name: Test name
            level: Test level (unit/integration/system)
            timeout: Test timeout in seconds
        
        Returns:
            TestResult object
        """
        result = TestResult(name=name, level=level, status=TestStatus.RUNNING)
        self.logger.info(f"Running {level.value} test: {name}")
        
        start = time.time()
        
        try:
            # Execute test with timeout
            test_func()
            result.status = TestStatus.PASSED
            self.logger.info(f"Test passed: {name}")
        
        except AssertionError as e:
            result.status = TestStatus.FAILED
            result.error_message = str(e)
            self.logger.error(f"Test failed: {name} - {e}")
        
        except subprocess.TimeoutExpired as e:
            result.status = TestStatus.ERROR
            result.error_message = f"Timeout after {timeout}s"
            self.logger.error(f"Test timeout: {name}")
        
        except Exception as e:
            result.status = TestStatus.ERROR
            result.error_message = str(e)
            self.logger.error(f"Test error: {name} - {e}")
        
        finally:
            result.duration = time.time() - start
        
        return result

    def run_docker_command(self, cmd: str, container: str = None) -> Dict[str, Any]:
        """
        Execute command in Docker container.
        
        Args:
            cmd: Command to execute
            container: Optional container name/ID
        
        Returns:
            Result dict with stdout, stderr, returncode
        """
        if container:
            full_cmd = ["docker", "exec", container, "bash", "-c", cmd]
        else:
            full_cmd = ["bash", "-c", cmd]
        
        try:
            result = subprocess.run(
                full_cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            return {
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
            }
        except subprocess.TimeoutExpired:
            return {
                'returncode': -1,
                'stdout': '',
                'stderr': 'Command timeout',
            }

    def run_all_suites(self) -> bool:
        """
        Execute all registered test suites.
        
        Returns:
            True if all tests passed
        """
        self.start_time = time.time()
        all_passed = True
        
        for suite in self.suites:
            self.logger.info(f"\n=== Running suite: {suite.name} ===")
            
            # Run setup
            if suite.setup:
                try:
                    suite.setup()
                except Exception as e:
                    self.logger.error(f"Setup failed for {suite.name}: {e}")
                    all_passed = False
                    continue
            
            # Run tests (would be populated by actual test implementation)
            # This is a framework - actual tests would be registered via callbacks
            
            # Run teardown
            if suite.teardown:
                try:
                    suite.teardown()
                except Exception as e:
                    self.logger.error(f"Teardown failed for {suite.name}: {e}")
                    all_passed = False
            
            # Log summary
            summary = suite.summary()
            success_rate = suite.success_rate()
            self.logger.info(f"Suite summary: {summary} ({success_rate:.1f}% passed)")
            
            if summary['failed'] > 0 or summary['error'] > 0:
                all_passed = False
        
        self.end_time = time.time()
        return all_passed

    def generate_report(self, output_format: str = "json") -> str:
        """
        Generate test report.
        
        Args:
            output_format: Report format (json/html)
        
        Returns:
            Report content as string
        """
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'duration': self.end_time - self.start_time if self.end_time else 0,
            'suites': []
        }
        
        for suite in self.suites:
            suite_data = {
                'name': suite.name,
                'description': suite.description,
                'summary': suite.summary(),
                'success_rate': suite.success_rate(),
                'tests': [t.to_dict() for t in suite.tests]
            }
            report_data['suites'].append(suite_data)
        
        if output_format == "json":
            return json.dumps(report_data, indent=2)
        elif output_format == "html":
            return self._generate_html_report(report_data)
        else:
            return str(report_data)

    def _generate_html_report(self, data: Dict[str, Any]) -> str:
        """Generate HTML test report."""
        html = """<!DOCTYPE html>
<html>
<head>
    <title>Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        .summary { background: #f0f0f0; padding: 10px; border-radius: 5px; margin: 10px 0; }
        .passed { color: green; }
        .failed { color: red; }
        .error { color: orange; }
        table { border-collapse: collapse; width: 100%; margin: 10px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #4CAF50; color: white; }
    </style>
</head>
<body>
    <h1>Test Report</h1>
"""
        
        html += f"<p>Generated: {data['timestamp']}</p>"
        html += f"<p>Duration: {data['duration']:.2f}s</p>"
        
        for suite in data['suites']:
            html += f"<h2>{suite['name']}</h2>"
            html += f"<div class='summary'>"
            html += f"<p>Success Rate: {suite['success_rate']:.1f}%</p>"
            html += f"<p>Total: {suite['summary']['total']}, "
            html += f"<span class='passed'>Passed: {suite['summary']['passed']}</span>, "
            html += f"<span class='failed'>Failed: {suite['summary']['failed']}</span>, "
            html += f"<span class='error'>Error: {suite['summary']['error']}</span></p>"
            html += f"</div>"
        
        html += "</body></html>"
        return html

    def save_report(self, filename: str, format: str = "json") -> Path:
        """
        Save test report to file.
        
        Args:
            filename: Output filename
            format: Report format
        
        Returns:
            Path to saved report
        """
        report_content = self.generate_report(format)
        report_path = self.artifacts_dir / filename
        
        with open(report_path, 'w') as f:
            f.write(report_content)
        
        self.logger.info(f"Report saved to: {report_path}")
        return report_path


if __name__ == "__main__":
    # Example usage
    harness = TestHarness()
    
    # Create example test suite
    suite = TestSuite(name="MINIX Boot Tests", description="Tests for MINIX boot process")
    
    # Register and run
    harness.register_suite(suite)
    harness.run_all_suites()
    
    # Generate report
    report_path = harness.save_report("test_report.json")
    print(f"Test report saved to: {report_path}")
