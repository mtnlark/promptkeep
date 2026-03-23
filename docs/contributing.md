# Contributing to PromptKeep

Thank you for your interest in contributing to PromptKeep! This document provides guidelines and instructions for contributing to the project.

## Getting Started

### Setting Up Your Development Environment

1. **Fork the repository** on GitHub.

2. **Clone your fork** to your local machine:
   ```bash
   git clone https://github.com/YOUR_USERNAME/promptkeep.git
   cd promptkeep
   ```

3. **Set up a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
   ```

4. **Install the package in development mode**:
   ```bash
   pip install -e .
   ```

5. **Install development dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

## Development Workflow

### Making Changes

1. **Create a new branch** for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding style and guidelines below.

3. **Write or update tests** that verify your changes.

4. **Run the tests** to ensure they pass:
   ```bash
   pytest
   ```

5. **Update documentation** if necessary.

### Submitting Changes

1. **Commit your changes** with a descriptive message:
   ```bash
   git commit -m "Add feature: your feature description"
   ```

2. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create a pull request** from your fork to the main repository.

## Coding Guidelines

### Architecture

PromptKeep uses dependency injection and protocol-based interfaces. When contributing:

- **Use `AppContext`** - Commands should receive dependencies via AppContext, not import them directly
- **Follow protocols** - New services should implement the appropriate protocol from `protocols.py`
- **Use custom exceptions** - Raise exceptions from `exceptions.py`, not generic Python exceptions
- **Keep modules focused** - Each module has a single responsibility

Example of using AppContext in a command:

```python
@app.command("mycommand")
@handle_errors
def my_command(vault_path: Optional[str] = None) -> None:
    ctx = get_context(vault_path)
    # Use ctx.repository, ctx.clipboard, ctx.editor, etc.
```

### Style Guide

- Follow [PEP 8](https://peps.python.org/pep-0008/) for Python code.
- Use meaningful variable and function names that describe their purpose.
- Keep functions and methods small and focused on a single responsibility.

### Documentation

- Write docstrings for all modules, classes, and functions.
- Follow the Google docstring format as demonstrated in the existing code.
- Include examples in docstrings when appropriate.
- Update relevant documentation in the `docs/` directory when making significant changes.

### Testing

- Write tests for new features and bug fixes
- Ensure all tests pass before submitting your changes
- We use `pytest` for testing
- Maintain test coverage above 90%

Run tests with coverage:

```bash
pytest --cov=promptkeep --cov-report=term-missing
```

The dependency injection architecture makes testing easy - you can mock services by passing test doubles to AppContext.

## Documentation

### Building Documentation

The documentation is built using [MkDocs](https://www.mkdocs.org/) with the [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) theme.

1. **Install documentation dependencies**:
   ```bash
   pip install mkdocs mkdocs-material
   ```

2. **Preview the documentation**:
   ```bash
   mkdocs serve
   ```
   This will start a local server at http://127.0.0.1:8000/ where you can preview your changes.

3. **Build the documentation**:
   ```bash
   mkdocs build
   ```
   This will generate static HTML files in the `site/` directory.

### Updating Documentation

- **Reference Documentation**: Update `docs/reference.md` when changing command-line parameters or adding new commands.
- **Usage Guide**: Update `docs/usage.md` for changes that affect how users interact with the tool.
- **Installation Instructions**: Update `docs/installation.md` if the installation process changes.

## Release Process

Releases are managed by the maintainers. The general process is:

1. **Version Bump**: Update the version in `pyproject.toml`.
2. **Changelog**: Update the changelog with a list of changes since the last release.
3. **Release Tag**: Create a tag for the release.
4. **PyPI Publishing**: Publish the new version to PyPI.

## Code of Conduct

Please be respectful and considerate of others when participating in this project. We strive to provide a welcoming and inclusive environment for everyone.

## Questions and Support

If you have questions or need support, please:

1. Check the existing documentation.
2. Look for existing issues in the GitHub repository.
3. Open a new issue if necessary.

Thank you for contributing to PromptKeep! 