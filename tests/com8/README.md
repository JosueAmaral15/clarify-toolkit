# COM8 Test Files

Unit tests and integration tests for Google Translate ODT formatting features (Session 75-77).

## Directory Structure

```
tests/com8/
├── fixtures/              # Test data files
├── test_*.py             # Unit test files
└── README.md             # This file
```

## Running Tests

```bash
# Run all COM8 tests
pytest tests/com8/ -v

# Run specific test
pytest tests/com8/test_html_format_mapper_COM8.py -v

# Run with coverage
pytest tests/com8/ --cov=src/translation --cov-report=html
```

## Test Files

- `test_html_format_mapper_COM8.py` - HTML format system tests
- `test_html_to_odt_COM8.py` - ODT creation tests
- `test_complete_workflow_COM8.py` - End-to-end translation tests
- `test_text_extractor_*.py` - TextExtractor unit tests
- `check_*.py` - Validation scripts
- `verify_*.py` - Verification utilities

## Notes

- These tests use actual ODT files for integration testing
- Test outputs are stored in `.test_outputs/com8/` (gitignored)
- Tests require `python-odf` package
