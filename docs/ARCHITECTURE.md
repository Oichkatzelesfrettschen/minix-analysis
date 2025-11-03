# Architecture Documentation

## Overview

This document describes the architecture and design decisions of the Visual Testing Playground project.

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Developer Machine                    │
│                                                          │
│  ┌────────────────┐         ┌─────────────────────┐    │
│  │   Local Code   │────────▶│  Docker Container   │    │
│  │                │  mount  │                     │    │
│  │  - gemini/     │         │  Node.js 18 LTS     │    │
│  │  - tests/      │         │  + Gemini v8        │    │
│  │  - scripts/    │         │  + GraphicsMagick   │    │
│  └────────────────┘         │                     │    │
│          │                  │  Runs tests         │    │
│          │                  │  Generates screens  │    │
│          ▼                  └─────────────────────┘    │
│  ┌────────────────┐                   │                │
│  │  Test Results  │◀──────────────────┘                │
│  │                │                                     │
│  │  - screens/    │  Results written back to host      │
│  │  - reports/    │                                     │
│  └────────────────┘                                     │
└─────────────────────────────────────────────────────────┘
```

## Components

### 1. Docker Layer

**Purpose**: Provide consistent, isolated testing environment

**Components**:
- `Dockerfile.gemini`: Defines the container image
- `scripts/gemini-docker.sh`: Wrapper script for Docker operations

**Key Features**:
- Node.js 18 LTS base
- GraphicsMagick for image processing
- Volume mounting for live code editing
- Automatic image building

**Design Decisions**:
- Use `bookworm-slim` variant to reduce image size
- Install Gemini globally for caching across runs
- Mount project directory as volume for development efficiency
- Keep system dependencies minimal

### 2. Testing Layer

**Purpose**: Define and execute visual regression tests

**Components**:
- `gemini/tests/*.test.js`: Test specifications
- `.gemini.yml`: Gemini configuration
- `gemini/screens/`: Reference screenshots

**Test Structure**:
```javascript
gemini.suite('Suite Name', (suite) => {
  suite
    .setUrl('/page')
    .setCaptureElements('.element')
    .capture('state', (actions, find) => {
      // Test actions
    });
});
```

**Design Decisions**:
- Organize tests by feature/page
- Use descriptive capture names
- Implement before/after hooks for setup/teardown
- Ignore dynamic content (timestamps, IDs)

### 3. Build & Automation Layer

**Purpose**: Automate building, testing, and deployment

**Components**:
- `.github/workflows/test.yml`: CI/CD pipeline
- `package.json` scripts: npm commands
- Git hooks via Husky: Pre-commit checks

**Pipeline Stages**:
1. **Lint**: Code quality checks
2. **Test**: Visual regression testing
3. **Security**: npm audit, Snyk scan
4. **Report**: Generate and upload artifacts

**Design Decisions**:
- Separate linting from testing for faster feedback
- Cache Docker layers for faster builds
- Upload artifacts for post-run analysis
- Run security checks on every PR

### 4. Code Quality Layer

**Purpose**: Maintain code consistency and quality

**Components**:
- `.eslintrc.json`: JavaScript linting rules
- `.prettierrc.json`: Code formatting rules
- Husky + lint-staged: Pre-commit hooks

**Quality Gates**:
- ESLint: Syntax and logic errors
- Prettier: Code formatting
- Pre-commit hooks: Prevent bad commits
- CI checks: Block merge on failure

## Data Flow

### Test Execution Flow

```
1. Developer runs: npm test (or ./scripts/gemini-docker.sh test)
                   │
                   ▼
2. Script checks for Docker image
                   │
                   ▼
3. If missing: Build image from Dockerfile
                   │
                   ▼
4. Mount project directory into container
                   │
                   ▼
5. Container runs Gemini with specified args
                   │
                   ▼
6. Gemini loads .gemini.yml config
                   │
                   ▼
7. Gemini executes test files
                   │
                   ▼
8. For each test:
   a. Navigate to URL
   b. Perform actions
   c. Capture screenshot
   d. Compare with reference
                   │
                   ▼
9. Generate HTML report
                   │
                   ▼
10. Write results to host filesystem
                   │
                   ▼
11. Exit with success/failure code
```

### CI/CD Flow

```
GitHub Event (push/PR)
        │
        ▼
Trigger GitHub Actions
        │
        ├─▶ Lint Job
        │   └─▶ ESLint + Prettier
        │
        ├─▶ Test Job
        │   ├─▶ Install dependencies
        │   ├─▶ Build Docker image
        │   ├─▶ Run tests
        │   └─▶ Upload artifacts
        │
        ├─▶ Docker Test Job
        │   └─▶ Verify wrapper script
        │
        └─▶ Security Job
            └─▶ npm audit + Snyk scan
```

## Design Principles

### 1. Reproducibility

**Goal**: Same test results across all environments

**Implementation**:
- Docker ensures consistent runtime
- Locked dependency versions
- Versioned reference images
- Documented setup process

### 2. Developer Experience

**Goal**: Fast, frictionless workflow

**Implementation**:
- Single command to run tests
- Automatic Docker image building
- Volume mounting for live editing
- Clear error messages
- Colored terminal output

### 3. Maintainability

**Goal**: Easy to update and extend

**Implementation**:
- Modular test organization
- Clear separation of concerns
- Comprehensive documentation
- Conventional commits
- Code formatting automation

### 4. Security

**Goal**: Keep dependencies secure

**Implementation**:
- Regular dependency updates
- Automated security scanning
- No hardcoded credentials
- Minimal system dependencies
- Latest LTS Node.js version

## Technology Stack

### Core Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| Node.js | 18 LTS | JavaScript runtime |
| npm | 9+ | Package management |
| Docker | 20.10+ | Containerization |
| Gemini | 8.0+ | Visual testing |
| GraphicsMagick | Latest | Image processing |

### Development Tools

| Tool | Purpose |
|------|---------|
| ESLint | JavaScript linting |
| Prettier | Code formatting |
| Husky | Git hooks |
| lint-staged | Pre-commit checks |
| Universal Ctags | Code navigation and indexing |

### CI/CD Tools

| Tool | Purpose |
|------|---------|
| GitHub Actions | CI/CD pipeline |
| Snyk | Security scanning |
| npm audit | Dependency auditing |

## Configuration Files

### Key Files

| File | Purpose |
|------|---------|
| `.gemini.yml` | Gemini test configuration |
| `.ctags.d/config.ctags` | Universal Ctags configuration |
| `Dockerfile.gemini` | Docker image definition |
| `package.json` | Node.js project metadata |
| `.eslintrc.json` | Linting rules |
| `.prettierrc.json` | Formatting rules |
| `.nvmrc` | Node version specification |

## Scalability Considerations

### Horizontal Scaling

Tests can run in parallel using Gemini's `parallelLimit` setting:

```yaml
system:
  parallelLimit: 5  # Run 5 tests concurrently
```

### Selenium Grid Integration

For distributed testing:

```yaml
gridUrl: http://selenium-hub:4444/wd/hub
```

### Multiple Browsers

Add browser configurations:

```yaml
browsers:
  chrome:
    # Chrome config
  firefox:
    # Firefox config
  safari:
    # Safari config
```

## Performance Optimizations

### Docker Layer Caching

1. Install system dependencies first (rarely change)
2. Install npm packages next (change occasionally)
3. Copy application code last (changes frequently)

### Test Execution

1. Use `parallelLimit` for concurrent tests
2. Reuse browser sessions (`testsPerSession`)
3. Set appropriate timeouts
4. Use headless mode

### CI/CD

1. Cache Docker layers between runs
2. Cache npm dependencies
3. Run lint before tests (fail fast)
4. Upload artifacts conditionally

## Security Model

### Docker Security

- Run as non-root user (planned)
- Minimal base image (slim variant)
- No privileged mode
- Read-only mounts where possible

### Dependency Security

- npm audit on every build
- Snyk scanning in CI
- Dependabot for automated updates
- Lock file for reproducibility

## Future Enhancements

### Planned Features

1. **Multi-browser support**: Firefox, Safari testing
2. **Visual diff reporting**: Better comparison UI
3. **Parallel execution**: Faster test runs
4. **Cloud integration**: BrowserStack/Sauce Labs
5. **Performance metrics**: Track test execution time

### Architectural Improvements

1. **Microservices**: Separate test runner from report generator
2. **API Layer**: RESTful API for remote test execution
3. **Database**: Store test history and trends
4. **Real-time updates**: WebSocket notifications

---

**Last Updated**: 2025-10-24
**Version**: 2.0.0
**Maintainer**: Eirikr
