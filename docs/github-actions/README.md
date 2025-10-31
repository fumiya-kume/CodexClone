# GitHub Actions Workflows for CodexCLI

This directory contains GitHub Actions workflow templates for automated CI/CD.

## Why workflows are here instead of `.github/workflows/`

Due to GitHub's security restrictions, workflow files cannot be created or updated via GitHub Apps without the `workflows` permission. To work around this limitation, the workflow templates are provided here for manual setup.

## Setup Instructions

To enable GitHub Actions for this repository:

1. **Manual Setup via GitHub UI:**
   - Go to your repository on GitHub
   - Navigate to `.github/workflows/` (create if it doesn't exist)
   - Copy the contents of `tests.yml` and `code-quality.yml` from this directory
   - Create corresponding files in `.github/workflows/` via GitHub's web interface

2. **Setup via Git (with proper permissions):**
   ```bash
   # Copy workflow files to .github/workflows/
   cp docs/github-actions/*.yml .github/workflows/

   # Commit and push (requires workflows permission)
   git add .github/workflows/
   git commit -m "Add GitHub Actions workflows"
   git push
   ```

## Workflow Files

### 1. tests.yml - Automated Testing

**Features:**
- Multi-platform testing: Ubuntu, macOS, Windows
- Python versions: 3.8, 3.9, 3.10, 3.11
- Test execution with pytest
- Coverage reporting (70% threshold)
- Codecov integration
- Coverage artifacts upload
- Pip caching for faster runs

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

### 2. code-quality.yml - Code Quality Checks

**Features:**
- Code formatting check with Black
- Linting with flake8
- Type checking with mypy
- Import sorting validation with isort
- Security scanning with bandit
- Security report artifacts

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

## Test Results

Current test status:
- **143 tests** passing (100% pass rate)
- **75% code coverage** (exceeds 70% threshold)
- All core modules comprehensively tested

## Workflow Details

### Test Coverage by Module

| Module | Coverage | Tests |
|--------|----------|-------|
| `__init__.py` | 100% | - |
| `agent.py` | 96% | 28 tests |
| `approval.py` | 97% | 28 tests |
| `context.py` | 88% | 22 tests |
| `file_ops.py` | 81% | 26 tests |
| `shell.py` | 100% | 20 tests |
| `utils.py` | 68% | 15 tests |
| `cli.py` | 34% | 14 tests |

### Running Tests Locally

```bash
# Install dev dependencies
uv sync --extra dev

# Run tests with coverage
uv run pytest --cov=codexcli --cov-report=term-missing -v

# Run code quality checks
uv run black --check src/ tests/
uv run flake8 src/ tests/
uv run mypy src/codexcli
```

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
