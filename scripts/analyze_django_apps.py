#!/usr/bin/env python3
"""
Analyze Django applications for technical debt.
This script helps gather code metrics and identify potential issues.
"""

import os
import sys
import re
import subprocess
from collections import defaultdict
import json
from pathlib import Path

# Base path for the application
BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
APP_DIR = BASE_DIR / "application"

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

def count_lines(file_path):
    """Count the number of lines in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return len(f.readlines())
    except Exception as e:
        print(f"Error counting lines in {file_path}: {e}")
        return 0

def analyze_app(app_name):
    """Analyze a Django application and gather metrics."""
    app_path = APP_DIR / app_name
    
    if not app_path.exists():
        print(f"App directory not found: {app_path}")
        return None
    
    results = {
        "app_name": app_name,
        "files": [],
        "total_lines": 0,
        "file_count": 0,
        "file_types": defaultdict(int),
        "has_tests": False,
        "has_models": False,
        "has_views": False,
        "has_forms": False,
        "has_urls": False,
        "has_serializers": False,
        "dependencies": set(),
    }
    
    # Walk through app directory and gather file info
    for root, dirs, files in os.walk(app_path):
        for file in files:
            if file.endswith(('.py', '.html', '.js', '.css', '.json')):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, APP_DIR)
                line_count = count_lines(file_path)
                
                file_type = file.split('.')[-1]
                results["file_types"][file_type] += 1
                
                file_info = {
                    "path": rel_path,
                    "lines": line_count,
                    "type": file_type,
                }
                
                results["files"].append(file_info)
                results["total_lines"] += line_count
                results["file_count"] += 1
                
                # Check for key Django files
                if file == "models.py":
                    results["has_models"] = True
                elif file == "views.py":
                    results["has_views"] = True
                elif file == "forms.py":
                    results["has_forms"] = True
                elif file == "urls.py":
                    results["has_urls"] = True
                elif file == "serializers.py":
                    results["has_serializers"] = True
                
                # Check if tests directory exists
                if os.path.basename(root) == "tests" or file.startswith("test_"):
                    results["has_tests"] = True
    
    # Sort files by line count (descending)
    results["files"] = sorted(results["files"], key=lambda x: x["lines"], reverse=True)
    
    # Find imports and potential dependencies
    for file_info in results["files"]:
        if file_info["type"] == "py":
            file_path = os.path.join(APP_DIR, file_info["path"])
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Look for imports from other apps
                    for app in APPS:
                        if app != app_name and f"from {app}" in content:
                            results["dependencies"].add(app)
            except Exception as e:
                print(f"Error analyzing imports in {file_path}: {e}")
    
    # Convert set to list for JSON serialization
    results["dependencies"] = list(results["dependencies"])
    
    return results

def generate_markdown_inventory(app_analysis):
    """Generate markdown file inventory section from app analysis."""
    if not app_analysis:
        return "No analysis data available."
    
    markdown = "## File Inventory\n\n"
    markdown += "| File | Lines | Type |\n"
    markdown += "|------|-------|------|\n"
    
    for file_info in app_analysis["files"]:
        markdown += f"| {file_info['path']} | {file_info['lines']} | {file_info['type']} |\n"
    
    markdown += f"\n**Total Files:** {app_analysis['file_count']}\n"
    markdown += f"**Total Lines of Code:** {app_analysis['total_lines']}\n\n"
    
    # File type breakdown
    markdown += "### File Type Breakdown\n\n"
    for file_type, count in app_analysis["file_types"].items():
        markdown += f"- **{file_type}**: {count} files\n"
    
    return markdown

def generate_dependencies_section(app_analysis):
    """Generate markdown dependencies section from app analysis."""
    if not app_analysis:
        return "No dependencies data available."
    
    markdown = "## External Dependencies and Integration Points\n\n"
    
    if app_analysis["dependencies"]:
        markdown += "This application depends on the following other Django apps in the project:\n\n"
        for dep in sorted(app_analysis["dependencies"]):
            markdown += f"- **{dep}**\n"
    else:
        markdown += "This application has no direct dependencies on other apps in the project.\n"
    
    return markdown

def update_analysis_file(app_name, app_analysis):
    """Update the analysis markdown file with gathered metrics."""
    analysis_path = BASE_DIR / "analysis" / f"{app_name}.md"
    
    if not analysis_path.exists():
        print(f"Analysis file not found: {analysis_path}")
        return
    
    with open(analysis_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace file inventory section
    inventory_section = generate_markdown_inventory(app_analysis)
    content = re.sub(
        r"## File Inventory\n\n\[List of all files analyzed in this application\]",
        inventory_section,
        content
    )
    
    # Replace dependencies section
    dependencies_section = generate_dependencies_section(app_analysis)
    content = re.sub(
        r"## External Dependencies and Integration Points\n\n\[List of dependencies and integration points with other applications\]",
        dependencies_section,
        content
    )
    
    # Write updated content back to file
    with open(analysis_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Updated analysis file: {analysis_path}")

def main():
    """Main function to analyze all Django apps."""
    os.makedirs(BASE_DIR / "analysis", exist_ok=True)
    
    # Save full analysis data as JSON for reference
    all_app_data = {}
    
    for app_name in APPS:
        print(f"Analyzing {app_name}...")
        app_analysis = analyze_app(app_name)
        
        if app_analysis:
            all_app_data[app_name] = app_analysis
            update_analysis_file(app_name, app_analysis)
    
    # Save all analysis data to JSON file
    with open(BASE_DIR / "analysis" / "app_analysis_data.json", 'w', encoding='utf-8') as f:
        json.dump(all_app_data, f, indent=2)
    
    print("Analysis complete. Data saved to analysis/app_analysis_data.json")

if __name__ == "__main__":
    main() 