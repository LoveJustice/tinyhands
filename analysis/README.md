# Django Technical Debt Analysis

This directory contains tools and results for analyzing technical debt in Django applications.

## Quick Start

To run the full technical debt analysis, use:

```bash
chmod +x scripts/run_analysis.sh
./scripts/run_analysis.sh
```

This will analyze all Django applications in the project and generate detailed reports.

## Analysis Process

The analysis follows these steps:

1. Generate template markdown files for each Django application
2. Gather basic metrics (file counts, line counts, dependencies)
3. Identify code quality issues (complexity, large files, code smells)
4. Analyze architectural concerns and anti-patterns
5. Generate executive summaries and a project-wide technical debt summary

## Results

After running the analysis, you'll find:

- Individual analysis files for each Django application (`<app_name>.md`)
- A project-wide technical debt summary (`technical_debt_summary.md`)
- JSON data files with detailed analysis results

## Documentation

For detailed instructions on how to run and customize the analysis, see:
- [Technical Debt Analysis Instructions](technical_debt_analysis_instructions.md)

## Scripts

The analysis is performed by the following scripts:

1. `scripts/generate_analysis_files.sh`: Creates template markdown files
2. `scripts/analyze_django_apps.py`: Gathers basic metrics
3. `scripts/identify_code_issues.py`: Analyzes code quality issues
4. `scripts/analyze_architecture.py`: Identifies architectural concerns
5. `scripts/generate_summaries.py`: Generates executive summaries
6. `scripts/run_analysis.sh`: Runs all steps in sequence

## Customization

To customize the analysis for your project:

1. Modify the list of Django apps in each script
2. Adjust thresholds for complexity, file size, etc.
3. Update the architectural criteria and recommendations
4. Change how applications are categorized and summarized

See the [Technical Debt Analysis Instructions](technical_debt_analysis_instructions.md) for details. 