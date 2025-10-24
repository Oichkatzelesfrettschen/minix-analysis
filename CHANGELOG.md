# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project setup
- Docker-based testing environment
- Gemini visual regression testing framework
- Comprehensive documentation
- CI/CD pipeline with GitHub Actions
- ESLint and Prettier configuration
- Example test suites
- Contribution guidelines

## [2.0.0] - 2025-10-24

### Added
- Node.js 18 LTS support
- Modern npm version (v9+)
- Enhanced Docker wrapper script with:
  - Colored output
  - Better error handling
  - Docker daemon checks
  - GUI mode support
  - Environment variable configuration
- Comprehensive test examples:
  - Homepage tests
  - Responsive design tests
  - Form interaction tests
- GitHub Actions CI/CD pipeline:
  - Automated linting
  - Visual regression testing
  - Security auditing
  - Docker integration tests
- Development tooling:
  - ESLint configuration
  - Prettier code formatting
  - Husky git hooks
  - Lint-staged pre-commit checks
- Documentation:
  - Comprehensive README
  - Contributing guidelines
  - Code of Conduct
  - License file

### Changed
- **BREAKING**: Upgraded from Node 10 to Node 18 LTS
- **BREAKING**: Removed Python 2 dependency (EOL)
- Updated Dockerfile to use `node:18-bookworm-slim` base image
- Updated npm from 6.14.18 to latest stable
- Updated Gemini from v7.5.2 to v8.0.0
- Renamed Docker image from `local/gemini-node10` to `local/gemini-node18`
- Enhanced Dockerfile with:
  - Metadata labels
  - Health checks
  - Optimized layer caching
  - Smaller image size (using slim variant)
- Improved `.nvmrc` to specify Node 18.20.0
- Updated `.gitignore` with comprehensive exclusions

### Removed
- Python 2 system dependency
- Outdated npm version 6.x
- Node 10 support

### Fixed
- Security vulnerabilities from outdated dependencies
- Missing documentation
- Placeholder test script
- Incomplete project metadata

### Security
- Upgraded all dependencies to latest secure versions
- Added npm audit to CI/CD pipeline
- Added Snyk security scanning
- Removed EOL Python 2 runtime

## [1.0.0] - 2025-10-23

### Added
- Initial scaffold with minimal implementation
- Basic Docker configuration
- Node 10.24.1 support
- Gemini v7.5.2 installation
- Basic wrapper script

[Unreleased]: https://github.com/eirikr/playground/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/eirikr/playground/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/eirikr/playground/releases/tag/v1.0.0
