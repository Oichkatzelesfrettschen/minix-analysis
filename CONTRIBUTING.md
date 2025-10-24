# Contributing to Visual Testing Playground

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Commit Message Guidelines](#commit-message-guidelines)

## Code of Conduct

This project adheres to a code of conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## Getting Started

### Prerequisites

- Node.js 18 or higher
- Docker and Docker Compose
- Git
- A code editor (VS Code recommended)

### Initial Setup

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/playground.git
   cd playground
   ```

3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/eirikr/playground.git
   ```

4. Install dependencies:
   ```bash
   npm install
   ```

5. Verify your setup:
   ```bash
   npm test
   ./scripts/gemini-docker.sh --version
   ```

## Development Workflow

### 1. Create a Feature Branch

Always create a new branch for your work:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions or modifications

### 2. Make Your Changes

- Write clean, readable code
- Follow the existing code style
- Add comments for complex logic
- Update documentation as needed

### 3. Test Your Changes

Before committing:

```bash
# Run linter
npm run lint

# Fix lint issues automatically
npm run lint:fix

# Check code formatting
npm run format:check

# Fix formatting
npm run format

# Run tests
npm test

# Run Docker tests
npm run docker:test
```

### 4. Commit Your Changes

We use conventional commits for clear commit history:

```bash
git add .
git commit -m "type(scope): description"
```

See [Commit Message Guidelines](#commit-message-guidelines) for details.

### 5. Keep Your Branch Updated

```bash
git fetch upstream
git rebase upstream/main
```

### 6. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

## Pull Request Process

### Before Submitting

- [ ] All tests pass
- [ ] Code is properly formatted
- [ ] No linting errors
- [ ] Documentation is updated
- [ ] Commit messages follow conventions
- [ ] Branch is up to date with main

### Submitting Your PR

1. Go to the original repository on GitHub
2. Click "New Pull Request"
3. Select your fork and branch
4. Fill out the PR template with:
   - Clear description of changes
   - Related issue numbers
   - Screenshots (if applicable)
   - Testing performed
   - Breaking changes (if any)

### PR Review Process

1. **Automated Checks**: CI/CD pipeline runs automatically
   - Linting
   - Tests
   - Build verification
   - Security scans

2. **Code Review**: Maintainers review your code
   - May request changes
   - May ask questions
   - May suggest improvements

3. **Address Feedback**: Make requested changes
   ```bash
   # Make changes
   git add .
   git commit -m "fix: address review feedback"
   git push origin feature/your-feature-name
   ```

4. **Approval and Merge**: Once approved, maintainers will merge your PR

## Coding Standards

### JavaScript Style

- Use ES6+ features
- Use `const` by default, `let` when reassignment needed
- Avoid `var`
- Use arrow functions for callbacks
- Use template literals for string interpolation
- Add JSDoc comments for functions

Example:
```javascript
/**
 * Calculates the sum of two numbers
 * @param {number} a - First number
 * @param {number} b - Second number
 * @returns {number} Sum of a and b
 */
const add = (a, b) => a + b;
```

### File Organization

```
gemini/tests/
├── homepage.test.js
├── forms.test.js
└── navigation.test.js
```

- One test suite per file
- Clear, descriptive file names
- Group related tests together

### Naming Conventions

- **Files**: kebab-case (e.g., `user-profile.test.js`)
- **Functions**: camelCase (e.g., `getUserData`)
- **Classes**: PascalCase (e.g., `UserProfile`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_RETRIES`)

## Testing Guidelines

### Writing Visual Tests

```javascript
gemini.suite('Component Name', (suite) => {
  suite
    .setUrl('/page-url')
    .setCaptureElements('.target-element')
    .capture('state description', function(actions, find) {
      // Test actions here
    });
});
```

### Test Best Practices

1. **Descriptive Names**: Use clear test descriptions
2. **Isolation**: Each test should be independent
3. **Wait for Stability**: Add waits for animations
4. **Ignore Dynamic Content**: Use `.ignoreElements()` for timestamps, random data
5. **Capture Meaningful States**: Test all important visual states

### Updating Reference Images

When visual changes are intentional:

```bash
npm run test:update
git add screens/
git commit -m "test: update reference screenshots for button redesign"
```

## Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Build process or auxiliary tool changes
- `perf`: Performance improvements
- `ci`: CI/CD changes

### Examples

```bash
feat(tests): add responsive design tests

Add visual regression tests for mobile and tablet viewports.
Tests verify layout adapts correctly at 768px and 375px widths.

Closes #123
```

```bash
fix(docker): correct image name in wrapper script

Changed hardcoded 'node10' to 'node18' in IMAGE_NAME variable
to match updated Dockerfile base image.
```

```bash
docs(readme): update installation instructions

- Add prerequisites section
- Include Docker installation steps
- Fix typos in quick start guide
```

### Scope Examples

- `docker` - Docker-related changes
- `tests` - Test-related changes
- `ci` - CI/CD pipeline changes
- `config` - Configuration file changes
- `scripts` - Build/utility script changes

## Questions or Problems?

- **General Questions**: Open a [Discussion](https://github.com/eirikr/playground/discussions)
- **Bug Reports**: Open an [Issue](https://github.com/eirikr/playground/issues)
- **Feature Requests**: Open an [Issue](https://github.com/eirikr/playground/issues) with [Feature Request] tag

## License

By contributing, you agree that your contributions will be licensed under the ISC License.

---

Thank you for contributing! 🎉
