#!/usr/bin/env python3
"""
Generate executive summaries for each Django app and create the project-wide technical debt summary.
This script consolidates the analysis data and generates readable summaries.
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict

# Base path for the application
BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
APP_DIR = BASE_DIR / "application"
ANALYSIS_DIR = BASE_DIR / "analysis"

# List of Django apps to analyze
APPS = [
    "accounts",
    "budget",
    "dataentry",
    "events",
    "export_import",
    "firebase",
    "help",
    "id_matching",
    "legal",
    "portal",
    "rest_api",
    "static_border_stations",
    "util",
]

def load_analysis_data():
    """Load all analysis data for apps."""
    try:
        # Load basic app analysis data
        with open(ANALYSIS_DIR / "app_analysis_data.json", 'r', encoding='utf-8') as f:
            app_analysis_data = json.load(f)
        
        # Load code issues data
        with open(ANALYSIS_DIR / "app_issues_data.json", 'r', encoding='utf-8') as f:
            app_issues_data = json.load(f)
        
        # Load architecture data
        with open(ANALYSIS_DIR / "app_architecture_data.json", 'r', encoding='utf-8') as f:
            app_architecture_data = json.load(f)
        
        # Combine all data
        combined_data = {}
        for app_name in APPS:
            combined_data[app_name] = {
                "basic_analysis": app_analysis_data.get(app_name, {}),
                "issues": app_issues_data.get(app_name, {}),
                "architecture": app_architecture_data.get(app_name, {})
            }
        
        return combined_data
    except Exception as e:
        print(f"Error loading analysis data: {e}")
        return {}

def generate_executive_summary(app_name, app_data):
    """Generate an executive summary for a Django application."""
    summary = f"## Executive Summary\n\n"
    
    # Basic stats
    basic_data = app_data.get("basic_analysis", {})
    total_lines = basic_data.get("total_lines", 0)
    file_count = basic_data.get("file_count", 0)
    
    summary += f"The {app_name} application contains {file_count} files with approximately {total_lines} lines of code. "
    
    # Architecture overview
    arch_data = app_data.get("architecture", {})
    arch_issues = arch_data.get("architecture_issues", [])
    django_patterns = arch_data.get("django_anti_patterns", [])
    missing_components = arch_data.get("missing_components", [])
    
    if arch_issues:
        summary += f"The analysis identified {len(arch_issues)} architectural concerns, "
    else:
        summary += "No significant architectural issues were identified, "
    
    # Code issues overview
    issues_data = app_data.get("issues", {})
    high_complexity_funcs = issues_data.get("high_complexity_functions", [])
    large_files = issues_data.get("large_files", [])
    code_smells = issues_data.get("code_smells", [])
    
    code_issues_count = len(high_complexity_funcs) + len(large_files)
    
    if code_issues_count > 0:
        summary += f"along with {code_issues_count} code quality issues including {len(high_complexity_funcs)} high complexity functions and {len(large_files)} overly large files. "
    else:
        summary += "and minimal code quality concerns. "
    
    # Highlight key strengths
    strengths = []
    
    if not missing_components:
        strengths.append("well-structured with all expected architectural components")
    
    if len(high_complexity_funcs) < 3:
        strengths.append("maintains good function complexity levels")
    
    if len(large_files) < 2:
        strengths.append("keeps file sizes manageable")
    
    if not django_patterns:
        strengths.append("avoids common Django anti-patterns")
    
    if strengths:
        summary += f"Key strengths include being {', '.join(strengths)}. "
    
    # Highlight key weaknesses
    weaknesses = []
    
    if "services.py" in missing_components:
        weaknesses.append("lack of a dedicated service layer")
    
    if "tests" in missing_components:
        weaknesses.append("insufficient testing infrastructure")
    
    if "Business logic in views" in django_patterns or "Business logic in models" in django_patterns:
        weaknesses.append("business logic embedded in views/models instead of a service layer")
    
    if len(high_complexity_funcs) > 5:
        weaknesses.append("multiple high-complexity functions requiring refactoring")
    
    if len(large_files) > 3:
        weaknesses.append("several oversized files that should be modularized")
    
    if weaknesses:
        summary += f"Primary areas of technical debt include {', '.join(weaknesses)}. "
    
    # Prioritization summary
    summary += "\n\n"
    summary += "From a technical debt perspective, this application requires "
    
    # Determine the level of intervention needed
    if len(arch_issues) > 5 or len(high_complexity_funcs) > 5 or len(large_files) > 3:
        summary += "significant refactoring "
        intervention_level = "high"
    elif len(arch_issues) > 2 or len(high_complexity_funcs) > 2 or len(large_files) > 1:
        summary += "moderate improvements "
        intervention_level = "medium"
    else:
        summary += "minor enhancements "
        intervention_level = "low"
    
    # Implementation timeline focus
    timeline_data = arch_data.get("implementation_timeline", {})
    short_term = timeline_data.get("short_term", [])
    medium_term = timeline_data.get("medium_term", [])
    long_term = timeline_data.get("long_term", [])
    
    if intervention_level == "high":
        if medium_term and long_term:
            focus_items = []
            if medium_term:
                focus_items.append(f"{medium_term[0].get('title', 'architectural improvements')}")
            if long_term:
                focus_items.append(f"{long_term[0].get('title', 'strategic refactoring')}")
            
            summary += f"with focus on {' and '.join(focus_items)}. "
    elif intervention_level == "medium":
        if short_term and medium_term:
            focus_items = []
            if short_term:
                focus_items.append(f"{short_term[0].get('title', 'quick fixes')}")
            if medium_term:
                focus_items.append(f"{medium_term[0].get('title', 'architectural improvements')}")
            
            summary += f"with focus on {' and '.join(focus_items)}. "
    else:
        if short_term:
            summary += f"with focus on {short_term[0].get('title', 'minor improvements')}. "
    
    # Overall evaluation
    quality_level = ""
    if intervention_level == "low":
        quality_level = "high-quality"
    elif intervention_level == "medium":
        quality_level = "moderate-quality"
    else:
        quality_level = "maintenance-requiring"
    
    summary += f"\n\nOverall, the {app_name} application is a {quality_level} component of the system "
    
    if intervention_level == "high":
        summary += "that would benefit substantially from architectural improvements and code refactoring to improve maintainability and reduce technical debt."
    elif intervention_level == "medium":
        summary += "with some technical debt that should be addressed in the medium term to ensure continued maintainability."
    else:
        summary += "with minimal technical debt that can be addressed through routine maintenance."
    
    return summary

def update_app_with_executive_summary(app_name, summary):
    """Update app analysis file with executive summary."""
    analysis_path = ANALYSIS_DIR / f"{app_name}.md"
    
    if not analysis_path.exists():
        print(f"Analysis file not found: {analysis_path}")
        return
    
    with open(analysis_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace executive summary section
    pattern = r"## Executive Summary\n\n\[Insert 500-word summary of key findings here\]"
    
    if re.search(pattern, content):
        content = re.sub(pattern, summary, content)
    else:
        # Try to insert at the beginning if pattern not found
        content = summary + "\n\n" + content
    
    # Write updated content back to file
    with open(analysis_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Updated executive summary in file: {analysis_path}")

def generate_technical_debt_summary(all_app_data):
    """Generate the technical debt summary document."""
    summary_path = ANALYSIS_DIR / "technical_debt_summary.md"
    
    # Collect summary data
    total_files = 0
    total_lines = 0
    apps_by_quality = {
        "high": [],
        "medium": [],
        "low": []
    }
    
    all_issues = defaultdict(int)
    all_anti_patterns = defaultdict(int)
    
    # Count files and lines, categorize apps
    for app_name, app_data in all_app_data.items():
        basic_data = app_data.get("basic_analysis", {})
        total_files += basic_data.get("file_count", 0)
        total_lines += basic_data.get("total_lines", 0)
        
        # Categorize app quality
        arch_data = app_data.get("architecture", {})
        issues_data = app_data.get("issues", {})
        
        arch_issues = arch_data.get("architecture_issues", [])
        high_complexity_funcs = issues_data.get("high_complexity_functions", [])
        large_files = issues_data.get("large_files", [])
        
        # Count all architecture issues for summary
        for issue in arch_issues:
            all_issues[issue.get("issue", "Unknown issue")] += 1
        
        # Count anti-patterns for summary
        for pattern in arch_data.get("django_anti_patterns", []):
            all_anti_patterns[pattern] += 1
        
        # Determine app quality based on issue counts
        if len(arch_issues) > 5 or len(high_complexity_funcs) > 5 or len(large_files) > 3:
            apps_by_quality["low"].append(app_name)
        elif len(arch_issues) > 2 or len(high_complexity_funcs) > 2 or len(large_files) > 1:
            apps_by_quality["medium"].append(app_name)
        else:
            apps_by_quality["high"].append(app_name)
    
    # Generate summary content
    content = "# Technical Debt Summary\n\n"
    
    # Overview section
    content += "## Overview\n\n"
    content += f"This analysis examined {len(APPS)} Django applications totaling {total_files} files and approximately {total_lines} lines of code. "
    content += f"Based on architectural quality and code health metrics, the applications were categorized as follows:\n\n"
    
    content += f"- **High Quality ({len(apps_by_quality['high'])} apps)**: Well-structured with minimal technical debt\n"
    content += f"- **Medium Quality ({len(apps_by_quality['medium'])} apps)**: Functional but with moderate technical debt requiring attention\n"
    content += f"- **Needs Improvement ({len(apps_by_quality['low'])} apps)**: Significant technical debt requiring substantial refactoring\n\n"
    
    # Applications by category
    content += "### Applications by Quality Category\n\n"
    
    content += "**High Quality:**\n\n"
    if apps_by_quality['high']:
        for app in sorted(apps_by_quality['high']):
            content += f"- {app}\n"
    else:
        content += "- None\n"
    content += "\n"
    
    content += "**Medium Quality:**\n\n"
    if apps_by_quality['medium']:
        for app in sorted(apps_by_quality['medium']):
            content += f"- {app}\n"
    else:
        content += "- None\n"
    content += "\n"
    
    content += "**Needs Improvement:**\n\n"
    if apps_by_quality['low']:
        for app in sorted(apps_by_quality['low']):
            content += f"- {app}\n"
    else:
        content += "- None\n"
    content += "\n"
    
    # Patterns across applications
    content += "## Patterns Across Multiple Applications\n\n"
    
    # Common architectural issues
    content += "### Common Architectural Issues\n\n"
    
    # Sort issues by frequency
    sorted_issues = sorted(all_issues.items(), key=lambda x: x[1], reverse=True)
    
    for issue, count in sorted_issues[:10]:  # Top 10 issues
        if count > 1:  # Only show issues present in multiple apps
            content += f"- **{issue}** (found in {count} applications)\n"
    content += "\n"
    
    # Common anti-patterns
    content += "### Common Django Anti-patterns\n\n"
    
    # Sort anti-patterns by frequency
    sorted_patterns = sorted(all_anti_patterns.items(), key=lambda x: x[1], reverse=True)
    
    for pattern, count in sorted_patterns:
        if count > 1:  # Only show patterns present in multiple apps
            content += f"- **{pattern}** (found in {count} applications)\n"
    content += "\n"
    
    # Prioritized issues across codebase
    content += "## Prioritized Issues\n\n"
    
    # Highest priority issues first
    content += "### High Priority\n\n"
    content += "1. **Missing Service Layer**: Most applications lack a dedicated service layer for business logic, resulting in complex views and models.\n"
    content += "2. **Insufficient Testing**: Many applications have minimal or no automated tests, making refactoring risky.\n"
    content += "3. **Business Logic in Views/Models**: Business logic is frequently embedded directly in views and models rather than in dedicated service classes.\n"
    content += "4. **High Complexity Functions**: Several applications contain functions with excessive cyclomatic complexity.\n"
    content += "5. **Large Files**: Multiple applications contain oversized files that violate the single responsibility principle.\n\n"
    
    content += "### Medium Priority\n\n"
    content += "1. **Inconsistent View Implementations**: Mixed usage of function-based and class-based views within applications.\n"
    content += "2. **Direct ORM Queries in Views**: Database queries directly in view functions instead of through abstraction layers.\n"
    content += "3. **Lack of Type Hints**: Python type annotations are largely absent, reducing code clarity and IDE support.\n"
    content += "4. **Missing Custom Managers**: Complex database queries could benefit from dedicated model managers.\n"
    content += "5. **Duplicated Code**: Similar code patterns repeated across different applications.\n\n"
    
    content += "### Lower Priority\n\n"
    content += "1. **Magic Numbers/Strings**: Hardcoded values without named constants.\n"
    content += "2. **Inconsistent Coding Style**: Varied code formatting and structure across applications.\n"
    content += "3. **TODOs/FIXMEs**: Unresolved comments indicating known issues.\n"
    content += "4. **Oversized Models**: Models with too many fields or responsibilities.\n"
    content += "5. **Long Lines**: Code exceeding recommended line length limits.\n\n"
    
    # Technical debt roadmap
    content += "## Technical Debt Roadmap\n\n"
    
    content += "### Immediate Actions (1-2 Months)\n\n"
    content += "1. **Introduce Automated Testing**: Add tests for critical paths to enable safer refactoring.\n"
    content += "2. **Extract Complex Functions**: Break down high-complexity functions into smaller, more manageable units.\n"
    content += "3. **Add Type Hints**: Gradually introduce type annotations to critical code paths.\n"
    content += "4. **Document Architecture**: Create architectural documentation for the current system.\n"
    content += "5. **Standardize View Implementation**: Select a consistent approach to view implementation.\n\n"
    
    content += "### Short-term Improvements (2-6 Months)\n\n"
    content += "1. **Create Service Layer Template**: Design and implement a service layer pattern for one core application.\n"
    content += "2. **Refactor High-Priority Applications**: Focus on improving the most problematic applications identified in this analysis.\n"
    content += "3. **Implement Custom Managers**: Extract complex queries into dedicated manager classes.\n"
    content += "4. **Improve Error Handling**: Standardize exception handling across the codebase.\n"
    content += "5. **Extract Database Query Layer**: Move direct ORM calls from views to dedicated query functions.\n\n"
    
    content += "### Medium-term Strategy (6-12 Months)\n\n"
    content += "1. **Implement Service Layer Across Applications**: Roll out the service layer pattern to all applications.\n"
    content += "2. **Domain-Driven Redesign**: Restructure core modules around business domains.\n"
    content += "3. **Refactor Large Files**: Break oversized files into domain-focused modules.\n"
    content += "4. **Standardize Common Patterns**: Create shared utilities for frequently used code patterns.\n"
    content += "5. **Increase Test Coverage**: Build comprehensive test suites for all applications.\n\n"
    
    content += "### Long-term Vision (12+ Months)\n\n"
    content += "1. **Complete Architecture Modernization**: Transition to a fully service-oriented architecture.\n"
    content += "2. **Domain-Driven Design Implementation**: Restructure the entire system around well-defined domain boundaries.\n"
    content += "3. **API Standardization**: Ensure all internal and external APIs follow consistent patterns.\n"
    content += "4. **Comprehensive Testing Strategy**: Achieve high test coverage across the entire codebase.\n"
    content += "5. **Continuous Refactoring Process**: Establish an ongoing process to prevent new technical debt.\n\n"
    
    # Write the content to the file
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Generated technical debt summary: {summary_path}")

def main():
    """Main function to generate summaries."""
    print("Loading analysis data...")
    all_app_data = load_analysis_data()
    
    if not all_app_data:
        print("Error: Could not load analysis data. Make sure you've run the previous analysis scripts.")
        return
    
    print("Generating executive summaries for each application...")
    for app_name in APPS:
        if app_name in all_app_data:
            print(f"Generating summary for {app_name}...")
            app_summary = generate_executive_summary(app_name, all_app_data[app_name])
            update_app_with_executive_summary(app_name, app_summary)
    
    print("Generating technical debt summary document...")
    generate_technical_debt_summary(all_app_data)
    
    print("Summary generation complete.")

if __name__ == "__main__":
    main() 