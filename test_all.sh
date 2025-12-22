#!/bin/bash
# test_all.sh - Run all checks in one go

set -e  # Exit immediately on error

echo "🔍 Running flake8 (critical errors)..."
flake8 . \
  --count \
  --select=E9,F63,F7,F82 \
  --show-source \
  --statistics

echo "🔍 Running flake8 (style & complexity)..."
flake8 . \
  --count \
  --max-complexity=10 \
  --max-line-length=79 \
  --statistics

echo "🎨 Running black (check only)..."
black . --check

echo "📏 Running isort (check only)..."
isort . --check-only

echo "🧪 Running tests with coverage..."
coverage run --source='.' manage.py test
coverage report
coverage html

echo "✅ All checks completed successfully!"
