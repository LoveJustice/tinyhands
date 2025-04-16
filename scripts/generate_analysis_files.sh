#!/bin/bash

# Script to generate technical debt analysis template files for each Django app

# Directory for analysis files
ANALYSIS_DIR="analysis"

# Make sure the analysis directory exists
mkdir -p "$ANALYSIS_DIR"

# List of Django apps to analyze
APPS=(
  "accounts"
  "budget"
  "dataentry"
  "events"
  "export_import"
  "firebase"
  "help"
  "id_matching"
  "legal"
  "portal"
  "rest_api"
  "static_border_stations"
  "util"
)

# Template content for each app analysis
generate_template() {
  local app_name="$1"
  
  cat > "${ANALYSIS_DIR}/${app_name}.md" << EOF
# Technical Debt Analysis: ${app_name}

## Executive Summary

[Insert 500-word summary of key findings here]

## Table of Contents

- [File Inventory](#file-inventory)
- [Analysis of Key Components](#analysis-of-key-components)
  - [Models](#models)
  - [Views](#views)
  - [Forms](#forms)
  - [URLs](#urls)
  - [Serializers](#serializers)
- [Application-Specific Issues](#application-specific-issues)
- [External Dependencies and Integration Points](#external-dependencies-and-integration-points)
- [Prioritized Issues](#prioritized-issues)
- [Implementation Timeline](#implementation-timeline)
  - [Short-term Fixes (1-2 sprints)](#short-term-fixes-1-2-sprints)
  - [Medium-term Improvements (1-2 quarters)](#medium-term-improvements-1-2-quarters)
  - [Long-term Strategic Refactoring (6+ months)](#long-term-strategic-refactoring-6-months)

## File Inventory

[List of all files analyzed in this application]

## Analysis of Key Components

### Models

[Analysis of models.py and related files]

### Views

[Analysis of views.py and related files]

### Forms

[Analysis of forms.py and related files]

### URLs

[Analysis of urls.py]

### Serializers

[Analysis of serializers.py and related files]

## Application-Specific Issues

[Detailed list of application-specific issues]

## External Dependencies and Integration Points

[List of dependencies and integration points with other applications]

## Prioritized Issues

| Issue | Severity | Effort | Impact | Description |
|-------|----------|--------|--------|-------------|
| Issue 1 | High/Medium/Low | Small/Medium/Large | Description of impact | Detailed description with recommendation |

## Implementation Timeline

### Short-term Fixes (1-2 sprints)

[List of short-term fixes with descriptions]

### Medium-term Improvements (1-2 quarters)

[List of medium-term improvements with descriptions]

### Long-term Strategic Refactoring (6+ months)

[List of long-term refactoring efforts with descriptions]
EOF

  echo "Generated template for ${ANALYSIS_DIR}/${app_name}.md"
}

# Create a template file for each app
for app in "${APPS[@]}"; do
  generate_template "$app"
done

# Create summary file
cat > "${ANALYSIS_DIR}/technical_debt_summary.md" << EOF
# Technical Debt Summary

## Overview

[High-level overview of technical debt across the entire project]

## Patterns Across Multiple Applications

[Identified patterns that span multiple applications]

## Prioritized Issues

[Prioritized list of issues across the entire codebase]

## Technical Debt Roadmap

[Roadmap for addressing technical debt systematically]
EOF

echo "Generated ${ANALYSIS_DIR}/technical_debt_summary.md"
echo "All template files have been generated in the ${ANALYSIS_DIR} directory. Please fill them with your analysis." 