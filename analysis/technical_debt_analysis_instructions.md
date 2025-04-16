# Django Technical Debt Analysis Instructions

This document outlines how to run the technical debt analysis scripts to generate comprehensive reports for each Django application and a project-wide summary.

## Overview

The analysis process involves the following steps:

1. Generate template files for each Django application
2. Gather basic metrics about each application (file count, line count, etc.)
3. Identify code quality issues and potential technical debt
4. Analyze architectural concerns and generate implementation recommendations
5. Generate executive summaries and a project-wide technical debt summary

## Prerequisites

- Python 3.6+
- Bash shell
- Access to the Django codebase

## Step 1: Generate Template Files

Run the script to create template files for each Django application:

```bash
cd /path/to/project
chmod +x analysis/scripts/generate_analysis_files.sh
./analysis/scripts/generate_analysis_files.sh
```

This will create template markdown files in the `analysis` directory for each Django application.

## Step 2: Gather Basic Metrics

Run the script to analyze each application and gather basic metrics:

```bash
chmod +x analysis/scripts/analyze_django_apps.py
./analysis/scripts/analyze_django_apps.py
```

This will update each application's analysis file with:
- File inventory (counts, types, lines of code)
- External dependencies and integration points

## Step 3: Identify Code Quality Issues

Run the script to analyze code quality and identify potential issues:

```bash
chmod +x analysis/scripts/identify_code_issues.py
./analysis/scripts/identify_code_issues.py
```

This will update each application's analysis file with:
- High complexity functions
- Large files
- Code smells (duplicate code, hardcoded secrets, TODOs, etc.)
- Prioritized issues with severity and effort ratings

## Step 4: Analyze Architecture

Run the script to analyze architectural concerns and generate recommendations:

```bash
chmod +x analysis/scripts/analyze_architecture.py
./analysis/scripts/analyze_architecture.py
```

This will update each application's analysis file with:
- Architectural issues
- Django-specific anti-patterns
- Missing architectural components
- Implementation timeline with short, medium, and long-term recommendations

## Step 5: Generate Summaries

Run the script to generate executive summaries and the project-wide technical debt summary:

```bash
chmod +x analysis/scripts/generate_summaries.py
./analysis/scripts/generate_summaries.py
```

This will:
- Add executive summaries to each application's analysis file
- Create a comprehensive technical debt summary for the entire project

## Output

After running all scripts, you'll have:

1. Individual analysis files for each Django application (`analysis/<app_name>.md`)
2. A project-wide technical debt summary (`analysis/technical_debt_summary.md`)
3. JSON data files with detailed analysis results:
   - `analysis/app_analysis_data.json`
   - `analysis/app_issues_data.json`
   - `analysis/app_architecture_data.json`

## Customizing the Analysis

You can customize the analysis by modifying the following files:

- **scripts/generate_analysis_files.sh**: Update the list of Django apps to analyze
- **scripts/identify_code_issues.py**: Adjust thresholds for complexity, file size, etc.
- **scripts/analyze_architecture.py**: Modify architectural criteria and recommendations
- **scripts/generate_summaries.py**: Change how applications are categorized and summarized

## Full Analysis in One Step

To run the entire analysis process in one step, you can use:

```bash
chmod +x analysis/scripts/*.py analysis/scripts/*.sh
./analysis/scripts/generate_analysis_files.sh
./analysis/scripts/analyze_django_apps.py
./analysis/scripts/identify_code_issues.py
./analysis/scripts/analyze_architecture.py
./analysis/scripts/generate_summaries.py
```

This will generate complete technical debt analysis for all Django applications in the project.

## Script Descriptions

1. **generate_analysis_files.sh**: Creates template markdown files for each application
2. **analyze_django_apps.py**: Gathers basic metrics about files, lines of code, etc.
3. **identify_code_issues.py**: Analyzes code quality issues using AST parsing
4. **analyze_architecture.py**: Identifies architectural concerns and anti-patterns
5. **generate_summaries.py**: Creates executive summaries and technical debt overview 