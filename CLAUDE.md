# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python package called `refregion` for creating reference regions for PET (Positron Emission Tomography) analysis. The package provides functions and CLI tools to generate anatomical reference regions from brain segmentations, particularly focused on creating cerebellar reference regions and custom reference regions with morphological operations.

## Development Commands

## Development strategy

- Use a test-driven development strategy, developing tests prior to generating solutions to the tests.
- Run the tests and ensure that they fail prior to generating any solutions.
- Write code that passes the tests. 
- IMPORTANT: Do not modify the tests simply so that the code passes. Only modify the tests if you identify a specific error in the test.
- make sure to commit after each change.
- once a feature is implemented, use the code-review agent and refactor.

### Notes for Development

- Think about the problem before generating code.
- Always add a smoke test for the main() function.
- Prefer reliance on widely used packages (such as numpy, pandas, and scikit-learn); avoid unknown packages from Github.
- Do not include code in __init__.py files.
- Use pytest for testing.
- Write code that is clean and modular.  Prefer shorter functions/methods over longer ones.
- Use functions rather than classes for tests.  Use pytest fixtures to share resources between tests.
- Create code that will work in Python 3.13 or later

### Setup
```bash
# Install dependencies (Poetry is required)
poetry install --with dev
```

### Code Quality and Testing
```bash
# Format code with Black
poetry run black .

# Check formatting (CI-style)
poetry run black --check .

# Lint with flake8
poetry run flake8 refregion tests --max-line-length=120

# Run tests with coverage
poetry run pytest --cov=refregion --cov-report=xml

# Run a single test file
poetry run pytest tests/test_cerebellum.py
```

## Architecture

The package is organized into several core modules:

- **`refregion/refregion.py`**: Core functions for creating custom reference regions with morphological operations
- **`refregion/cerebellum.py`**: Specialized functions for cerebellar reference region creation
- **`refregion/morphology.py`**: Low-level morphological operations (erosion, dilation)
- **`refregion/wrappers.py`**: High-level wrapper functions and utilities
- **`refregion/cli/`**: Command-line interface implementations
  - `refregion.py`: General-purpose CLI for custom reference regions
  - `ref_cerebellum.py`: Specialized CLI for cerebellar reference regions

### Key Processing Pipeline

1. **Input handling**: NIfTI format medical images (`.nii`, `.nii.gz`)
2. **Region selection**: Extract specific anatomical indices from segmentation masks
3. **Morphological operations**: Apply erosion/dilation to refine regions and avoid contamination
4. **Exclusion processing**: Remove unwanted anatomical regions with optional dilation
5. **Output generation**: Save processed reference regions preserving original geometry

### CLI Tools Available

The package provides two main CLI entry points (defined in pyproject.toml):
- `refregion`: General-purpose reference region creation
- `ref_cerebellum`: Specialized cerebellar reference region creation

## Code Style

- Line length: 120 characters (configured in pyproject.toml)
- Formatter: Black
- Linter: flake8 with extensions E203, W503 ignored
- Type hints: Used throughout the codebase
- Medical imaging: Uses nibabel for NIfTI file handling, scikit-image for morphological operations

## Testing

Tests are located in the `tests/` directory with coverage configured to track the `refregion` package. The CI pipeline runs tests across Python 3.9, 3.10, and 3.11.