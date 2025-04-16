#!/bin/bash
# Run all technical debt analysis scripts in sequence

# Exit on any error
set -e

# Define paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
ANALYSIS_DIR="$BASE_DIR/analysis"

echo "===== Django Technical Debt Analysis ====="
echo "Starting analysis at $(date)"
echo

# Step 1: Generate template files
echo "Step 1: Generating template files..."
chmod +x "$SCRIPT_DIR/generate_analysis_files.sh"
"$SCRIPT_DIR/generate_analysis_files.sh"
echo "Template files created."
echo

# Step 2: Gather basic metrics
echo "Step 2: Gathering basic metrics..."
chmod +x "$SCRIPT_DIR/analyze_django_apps.py"
"$SCRIPT_DIR/analyze_django_apps.py"
echo "Basic metrics gathered."
echo

# Step 3: Identify code quality issues
echo "Step 3: Identifying code quality issues..."
chmod +x "$SCRIPT_DIR/identify_code_issues.py"
"$SCRIPT_DIR/identify_code_issues.py"
echo "Code quality issues identified."
echo

# Step 4: Analyze architecture
echo "Step 4: Analyzing architecture..."
chmod +x "$SCRIPT_DIR/analyze_architecture.py"
"$SCRIPT_DIR/analyze_architecture.py"
echo "Architecture analysis complete."
echo

# Step 5: Generate summaries
echo "Step 5: Generating summaries..."
chmod +x "$SCRIPT_DIR/generate_summaries.py"
"$SCRIPT_DIR/generate_summaries.py"
echo "Summaries generated."
echo

echo "===== Analysis Complete ====="
echo "Results are available in the $ANALYSIS_DIR directory:"
echo " - Individual app analyses: $ANALYSIS_DIR/<app_name>.md"
echo " - Project summary: $ANALYSIS_DIR/technical_debt_summary.md"
echo " - Analysis data: $ANALYSIS_DIR/*.json"
echo
echo "Analysis completed at $(date)" 