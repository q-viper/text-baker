# Tests for TextBaker

This folder contains unit tests and integration tests for the TextBaker package.

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=textbaker --cov-report=html

# Run specific test file
pytest tests/test_configs.py -v

# Run specific test
pytest tests/test_configs.py::test_transform_config_defaults -v
```

## Test Structure

- `conftest.py` - Pytest fixtures and configuration
- `test_configs.py` - Tests for configuration models
- `test_random_state.py` - Tests for random state management
- `test_generator.py` - Tests for TextGenerator class
- `test_ui_config.py` - Tests for UI configuration constants
- `test_cli.py` - Tests for CLI commands
