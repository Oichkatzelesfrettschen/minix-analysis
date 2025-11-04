"""
Unit tests for TeXplosion validation script

Tests the validation functionality for the TeXplosion pipeline setup.
"""

import pytest
import sys
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

try:
    from validate_texplosion_setup import (
        Colors,
        check_command,
        check_file_exists,
        check_directory_exists,
        validate_python_packages,
        validate_workflow_yaml
    )
    SCRIPT_AVAILABLE = True
except ImportError:
    SCRIPT_AVAILABLE = False
    pytestmark = pytest.mark.skip("validate-texplosion-setup script not importable")


@pytest.mark.unit
class TestValidationScript:
    """Test validation script functions"""
    
    def test_colors_defined(self):
        """Test that color codes are defined"""
        if not SCRIPT_AVAILABLE:
            pytest.skip("Script not available")
        
        assert hasattr(Colors, 'GREEN')
        assert hasattr(Colors, 'RED')
        assert hasattr(Colors, 'YELLOW')
        assert hasattr(Colors, 'END')
    
    @patch('subprocess.run')
    def test_check_command_success(self, mock_run):
        """Test command check with successful command"""
        if not SCRIPT_AVAILABLE:
            pytest.skip("Script not available")
        
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Python 3.9.0"
        )
        
        status, message = check_command('python3', 'Python')
        assert status is True
        assert 'Python' in message or message == 'Python 3.9.0'
    
    @patch('subprocess.run')
    def test_check_command_failure(self, mock_run):
        """Test command check with failed command"""
        if not SCRIPT_AVAILABLE:
            pytest.skip("Script not available")
        
        mock_run.side_effect = FileNotFoundError()
        
        status, message = check_command('nonexistent', 'Test')
        assert status is False
        assert 'not found' in message.lower()
    
    def test_check_file_exists_true(self, tmp_path):
        """Test file existence check for existing file"""
        if not SCRIPT_AVAILABLE:
            pytest.skip("Script not available")
        
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        status, message = check_file_exists(str(test_file), "Test file")
        assert status is True
        assert 'Found' in message
    
    def test_check_file_exists_false(self, tmp_path):
        """Test file existence check for missing file"""
        if not SCRIPT_AVAILABLE:
            pytest.skip("Script not available")
        
        test_file = tmp_path / "missing.txt"
        
        status, message = check_file_exists(str(test_file), "Test file")
        assert status is False
        assert 'not found' in message.lower()
    
    def test_check_directory_exists_true(self, tmp_path):
        """Test directory existence check for existing directory"""
        if not SCRIPT_AVAILABLE:
            pytest.skip("Script not available")
        
        test_dir = tmp_path / "testdir"
        test_dir.mkdir()
        (test_dir / "file1.txt").write_text("content")
        
        status, message = check_directory_exists(str(test_dir), "Test dir")
        assert status is True
        assert 'Found' in message
    
    @patch('builtins.__import__')
    def test_validate_python_packages(self, mock_import):
        """Test Python package validation"""
        if not SCRIPT_AVAILABLE:
            pytest.skip("Script not available")
        
        # Mock successful import
        mock_import.return_value = Mock()
        
        results = validate_python_packages()
        assert isinstance(results, list)
        assert len(results) > 0
        
        for package, status, message, required in results:
            assert isinstance(package, str)
            assert isinstance(status, bool)
            assert isinstance(message, str)
            assert isinstance(required, bool)


@pytest.mark.unit
class TestWorkflowValidation:
    """Test workflow YAML validation"""
    
    def test_validate_workflow_missing_file(self):
        """Test validation with missing workflow file"""
        if not SCRIPT_AVAILABLE:
            pytest.skip("Script not available")
        
        # Temporarily change to a directory without workflows
        import os
        original_dir = os.getcwd()
        try:
            os.chdir('/tmp')
            status, message = validate_workflow_yaml()
            assert status is False
            assert 'not found' in message.lower()
        finally:
            os.chdir(original_dir)
    
    def test_validate_workflow_yaml_structure(self, tmp_path):
        """Test workflow YAML structure validation"""
        if not SCRIPT_AVAILABLE:
            pytest.skip("Script not available")
        
        # Create a valid workflow file
        workflow_dir = tmp_path / ".github" / "workflows"
        workflow_dir.mkdir(parents=True)
        workflow_file = workflow_dir / "texplosion-pages.yml"
        
        workflow_content = """
name: Test Workflow
on: push
jobs:
  generate-diagrams:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
  compile-latex:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
  build-pages:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
"""
        workflow_file.write_text(workflow_content)
        
        # Change to temp directory for test
        import os
        original_dir = os.getcwd()
        try:
            os.chdir(tmp_path)
            status, message = validate_workflow_yaml()
            assert status is True
            assert '3/3 jobs' in message or 'valid' in message.lower()
        finally:
            os.chdir(original_dir)


@pytest.mark.integration
class TestValidationScriptIntegration:
    """Integration tests for the full validation script"""
    
    def test_script_runs_without_error(self):
        """Test that validation script can run without crashing"""
        # Try to run the actual script
        try:
            result = subprocess.run(
                [sys.executable, 'scripts/validate-texplosion-setup.py'],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=Path(__file__).parent.parent
            )
            # Script should exit with 0 or 1, not crash
            assert result.returncode in [0, 1]
        except FileNotFoundError:
            pytest.skip("Validation script not found")
        except subprocess.TimeoutExpired:
            pytest.fail("Validation script timed out")


@pytest.mark.unit
class TestBuildValidation:
    """Test build validation script"""
    
    def test_build_validation_script_exists(self):
        """Test that build validation script exists"""
        script_path = Path(__file__).parent.parent / 'scripts' / 'validate-build.py'
        assert script_path.exists(), "Build validation script should exist"
    
    def test_build_validation_executable(self):
        """Test that build validation script is executable"""
        script_path = Path(__file__).parent.parent / 'scripts' / 'validate-build.py'
        if script_path.exists():
            assert script_path.stat().st_mode & 0o111, "Script should be executable"
