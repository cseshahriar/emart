#!/bin/bash
# test_all.sh - Run all checks in one go

echo "🔍 Running flake8..."
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

echo "🎨 Running black..."
black . --check --diff

echo "📏 Running isort..."
isort . --check-only --diff

echo "🧪 Running tests with coverage..."
coverage run --source='.' manage.py test users
coverage report
coverage html  # Optional: generate HTML report

echo "✅ All checks completed!"
