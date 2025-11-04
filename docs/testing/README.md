# Testing Framework - Complete Guide

**Last Updated:** 2025-11-04  
**Status:** Production Ready  
**Coverage Target:** 80%+

---

## Overview

The MINIX Analysis project uses a comprehensive testing framework to ensure code quality, reliability, and maintainability. This guide covers all aspects of testing in the project.

---

## Table of Contents

1. [Testing Philosophy](#testing-philosophy)
2. [Test Infrastructure](#test-infrastructure)
3. [Running Tests](#running-tests)
4. [Writing Tests](#writing-tests)
5. [Test Categories](#test-categories)
6. [Coverage Requirements](#coverage-requirements)
7. [CI/CD Integration](#cicd-integration)
8. [Troubleshooting](#troubleshooting)

---

## Testing Philosophy

### Principles

1. **Test Early, Test Often** - Write tests alongside code
2. **Comprehensive Coverage** - Aim for 80%+ code coverage
3. **Fast Feedback** - Unit tests should run in seconds
4. **Isolation** - Tests should be independent
5. **Clarity** - Tests serve as documentation

### Test Pyramid

```
        /\
       /  \      E2E Tests (Few)
      /____\
     /      \    Integration Tests (Some)
    /________\
   /          \  Unit Tests (Many)
  /__________  \
```

---

## Test Infrastructure

### Framework: pytest

**Why pytest?**
- Simple and pythonic syntax
- Powerful fixtures
- Excellent plugin ecosystem
- Great CI/CD integration

### Configuration

**File:** `pytest.ini`

```ini
[pytest]
python_files = test_*.py
python_classes = Test*
python_functions = test_*
testpaths = tests
```

**Key settings:**
- Test discovery patterns
- Coverage configuration
- Custom markers
- Output options

### Directory Structure

```
tests/
├── conftest.py              # Shared fixtures
├── test_*.py                # Unit tests
├── test_integration.py      # Integration tests
├── test_performance.py      # Performance tests
├── test_property_based.py   # Property-based tests
└── modules/                 # Module-specific tests
    ├── test_cpu_pipeline.py
    └── test_mcp_server.py
```

---

## Running Tests

### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_analyzers.py

# Run specific test
pytest tests/test_analyzers.py::test_source_analyzer_basic
```

### Test Categories

Use markers to run specific test categories:

```bash
# Unit tests only (fast)
pytest -m unit

# Integration tests
pytest -m integration

# Performance benchmarks
pytest -m benchmark

# All except slow tests
pytest -m "not slow"

# Property-based tests
pytest -m property
```

### Verbose Output

```bash
# Detailed output
pytest -v

# Show print statements
pytest -s

# Show local variables on failure
pytest -l

# Stop on first failure
pytest -x
```

### Parallel Execution

```bash
# Run tests in parallel (4 workers)
pytest -n 4

# Auto-detect CPU count
pytest -n auto
```

---

## Writing Tests

### Basic Test Structure

```python
import pytest
from mymodule import my_function

def test_my_function_basic():
    """Test basic functionality"""
    result = my_function(input_data)
    assert result == expected_output

def test_my_function_edge_case():
    """Test edge case handling"""
    with pytest.raises(ValueError):
        my_function(invalid_input)
```

### Using Fixtures

```python
@pytest.fixture
def sample_data():
    """Provide sample data for tests"""
    return {
        'key1': 'value1',
        'key2': 'value2'
    }

def test_with_fixture(sample_data):
    """Test using fixture"""
    assert 'key1' in sample_data
```

### Parametrized Tests

```python
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_double(input, expected):
    """Test with multiple inputs"""
    assert double(input) == expected
```

### Test Markers

```python
@pytest.mark.unit
def test_unit_example():
    """Unit test"""
    pass

@pytest.mark.integration
def test_integration_example():
    """Integration test"""
    pass

@pytest.mark.slow
def test_slow_operation():
    """Test that takes >10 seconds"""
    pass

@pytest.mark.requires_minix
def test_with_minix_source():
    """Test requiring MINIX source code"""
    pass
```

---

## Test Categories

### 1. Unit Tests

**Purpose:** Test individual functions/classes in isolation

**Characteristics:**
- Fast (milliseconds)
- No external dependencies
- Use mocks/stubs
- High volume

**Example:**
```python
@pytest.mark.unit
def test_parse_function():
    """Test C function parsing"""
    code = "void foo() { return; }"
    result = parse_c_function(code)
    assert result.name == "foo"
    assert result.return_type == "void"
```

### 2. Integration Tests

**Purpose:** Test component interactions

**Characteristics:**
- Medium speed (seconds)
- Multiple components
- Real dependencies
- Medium volume

**Example:**
```python
@pytest.mark.integration
def test_analysis_pipeline():
    """Test complete analysis pipeline"""
    analyzer = SourceAnalyzer()
    generator = TikZGenerator()
    
    data = analyzer.analyze("minix-source/")
    diagrams = generator.generate(data)
    
    assert len(diagrams) > 0
```

### 3. Performance Tests

**Purpose:** Benchmark performance

**Characteristics:**
- Timing-focused
- Use pytest-benchmark
- Track regressions
- Low volume

**Example:**
```python
@pytest.mark.benchmark
def test_analyzer_performance(benchmark):
    """Benchmark analyzer performance"""
    result = benchmark(analyze_file, "large_file.c")
    assert result is not None
```

### 4. Property-Based Tests

**Purpose:** Generate test cases automatically

**Characteristics:**
- Uses hypothesis library
- Finds edge cases
- High confidence
- Medium volume

**Example:**
```python
from hypothesis import given, strategies as st

@pytest.mark.property
@given(st.integers())
def test_double_property(n):
    """Property: doubling is commutative"""
    assert double(double(n)) == double(n) * 2
```

---

## Coverage Requirements

### Target: 80%+

**Current Status:** 15% → Target: 80%

### Measuring Coverage

```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html

# View report
open htmlcov/index.html

# Generate XML for CI
pytest --cov=src --cov-report=xml

# Check coverage threshold
pytest --cov=src --cov-fail-under=80
```

### Coverage by Module

| Module | Current | Target | Priority |
|--------|---------|--------|----------|
| src/analyzers | 15% | 80% | High |
| src/generators | 10% | 80% | High |
| src/validators | 30% | 80% | Medium |
| tools/ | 5% | 60% | Medium |
| scripts/ | 0% | 40% | Low |

### Improving Coverage

1. **Identify gaps:** Use coverage reports
2. **Write tests:** Focus on high-value code
3. **Review regularly:** Weekly coverage checks
4. **Enforce in CI:** Fail builds below threshold

---

## CI/CD Integration

### GitHub Actions

**Workflow:** `.github/workflows/ci.yml`

```yaml
test:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run tests
      run: pytest --cov=src --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

### Test Matrix

Run tests on multiple Python versions:

```yaml
strategy:
  matrix:
    python-version: ['3.7', '3.8', '3.9', '3.10', '3.11']
```

### Caching

Speed up CI with dependency caching:

```yaml
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
```

---

## Best Practices

### DO:

✅ Write tests before fixing bugs (TDD)  
✅ Keep tests simple and focused  
✅ Use descriptive test names  
✅ Test edge cases and error conditions  
✅ Mock external dependencies  
✅ Run tests before committing  
✅ Update tests with code changes  

### DON'T:

❌ Write tests that depend on other tests  
❌ Use hardcoded file paths  
❌ Test implementation details  
❌ Ignore failing tests  
❌ Skip writing tests for "simple" code  
❌ Commit commented-out tests  

---

## Troubleshooting

### Common Issues

**Problem:** Tests fail locally but pass in CI

**Solution:**
- Check Python version differences
- Verify all dependencies installed
- Check for missing test data files
- Review environment variables

**Problem:** Slow test execution

**Solution:**
- Use `pytest -m "not slow"` for quick runs
- Run tests in parallel: `pytest -n auto`
- Profile tests: `pytest --durations=10`
- Optimize or mark slow tests

**Problem:** Import errors in tests

**Solution:**
- Install package in editable mode: `pip install -e .`
- Check PYTHONPATH
- Verify test file naming (test_*.py)

**Problem:** Coverage not accurate

**Solution:**
- Check coverage config in pytest.ini
- Ensure all source files included
- Verify omit patterns
- Re-run with `--cov-append` if needed

---

## Advanced Topics

### Fixtures

**Scopes:**
- `function` - Run per test (default)
- `class` - Run per test class
- `module` - Run per module
- `session` - Run once per session

**Example:**
```python
@pytest.fixture(scope="session")
def minix_source():
    """Load MINIX source once"""
    return load_minix_source()
```

### Mocking

```python
from unittest.mock import Mock, patch

@patch('module.external_api_call')
def test_with_mock(mock_api):
    """Test with mocked external call"""
    mock_api.return_value = {'data': 'test'}
    result = function_that_calls_api()
    assert result == expected
```

### Temporary Files

```python
def test_with_temp_file(tmp_path):
    """Test using temporary file"""
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")
    assert test_file.read_text() == "content"
```

---

## Resources

### Documentation

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [hypothesis documentation](https://hypothesis.readthedocs.io/)

### Tools

- **pytest** - Testing framework
- **pytest-cov** - Coverage plugin
- **pytest-benchmark** - Performance testing
- **hypothesis** - Property-based testing
- **pytest-xdist** - Parallel execution

### Examples

See `tests/` directory for complete examples:
- `test_analyzers.py` - Unit test examples
- `test_integration.py` - Integration test examples
- `test_performance.py` - Benchmark examples
- `test_property_based.py` - Property-based test examples

---

## Checklist

### Before Committing

- [ ] All tests pass: `pytest`
- [ ] Coverage above threshold: `pytest --cov=src --cov-fail-under=80`
- [ ] No linting errors: `flake8 src/ tests/`
- [ ] Code formatted: `black src/ tests/`
- [ ] Type checks pass: `mypy src/`

### Before Merging

- [ ] All CI checks pass
- [ ] Coverage increased or maintained
- [ ] New features have tests
- [ ] Bug fixes have regression tests
- [ ] Documentation updated

---

**Maintained By:** Testing Team  
**Last Review:** 2025-11-04  
**Next Review:** 2026-02-04

---

*Test with confidence. Build with quality. Ship with pride.*

**AD ASTRA PER MATHEMATICA ET SCIENTIAM** ✨
