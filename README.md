# Playground - Visual Testing Framework

A modern, Docker-based visual regression testing environment using Gemini framework for consistent cross-browser testing.

## Overview

This project provides a reproducible environment for visual regression testing using Gemini, containerized with Docker to ensure consistency across development environments.

## Features

- **Docker-based testing environment** - Consistent testing across all platforms
- **Node.js 18 LTS** - Modern, stable runtime with long-term support
- **Gemini visual testing** - Powerful visual regression testing framework
- **Automated setup** - Single command to build and run tests
- **Volume mounting** - Live code editing without container rebuild

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (optional, for orchestration)
- Node.js 18+ (for local development)
- GraphicsMagick (installed automatically in container)

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd Playground

# Ensure dependencies are up to date
npm install

# Or use make for full setup
make dev-setup
```

### 2. Run Tests with Docker

The project includes a convenient wrapper script that handles Docker image building and test execution:

```bash
# Run all tests
./scripts/gemini-docker.sh test

# Update reference screenshots
./scripts/gemini-docker.sh update

# Run specific test suite
./scripts/gemini-docker.sh test --grep "homepage"
```

### 3. Local Development (without Docker)

```bash
# Install dependencies
npm install

# Run tests locally
npm test

# Update reference images
npm run test:update

# Or use make commands
make test
make tags
make lint
```

For all available commands, run `make help`.

## Project Structure

```
Playground/
├── .claude/              # Claude Code configuration
├── .ctags.d/             # Ctags configuration
│   └── config.ctags      # Tag generation patterns
├── .github/              # CI/CD workflows
├── docs/                 # Documentation
│   ├── ARCHITECTURE.md   # Architecture overview
│   ├── CTAGS.md         # Ctags integration guide
│   └── ...
├── drivers/              # Driver implementations
│   └── logs/             # Runtime logs
├── gemini/               # Gemini test suites
│   ├── screens/          # Reference screenshots
│   └── tests/            # Test specifications
├── logs/                 # Application logs
├── scripts/              # Build and automation scripts
│   ├── gemini-docker.sh  # Docker wrapper for Gemini
│   ├── generate-tags.sh  # Ctags generation script
│   └── hooks/            # Git hook examples
├── .gitignore            # Git exclusions
├── .nvmrc                # Node version specification
├── Dockerfile.gemini     # Docker configuration
├── Makefile              # Build automation
├── package.json          # Node.js dependencies
└── README.md             # This file
```

## Configuration

### Node Version

This project uses Node.js 18 LTS. The version is specified in:
- `.nvmrc` - For nvm users
- `Dockerfile.gemini` - For containerized builds

### Gemini Configuration

Visual testing configuration is defined in `.gemini.yml`:

```yaml
system:
  projectRoot: .
  sourceRoot: gemini
  plugins:
    - gemini-gui

browsers:
  chrome:
    desiredCapabilities:
      browserName: chrome
```

See [Gemini documentation](https://github.com/gemini-testing/gemini) for advanced configuration.

## Docker Environment

### Building the Image

The Docker image is built automatically on first run, but you can manually build it:

```bash
docker build -f Dockerfile.gemini -t local/gemini-node18 .
```

### Image Contents

- **Base**: Node.js 18 LTS (Debian Bookworm)
- **npm**: Latest stable version
- **GraphicsMagick**: For image processing
- **Gemini**: Visual regression testing framework

### Environment Variables

```bash
# Override Docker image name
GEMINI_IMAGE=custom/image-name ./scripts/gemini-docker.sh test

# Pass additional Docker options
DOCKER_OPTS="--network host" ./scripts/gemini-docker.sh test
```

## Testing

### Writing Tests

Create test files in `gemini/tests/`:

```javascript
// gemini/tests/homepage.test.js
gemini.suite('Homepage', (suite) => {
  suite
    .setUrl('/')
    .setCaptureElements('.main-content')
    .capture('plain')
    .capture('with hover', (actions) => {
      actions.mouseMove('.button');
    });
});
```

### Running Tests

```bash
# All tests
npm test

# Specific suite
npm test -- --grep "Homepage"

# Update references
npm run test:update

# Generate HTML report
npm run test:report
```

### CI/CD Integration

GitHub Actions workflows are configured in `.github/workflows/`:

**Main Pipeline** (`test.yml`):
- Lint, format checking, and code quality
- **Ctags validation** - Validates tag generation and content
- Visual regression tests with Docker
- Security audits (npm audit, Snyk)
- **Build validation** - Tests Makefile targets
- **Integration summary** - Aggregates all results

**Ctags Documentation** (`ctags-docs.yml`):
- Validates ctags configuration and documentation
- Checks documentation links and completeness
- Generates documentation artifacts

**Release Management** (`release.yml`):
- Validates ctags for releases
- Packages ctags integration
- Auto-generates release notes

See [CI/CD Audit Report](docs/CICD_AUDIT.md) for complete details.
- Fails build on visual regression

## Development

### Local Setup

```bash
# Use correct Node version (with nvm)
nvm use

# Install dependencies
npm install

# Start development server (if applicable)
npm run dev
```

### Code Navigation

This project uses Universal Ctags for efficient code navigation:

```bash
# Generate tags file
npm run tags

# Update incrementally (faster)
npm run tags:incremental
```

See [docs/CTAGS.md](docs/CTAGS.md) for editor integration and advanced usage.

### Adding New Tests

1. Create test file in `gemini/tests/`
2. Run tests to generate reference images
3. Review and commit reference images
4. Push changes - CI will validate

### Debugging

```bash
# Run with verbose logging
DEBUG=gemini:* npm test

# Run single test
npm test -- --grep "specific test"

# Interactive mode
./scripts/gemini-docker.sh gui
```

## Troubleshooting

### Docker Issues

**Error: Cannot connect to Docker daemon**
```bash
# Start Docker service
sudo systemctl start docker

# Add user to docker group (Linux)
sudo usermod -aG docker $USER
```

**Error: Permission denied**
```bash
# Fix file permissions
chmod +x scripts/gemini-docker.sh
```

### Test Failures

**Visual differences detected**
1. Review differences in report: `gemini-report/index.html`
2. If changes are intentional: `npm run test:update`
3. Commit updated reference images

**Image processing errors**
- Ensure GraphicsMagick is installed
- Check Docker image includes `graphicsmagick`
- Verify image formats are supported (PNG, JPEG)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines and pull request process.

## License

ISC License - see [LICENSE](LICENSE) file for details.

## Resources

- [Gemini Documentation](https://github.com/gemini-testing/gemini)
- [Docker Documentation](https://docs.docker.com/)
- [Node.js Documentation](https://nodejs.org/docs/)
- [Visual Regression Testing Guide](https://martinfowler.com/articles/visual-testing.html)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and release notes.

---

**Note**: This project uses Docker to ensure consistent testing environments. All commands can be run locally or via Docker using the provided wrapper script.
