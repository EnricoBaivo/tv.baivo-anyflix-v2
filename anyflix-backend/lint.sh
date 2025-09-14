#!/bin/bash
# Comprehensive linting script for the project

echo "🔍 Running comprehensive code quality checks..."
echo "=============================================="

echo "📋 Running Ruff (fast linter)..."
uv run ruff check . || echo "❌ Ruff found issues"

echo ""
echo "🎨 Running Black (code formatter)..."
uv run black --check . || echo "❌ Black formatting issues found"

echo ""
echo "📦 Running isort (import sorting)..."
uv run isort --check-only . || echo "❌ Import sorting issues found"

echo ""
echo "🔬 Running mypy (type checking)..."
uv run mypy demo_bullet_anime.py lib/services/matching_service.py --show-error-codes || echo "❌ Type checking issues found"

echo ""
echo "✅ Linting complete!"
echo ""
echo "To fix issues automatically:"
echo "  - Formatting: uv run black ."
echo "  - Imports: uv run isort ."
echo "  - Some linting: uv run ruff check --fix ."
echo "  - Type issues: Fix manually based on mypy output"
