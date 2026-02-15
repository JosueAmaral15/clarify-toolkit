# COM8 Investigation Scripts

Diagnostic and debugging scripts used during Google Translate ODT feature development (Sessions 75-77).

## Directory Structure

```
scripts/com8/
├── investigate_*.py      # Investigation scripts
├── debug_*.py           # Debugging utilities  
├── diagnostic_*.py      # Diagnostic tools
├── trace_*.py           # Execution tracing
├── show_*.py            # Output visualization
├── COMPARE_*.py         # Comparison tools
├── DETAILED_*.py        # Detailed analysis
└── README.md            # This file
```

## Usage

These are ONE-OFF investigation tools, NOT unit tests.

```bash
# Example: Run investigation script
cd scripts/com8
PYTHONPATH=../../src python3 investigate_placeholder_corruption.py

# Example: Compare outputs
PYTHONPATH=../../src python3 COMPARE_FORMATTING_ORIGINAL_VS_TRANSLATED.py
```

## Script Categories

### Investigation
- `investigate_*.py` - Problem investigation (placeholder corruption, tab loss, etc.)

### Debugging
- `debug_*.py` - Segment debugging, format inspection
- `diagnostic_*.py` - ODT structure diagnosis

### Analysis
- `COMPARE_*.py` - Compare original vs translated
- `DETAILED_*.py` - Detailed formatting analysis
- `VISUAL_*.py` - Visual comparison tools
- `READ_*.py` - Content extraction tools

### Verification
- `trace_*.py` - Trace execution flow
- `show_*.py` - Show specific data (deleted line breaks, etc.)

## Notes

- These scripts were created during bug investigation
- They are kept for reference and future debugging
- Output files go to `.test_outputs/com8/`
- Not maintained as unit tests
