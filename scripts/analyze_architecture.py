#!/usr/bin/env python3
"""
Analyze Django application architecture and generate implementation timelines.
This script helps identify architectural issues and recommend improvements.
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict

# Base path for the application
BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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

def analyze_app_architecture(app_name):
    """Analyze the architecture of a Django application."""
    app_path = APP_DIR / app_name
    
    if not app_path.exists():
        print(f"App directory not found: {app_path}")
        return None
    
    results = {
        "app_name": app_name,
        "architecture_issues": [],
        "missing_components": [],
        "django_anti_patterns": [],
        "implementation_timeline": {
            "short_term": [],
            "medium_term": [],
            "long_term": []
        }
    }
    
    # Check for key files/components
    key_files = {
        "models.py": False,
        "views.py": False,
        "forms.py": False,
        "serializers.py": False,
        "urls.py": False,
        "tests": False,
        "services.py": False,
        "managers.py": False,
    }
    
    for root, dirs, files in os.walk(app_path):
        for file in files:
            if file in key_files:
                key_files[file] = True
        
        if "tests" in dirs:
            key_files["tests"] = True
    
    # Detect missing architectural components
    for component, exists in key_files.items():
        if not exists:
            if component == "services.py":
                results["architecture_issues"].append({
                    "issue": "Missing service layer",
                    "description": "No service layer found to separate business logic from views/models.",
                    "impact": "Business logic is likely mixed with presentation logic in views or data access in models."
                })
                results["missing_components"].append(component)
            elif component == "managers.py":
                results["architecture_issues"].append({
                    "issue": "Missing custom model managers",
                    "description": "No custom manager layer to abstract complex queries from models and views.",
                    "impact": "Complex queries likely embedded in views or scattered across the codebase."
                })
                results["missing_components"].append(component)
            elif component == "tests":
                results["architecture_issues"].append({
                    "issue": "Missing tests directory",
                    "description": "No dedicated tests directory found.",
                    "impact": "Application may lack proper test coverage."
                })
                results["missing_components"].append(component)
            elif component == "forms.py" and key_files["views.py"]:
                # Only flag missing forms if we have views
                results["missing_components"].append(component)
                
    # Analyze models.py for architectural issues
    models_path = app_path / "models.py"
    if models_path.exists():
        try:
            with open(models_path, 'r', encoding='utf-8') as f:
                models_content = f.read()
                
                # Check for large models (potential god objects)
                model_classes = re.findall(r'class\s+(\w+)\(.*Model.*\):', models_content)
                if len(model_classes) > 5:
                    results["architecture_issues"].append({
                        "issue": "Too many models in a single file",
                        "description": f"Found {len(model_classes)} model classes in models.py.",
                        "impact": "Indicates potential lack of proper domain separation and modularity."
                    })
                
                # Check for business logic in models
                if re.search(r'def\s+\w+\(self.*\):.{100,}', models_content, re.DOTALL):
                    results["architecture_issues"].append({
                        "issue": "Complex business logic in models",
                        "description": "Models contain complex methods that should be in a service layer.",
                        "impact": "Violates separation of concerns, makes testing harder."
                    })
                    results["django_anti_patterns"].append("Business logic in models")
                
                # Check for model properties that should be methods
                if re.search(r'@property\s*\ndef\s+\w+\(self\):.{100,}', models_content, re.DOTALL):
                    results["architecture_issues"].append({
                        "issue": "Complex logic in model properties",
                        "description": "Models have complex properties that might be better as methods or in services.",
                        "impact": "Can lead to performance issues and violates separation of concerns."
                    })
        except Exception as e:
            print(f"Error analyzing models.py for {app_name}: {e}")
    
    # Analyze views.py for architectural issues
    views_path = app_path / "views.py"
    if views_path.exists():
        try:
            with open(views_path, 'r', encoding='utf-8') as f:
                views_content = f.read()
                
                # Check for business logic in views
                if re.search(r'def\s+\w+\(.*\):.{200,}', views_content, re.DOTALL):
                    results["architecture_issues"].append({
                        "issue": "Complex business logic in views",
                        "description": "Views contain complex methods that should be in a service layer.",
                        "impact": "Violates separation of concerns, makes testing harder."
                    })
                    results["django_anti_patterns"].append("Business logic in views")
                
                # Check for mixing of view types (function-based vs class-based)
                has_fbv = re.search(r'def\s+\w+\(request', views_content) is not None
                has_cbv = re.search(r'class\s+\w+View\(', views_content) is not None
                
                if has_fbv and has_cbv:
                    results["architecture_issues"].append({
                        "issue": "Mixing function-based and class-based views",
                        "description": "The application mixes both view styles, which can be confusing.",
                        "impact": "Inconsistent patterns make code harder to understand and maintain."
                    })
                    results["django_anti_patterns"].append("Mixed view styles")
                
                # Check for direct ORM queries in views
                if re.search(r'Model\.objects\.filter\(|Model\.objects\.get\(|Model\.objects\.all\(', views_content):
                    results["architecture_issues"].append({
                        "issue": "Direct ORM queries in views",
                        "description": "Views contain direct ORM queries instead of using a service layer.",
                        "impact": "Makes views harder to test and violates separation of concerns."
                    })
                    results["django_anti_patterns"].append("Direct ORM in views")
        except Exception as e:
            print(f"Error analyzing views.py for {app_name}: {e}")
    
    # Load existing issues data to inform recommendations
    try:
        with open(ANALYSIS_DIR / "app_issues_data.json", 'r', encoding='utf-8') as f:
            all_issues_data = json.load(f)
            app_issues = all_issues_data.get(app_name, {})
            
            # If we have high complexity functions, add as architectural issues
            high_complexity_funcs = app_issues.get("high_complexity_functions", [])
            if len(high_complexity_funcs) > 3:
                results["architecture_issues"].append({
                    "issue": "Multiple high complexity functions",
                    "description": f"Found {len(high_complexity_funcs)} functions with high cyclomatic complexity.",
                    "impact": "Indicates code that is difficult to maintain and test."
                })
            
            # If we have large files, add as architectural issues
            large_files = app_issues.get("large_files", [])
            if len(large_files) > 2:
                results["architecture_issues"].append({
                    "issue": "Multiple large files",
                    "description": f"Found {len(large_files)} files with excessive line counts.",
                    "impact": "Indicates poor modularity and separation of concerns."
                })
            
            # Find Django anti-patterns in code smells
            code_smells = app_issues.get("code_smells", [])
            django_pattern_smells = [s for s in code_smells if s.get("category") == "Django Anti-patterns"]
            if django_pattern_smells:
                patterns = set()
                for smell in django_pattern_smells:
                    if ".extra(" in smell.get("content", ""):
                        patterns.add("Using .extra() method")
                    elif ".values(" in smell.get("content", ""):
                        patterns.add("Overuse of .values()")
                    elif "raw(" in smell.get("content", ""):
                        patterns.add("Using raw SQL")
                
                for pattern in patterns:
                    if pattern not in results["django_anti_patterns"]:
                        results["django_anti_patterns"].append(pattern)
    except Exception as e:
        print(f"Error loading issues data for {app_name}: {e}")
    
    # Generate implementation timeline recommendations based on findings
    generate_implementation_timeline(results)
    
    return results

def generate_implementation_timeline(results):
    """Generate implementation timeline recommendations based on architectural findings."""
    # Short-term fixes (1-2 sprints)
    if "Direct ORM in views" in results["django_anti_patterns"]:
        results["implementation_timeline"]["short_term"].append({
            "title": "Extract database queries from views",
            "description": "Move direct ORM queries from views into a query layer or service functions.",
            "effort": "Medium",
            "benefits": ["Improves testability", "Reduces view complexity", "First step toward service layer"]
        })
    
    if "Mixed view styles" in results["django_anti_patterns"]:
        results["implementation_timeline"]["short_term"].append({
            "title": "Standardize view implementations",
            "description": "Convert all views to a consistent style (class-based or function-based).",
            "effort": "Medium",
            "benefits": ["Improves code consistency", "Makes codebase easier to understand"]
        })
    
    # Add common short-term recommendations
    results["implementation_timeline"]["short_term"].append({
        "title": "Add type hints to function signatures",
        "description": "Add Python type hints to critical functions for better IDE support and documentation.",
        "effort": "Small",
        "benefits": ["Improves code clarity", "Reduces bugs", "Better IDE support"]
    })
    
    # Medium-term improvements (1-2 quarters)
    if "Missing service layer" in [issue["issue"] for issue in results["architecture_issues"]]:
        results["implementation_timeline"]["medium_term"].append({
            "title": "Implement service layer",
            "description": "Create a service.py file to house business logic extracted from views and models.",
            "effort": "Large",
            "benefits": ["Separation of concerns", "Improves testability", "Centralizes business logic"]
        })
    
    if "Business logic in models" in results["django_anti_patterns"]:
        results["implementation_timeline"]["medium_term"].append({
            "title": "Extract business logic from models",
            "description": "Move complex methods and properties from models to appropriate service classes.",
            "effort": "Medium",
            "benefits": ["Slimmer models", "Better separation of concerns", "Improved testability"]
        })
    
    if "Missing custom model managers" in [issue["issue"] for issue in results["architecture_issues"]]:
        results["implementation_timeline"]["medium_term"].append({
            "title": "Implement custom model managers",
            "description": "Create managers.py to encapsulate complex query logic and database operations.",
            "effort": "Medium",
            "benefits": ["Query reusability", "Cleaner models", "Improved abstraction"]
        })
    
    # Long-term strategic refactoring (6+ months)
    # Common long-term recommendations
    results["implementation_timeline"]["long_term"].append({
        "title": "Implement Domain-Driven Design principles",
        "description": "Restructure app around business domains with clear boundaries and service interfaces.",
        "effort": "Large",
        "benefits": ["Better alignment with business needs", "Improved maintainability", "Clearer architecture"]
    })
    
    if "Too many models in a single file" in [issue["issue"] for issue in results["architecture_issues"]]:
        results["implementation_timeline"]["long_term"].append({
            "title": "Reorganize models into domain modules",
            "description": "Split models.py into multiple domain-specific modules with related models grouped together.",
            "effort": "Large",
            "benefits": ["Improved organization", "Better domain separation", "Reduced file size"]
        })
    
    # Add app-specific long-term recommendations based on name
    if results["app_name"] == "accounts":
        results["implementation_timeline"]["long_term"].append({
            "title": "Implement proper authentication service layer",
            "description": "Refactor authentication logic into a dedicated service with clear interfaces.",
            "effort": "Large",
            "benefits": ["Improved security", "Better user management", "Cleaner authentication flow"]
        })
    elif results["app_name"] in ["dataentry", "export_import"]:
        results["implementation_timeline"]["long_term"].append({
            "title": "Implement Command Query Responsibility Segregation (CQRS)",
            "description": "Separate read and write operations for complex data flows.",
            "effort": "Large",
            "benefits": ["Improved performance", "Better scalability", "Clearer data flow"]
        })
    
    return results

def generate_architecture_section(app_analysis):
    """Generate markdown section for architectural concerns."""
    if not app_analysis:
        return "No architecture analysis data available."
    
    markdown = "## Architecture Analysis\n\n"
    
    # Architectural Issues
    if app_analysis["architecture_issues"]:
        markdown += "### Architectural Issues\n\n"
        for issue in app_analysis["architecture_issues"]:
            markdown += f"#### {issue['issue']}\n\n"
            markdown += f"**Description:** {issue['description']}\n\n"
            markdown += f"**Impact:** {issue['impact']}\n\n"
    else:
        markdown += "### Architectural Issues\n\n"
        markdown += "No significant architectural issues identified.\n\n"
    
    # Django Anti-patterns
    if app_analysis["django_anti_patterns"]:
        markdown += "### Django-Specific Anti-patterns\n\n"
        for pattern in app_analysis["django_anti_patterns"]:
            markdown += f"- {pattern}\n"
        markdown += "\n"
    else:
        markdown += "### Django-Specific Anti-patterns\n\n"
        markdown += "No significant Django anti-patterns identified.\n\n"
    
    # Missing Components
    if app_analysis["missing_components"]:
        markdown += "### Missing Architectural Components\n\n"
        for component in app_analysis["missing_components"]:
            markdown += f"- {component}\n"
        markdown += "\n"
    
    return markdown

def generate_timeline_section(app_analysis):
    """Generate markdown section for implementation timeline."""
    if not app_analysis:
        return "No implementation timeline data available."
    
    markdown = "## Implementation Timeline\n\n"
    
    # Short-term fixes
    markdown += "### Short-term Fixes (1-2 sprints)\n\n"
    if app_analysis["implementation_timeline"]["short_term"]:
        for item in app_analysis["implementation_timeline"]["short_term"]:
            markdown += f"#### {item['title']}\n\n"
            markdown += f"**Description:** {item['description']}\n\n"
            markdown += f"**Effort:** {item['effort']}\n\n"
            markdown += "**Benefits:**\n"
            for benefit in item["benefits"]:
                markdown += f"- {benefit}\n"
            markdown += "\n"
    else:
        markdown += "No short-term fixes identified.\n\n"
    
    # Medium-term improvements
    markdown += "### Medium-term Improvements (1-2 quarters)\n\n"
    if app_analysis["implementation_timeline"]["medium_term"]:
        for item in app_analysis["implementation_timeline"]["medium_term"]:
            markdown += f"#### {item['title']}\n\n"
            markdown += f"**Description:** {item['description']}\n\n"
            markdown += f"**Effort:** {item['effort']}\n\n"
            markdown += "**Benefits:**\n"
            for benefit in item["benefits"]:
                markdown += f"- {benefit}\n"
            markdown += "\n"
    else:
        markdown += "No medium-term improvements identified.\n\n"
    
    # Long-term strategic refactoring
    markdown += "### Long-term Strategic Refactoring (6+ months)\n\n"
    if app_analysis["implementation_timeline"]["long_term"]:
        for item in app_analysis["implementation_timeline"]["long_term"]:
            markdown += f"#### {item['title']}\n\n"
            markdown += f"**Description:** {item['description']}\n\n"
            markdown += f"**Effort:** {item['effort']}\n\n"
            markdown += "**Benefits:**\n"
            for benefit in item["benefits"]:
                markdown += f"- {benefit}\n"
            markdown += "\n"
    else:
        markdown += "No long-term strategic refactoring identified.\n\n"
    
    return markdown

def update_analysis_file_with_architecture(app_name, app_analysis):
    """Update the analysis markdown file with architecture analysis."""
    analysis_path = ANALYSIS_DIR / f"{app_name}.md"
    
    if not analysis_path.exists():
        print(f"Analysis file not found: {analysis_path}")
        return
    
    with open(analysis_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add architecture section after file inventory
    architecture_section = generate_architecture_section(app_analysis)
    
    # Check if there's already an Architecture Analysis section
    if "## Architecture Analysis" not in content:
        # Find where to insert the architecture section
        file_inventory_pos = content.find("## Analysis of Key Components")
        
        if file_inventory_pos != -1:
            # Insert architecture section before Analysis of Key Components
            content = (
                content[:file_inventory_pos] + 
                architecture_section + 
                content[file_inventory_pos:]
            )
        else:
            # Append to the end if we can't find the insertion point
            content += "\n\n" + architecture_section
    
    # Write updated content back to file
    with open(analysis_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Updated architecture analysis in file: {analysis_path}")

def update_analysis_file_with_timeline(app_name, app_analysis):
    """Update the analysis markdown file with implementation timeline."""
    analysis_path = ANALYSIS_DIR / f"{app_name}.md"
    
    if not analysis_path.exists():
        print(f"Analysis file not found: {analysis_path}")
        return
    
    with open(analysis_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace timeline sections
    timeline_section = generate_timeline_section(app_analysis)
    
    # Replace implementation timeline section
    pattern = r"## Implementation Timeline\n\n### Short-term Fixes \(1-2 sprints\)\n\n\[List of short-term fixes with descriptions\]\n\n### Medium-term Improvements \(1-2 quarters\)\n\n\[List of medium-term improvements with descriptions\]\n\n### Long-term Strategic Refactoring \(6\+ months\)\n\n\[List of long-term refactoring efforts with descriptions\]"
    
    if re.search(pattern, content):
        content = re.sub(pattern, timeline_section, content)
    else:
        # Append to the end if we can't find the pattern
        content += "\n\n" + timeline_section
    
    # Write updated content back to file
    with open(analysis_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Updated implementation timeline in file: {analysis_path}")

def main():
    """Main function to analyze architecture in all Django apps."""
    os.makedirs(ANALYSIS_DIR, exist_ok=True)
    
    # Save full analysis data as JSON for reference
    all_app_architecture = {}
    
    for app_name in APPS:
        print(f"Analyzing architecture in {app_name}...")
        app_architecture = analyze_app_architecture(app_name)
        
        if app_architecture:
            all_app_architecture[app_name] = app_architecture
            update_analysis_file_with_architecture(app_name, app_architecture)
            update_analysis_file_with_timeline(app_name, app_architecture)
    
    # Save all architecture data to JSON file
    with open(ANALYSIS_DIR / "app_architecture_data.json", 'w', encoding='utf-8') as f:
        json.dump(all_app_architecture, f, indent=2)
    
    print("Architecture analysis complete. Data saved to analysis/app_architecture_data.json")

if __name__ == "__main__":
    main() 