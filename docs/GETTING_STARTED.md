# Getting Started Guide

Complete guide to setting up and using this visual testing playground.

## Prerequisites

Before you begin, ensure you have the following installed:

### Required

- **Node.js 18+**: [Download here](https://nodejs.org/)
  ```bash
  node --version  # Should be >= 18.0.0
  ```

- **npm 9+**: Comes with Node.js, or upgrade:
  ```bash
  npm install -g npm@latest
  npm --version  # Should be >= 9.0.0
  ```

- **Docker**: [Get Docker](https://docs.docker.com/get-docker/)
  ```bash
  docker --version  # Should be >= 20.10.0
  docker info  # Verify daemon is running
  ```

- **Git**: [Install Git](https://git-scm.com/downloads)
  ```bash
  git --version
  ```

### Optional

- **nvm** (Node Version Manager): [Install nvm](https://github.com/nvm-sh/nvm)
- **Docker Compose**: [Install Compose](https://docs.docker.com/compose/install/)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/eirikr/playground.git
cd playground
```

### 2. Use Correct Node Version

If using nvm:
```bash
nvm use
# or if version not installed:
nvm install
```

Otherwise, ensure you're using Node 18+:
```bash
node --version
```

### 3. Install Dependencies

```bash
npm install
```

This installs:
- Gemini visual testing framework
- ESLint for linting
- Prettier for code formatting
- Development tools

### 4. Make Scripts Executable

```bash
chmod +x scripts/*.sh
```

## Quick Start

### Run Your First Test

#### Option 1: Using Docker (Recommended)

```bash
./scripts/gemini-docker.sh test
```

This will:
1. Build Docker image (first time only)
2. Run all tests
3. Generate HTML report

#### Option 2: Using npm

```bash
npm test
```

#### Option 3: Using Docker Compose

```bash
docker-compose up gemini
```

### View Results

After tests run:

```bash
# Open HTML report in browser
open gemini-report/index.html  # macOS
xdg-open gemini-report/index.html  # Linux
start gemini-report/index.html  # Windows
```

## Project Structure

```
playground/
├── gemini/              # Test files
│   ├── tests/          # Test specifications
│   └── screens/        # Reference screenshots
├── drivers/            # Custom driver implementations
├── scripts/            # Build and utility scripts
├── docs/              # Documentation
├── .github/           # CI/CD workflows
├── .gemini.yml        # Gemini configuration
├── Dockerfile.gemini  # Docker image
└── package.json       # Node.js dependencies
```

## Writing Your First Test

### 1. Create Test File

```bash
# Create new test file
touch gemini/tests/my-first-test.js
```

### 2. Write Test

```javascript
// gemini/tests/my-first-test.js
const gemini = require('gemini');

gemini.suite('My First Test', (suite) => {
  suite
    .setUrl('https://example.com')
    .setCaptureElements('body')
    .capture('homepage', function(actions, find) {
      // Test actions go here
    });
});
```

### 3. Run Test

```bash
npm test -- --grep "My First Test"
```

### 4. Update Reference Images

```bash
npm run test:update
```

### 5. Commit Reference Images

```bash
git add gemini/screens/
git commit -m "test: add My First Test reference images"
```

## Common Commands

### Testing

```bash
# Run all tests
npm test

# Run specific test
npm test -- --grep "test name"

# Update reference screenshots
npm run test:update

# Generate HTML report
npm run test:report

# Run in GUI mode
npm run test:gui
```

### Docker

```bash
# Build Docker image
docker build -f Dockerfile.gemini -t local/gemini-node18 .

# Run tests in Docker
./scripts/gemini-docker.sh test

# Update references in Docker
./scripts/gemini-docker.sh update

# Force rebuild image
FORCE_BUILD=1 ./scripts/gemini-docker.sh test
```

### Docker Compose

```bash
# Run tests
docker-compose up gemini

# Run with Selenium Grid
docker-compose --profile grid up

# Run specific command
docker-compose run --rm gemini update

# Clean up
docker-compose down -v
```

### Linting and Formatting

```bash
# Check code style
npm run lint

# Fix code style
npm run lint:fix

# Check formatting
npm run format:check

# Fix formatting
npm run format
```

### Git

```bash
# Check status
git status

# Stage changes
git add .

# Commit (will run pre-commit hooks)
git commit -m "type: description"

# Push to remote
git push
```

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/my-feature
```

### 2. Make Changes

Edit files in your editor.

### 3. Test Changes

```bash
npm test
npm run lint
```

### 4. Commit Changes

```bash
git add .
git commit -m "feat: add new feature"
```

### 5. Push and Create PR

```bash
git push origin feature/my-feature
# Then create Pull Request on GitHub
```

## Configuration

### Gemini Configuration

Edit `.gemini.yml`:

```yaml
system:
  projectRoot: .
  sourceRoot: gemini
  parallelLimit: 5  # Concurrent tests

browsers:
  chrome:
    windowSize: '1920x1080'
    tolerance: 2.5
```

### Docker Configuration

Edit environment variables:

```bash
# Use custom image name
GEMINI_IMAGE=my-custom-image ./scripts/gemini-docker.sh test

# Pass Docker options
DOCKER_OPTS="--network host" ./scripts/gemini-docker.sh test
```

### Node.js Configuration

Update Node version in:
- `.nvmrc` - For nvm users
- `Dockerfile.gemini` - For Docker
- `package.json` engines field

## Troubleshooting

### Issue: Tests Failing

**Solution**:
1. Check if images match expectations
2. View HTML report: `open gemini-report/index.html`
3. If intentional changes: `npm run test:update`

### Issue: Docker Permission Denied

**Solution**:
```bash
# Add user to docker group (Linux)
sudo usermod -aG docker $USER
# Log out and back in

# Or use sudo
sudo ./scripts/gemini-docker.sh test
```

### Issue: Port Already in Use

**Solution**:
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
DOCKER_OPTS="-p 8001:8000" ./scripts/gemini-docker.sh gui
```

### Issue: Out of Memory

**Solution**:

Reduce parallel tests in `.gemini.yml`:
```yaml
system:
  parallelLimit: 2  # Reduce from 5 to 2
```

### Issue: Lint Errors

**Solution**:
```bash
# Auto-fix most issues
npm run lint:fix
npm run format

# Check remaining issues
npm run lint
```

## Next Steps

Now that you're set up:

1. **Read the docs**:
   - [Architecture](./ARCHITECTURE.md)
   - [Contributing](../CONTRIBUTING.md)
   - [API Reference](./API.md)

2. **Explore examples**:
   - Check `gemini/tests/example.test.js`
   - Review `drivers/example-driver.js`

3. **Write tests**:
   - Create test files in `gemini/tests/`
   - Run and update references
   - Commit your work

4. **Customize**:
   - Modify `.gemini.yml` for your needs
   - Add custom drivers in `drivers/`
   - Update CI/CD in `.github/workflows/`

5. **Contribute**:
   - Fix bugs
   - Add features
   - Improve documentation
   - See [CONTRIBUTING.md](../CONTRIBUTING.md)

## Getting Help

- **Documentation**: Browse `docs/` directory
- **Issues**: [GitHub Issues](https://github.com/eirikr/playground/issues)
- **Discussions**: [GitHub Discussions](https://github.com/eirikr/playground/discussions)
- **Email**: [your-email@example.com]

## Resources

- [Gemini Documentation](https://github.com/gemini-testing/gemini)
- [Docker Documentation](https://docs.docker.com/)
- [Node.js Best Practices](https://github.com/goldbergyoni/nodebestpractices)
- [Visual Testing Guide](https://martinfowler.com/articles/visual-testing.html)

---

**Happy Testing!** 🎉

If you found this guide helpful, please star the repository and share with others.
