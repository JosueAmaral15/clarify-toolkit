#!/bin/bash
# CI/CD Quality Gates Script for Clarify Project
# Run this before committing code to ensure quality standards

set -e  # Exit on any error

echo "=========================================="
echo "🔍 Running Quality Gates for Clarify"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Change to project root
cd "$(dirname "$0")"

# 1. Black formatter
echo "📝 Step 1/5: Running Black (code formatter)..."
if python -m black --check --line-length=120 src/extractors/ src/gui/jsx_extractor_dock.py 2>&1; then
    echo -e "${GREEN}✅ Black: Code is properly formatted${NC}"
else
    echo -e "${YELLOW}⚠️  Black: Code needs formatting. Running formatter...${NC}"
    python -m black --line-length=120 src/extractors/ src/gui/jsx_extractor_dock.py
    echo -e "${GREEN}✅ Code formatted successfully${NC}"
fi
echo ""

# 2. isort (import sorting)
echo "📦 Step 2/5: Running isort (import sorting)..."
if python -m isort --check-only --profile=black --line-length=120 src/extractors/ src/gui/jsx_extractor_dock.py 2>&1; then
    echo -e "${GREEN}✅ isort: Imports are properly sorted${NC}"
else
    echo -e "${YELLOW}⚠️  isort: Imports need sorting. Running isort...${NC}"
    python -m isort --profile=black --line-length=120 src/extractors/ src/gui/jsx_extractor_dock.py
    echo -e "${GREEN}✅ Imports sorted successfully${NC}"
fi
echo ""

# 3. Pylint (code quality)
echo "🔎 Step 3/5: Running Pylint (code quality)..."
PYLINT_SCORE=$(python -m pylint src/extractors/ --rcfile=.pylintrc 2>&1 | grep "rated" | awk '{print $7}' | cut -d'/' -f1)
if (( $(echo "$PYLINT_SCORE >= 9.0" | bc -l) )); then
    echo -e "${GREEN}✅ Pylint: Score $PYLINT_SCORE/10 (threshold: 9.0/10)${NC}"
else
    echo -e "${RED}❌ Pylint: Score $PYLINT_SCORE/10 is below threshold (9.0/10)${NC}"
    echo "Run 'python -m pylint src/extractors/ --rcfile=.pylintrc' for details"
    exit 1
fi
echo ""

# 4. Syntax check
echo "✔️  Step 4/5: Checking Python syntax..."
if python -m py_compile src/extractors/*.py src/gui/jsx_extractor_dock.py 2>&1; then
    echo -e "${GREEN}✅ Syntax: No syntax errors found${NC}"
else
    echo -e "${RED}❌ Syntax errors detected${NC}"
    exit 1
fi
echo ""

# 5. Functional tests
echo "🧪 Step 5/5: Running functional tests..."
if python test_jsx_extractor.py 2>&1 | grep -q "🎉 ALL TESTS PASSED"; then
    echo -e "${GREEN}✅ Tests: All functional tests passed${NC}"
else
    echo -e "${RED}❌ Some tests failed${NC}"
    python test_jsx_extractor.py
    exit 1
fi
echo ""

# Summary
echo "=========================================="
echo -e "${GREEN}✅ All Quality Gates Passed!${NC}"
echo "=========================================="
echo "Code is ready for commit 🚀"
echo ""
