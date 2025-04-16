#!/usr/bin/env python3
"""
Identify code quality issues in Django applications.
This script helps detect potential technical debt and code quality problems.
"""

import os
import re
import json
from pathlib import Path
import ast
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

class CodeComplexityVisitor(ast.NodeVisitor):
    """AST visitor to measure code complexity."""
    
    def __init__(self):
        self.complexity = {}
        self.current_function = None
        self.line_counts = defaultdict(int)
        self.max_line_length = defaultdict(int)
        self.current_file = None
        
    def visit_FunctionDef(self, node):
        prev_function = self.current_function
        self.current_function = node.name
        
        # Count lines of code in function
        start_line = node.lineno
        end_line = max(line for line in [getattr(n, 'lineno', 0) for n in ast.walk(node)] if line > 0)
        
        # Calculate cyclomatic complexity
        conditions = 0
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For)):
                conditions += 1
            elif isinstance(child, ast.BoolOp) and isinstance(child.op, ast.And):
                conditions += len(child.values) - 1
            
        self.complexity[node.name] = {
            'cyclomatic_complexity': conditions + 1,  # Base complexity of 1
            'line_count': end_line - start_line + 1,
            'start_line': start_line,
            'end_line': end_line
        }
        
        self.generic_visit(node)
        self.current_function = prev_function
    
    def analyze_file(self, file_path):
        """Analyze a Python file for complexity and code smells."""
        self.current_file = file_path
        self.complexity = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Measure line lengths
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    self.line_counts[len(line)] += 1
                    self.max_line_length[i+1] = len(line)
                
                # Parse AST and visit nodes
                tree = ast.parse(content)
                self.visit(tree)
                
                return {
                    'file': str(file_path),
                    'functions': self.complexity,
                    'line_count': len(lines),
                    'max_line_length': max(self.max_line_length.values()) if self.max_line_length else 0,
                    'long_lines': sum(1 for length in self.max_line_length.values() if length > 100)
                }
        except SyntaxError as e:
            return {
                'file': str(file_path),
                'error': f"Syntax error in file: {e}",
                'line_count': 0,
                'max_line_length': 0,
                'long_lines': 0
            }
        except Exception as e:
            return {
                'file': str(file_path),
                'error': f"Error analyzing file: {e}",
                'line_count': 0,
                'max_line_length': 0,
                'long_lines': 0
            }

def find_code_smells(content, file_path):
    """Identify potential code smells in the content."""
    issues = []
    
    # Check for hardcoded secrets
    patterns = {
        "Hardcoded Secret": [
            r'password\s*=\s*["\'](?![\{\}]).+["\']',
            r'secret\s*=\s*["\'](?![\{\}]).+["\']',
            r'SECRET_KEY\s*=\s*["\'](?![\{\}]).+["\']',
            r'api_key\s*=\s*["\'](?![\{\}]).+["\']',
        ],
        "TODO/FIXME Comment": [
            r'#\s*(TODO|FIXME)',
            r"'''\s*(TODO|FIXME)",
            r'"""\s*(TODO|FIXME)',
        ],
        "Potentially Risky": [
            r'eval\(',
            r'exec\(',
            r'os\.system\(',
            r'subprocess\.call\(',
            r'subprocess\.Popen\(',
            r'__import__\(',
        ],
        "Django Anti-patterns": [
            r'raw_id_fields',
            r'raw\(\s*[\'"].+[\'"]\s*\)',
            r'\.extra\(',
            r'\.values\(',
            r'select_related\(\s*\)',  # Empty select_related
        ],
        "Magic Numbers": [
            r'[\s\(=\[,\+\-\*/]\d{4,}[\s\),\.\+\-\*/;]',  # Numbers with 4+ digits
        ]
    }
    
    lines = content.split('\n')
    
    for category, pattern_list in patterns.items():
        for pattern in pattern_list:
            for i, line in enumerate(lines):
                if re.search(pattern, line):
                    issues.append({
                        'category': category,
                        'pattern': pattern,
                        'line': i + 1,
                        'content': line.strip(),
                        'file': file_path
                    })
    
    # Check for duplicate code blocks (3+ lines)
    code_blocks = {}
    for i in range(len(lines) - 2):
        if len(lines[i].strip()) + len(lines[i+1].strip()) + len(lines[i+2].strip()) > 10:  # Skip empty lines
            block = '\n'.join(lines[i:i+3])
            if block in code_blocks:
                issues.append({
                    'category': 'Duplicate Code',
                    'pattern': 'Duplicate code block',
                    'line': i + 1,
                    'content': f"Same as lines {code_blocks[block]+1}-{code_blocks[block]+3}",
                    'file': file_path
                })
            else:
                code_blocks[block] = i
    
    return issues

def analyze_app_for_issues(app_name):
    """Analyze an app for code quality issues."""
    app_path = APP_DIR / app_name
    
    if not app_path.exists():
        print(f"App directory not found: {app_path}")
        return None
    
    results = {
        "app_name": app_name,
        "complexity_metrics": [],
        "code_smells": [],
        "high_complexity_functions": [],
        "large_files": []
    }
    
    # Find all Python files in the app
    for root, dirs, files in os.walk(app_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, APP_DIR)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Analyze code complexity
                    visitor = CodeComplexityVisitor()
                    complexity_data = visitor.analyze_file(file_path)
                    results["complexity_metrics"].append(complexity_data)
                    
                    # Find code smells
                    smells = find_code_smells(content, rel_path)
                    results["code_smells"].extend(smells)
                    
                    # Identify high complexity functions
                    for func_name, func_data in complexity_data.get('functions', {}).items():
                        if func_data.get('cyclomatic_complexity', 0) > 10:
                            results["high_complexity_functions"].append({
                                "file": rel_path,
                                "function": func_name,
                                "complexity": func_data.get('cyclomatic_complexity', 0),
                                "lines": func_data.get('line_count', 0),
                                "start_line": func_data.get('start_line', 0),
                                "end_line": func_data.get('end_line', 0)
                            })
                    
                    # Identify large files
                    if complexity_data.get('line_count', 0) > 300:
                        results["large_files"].append({
                            "file": rel_path,
                            "line_count": complexity_data.get('line_count', 0),
                            "long_lines": complexity_data.get('long_lines', 0)
                        })
                    
                except Exception as e:
                    print(f"Error analyzing {file_path}: {e}")
    
    # Sort high complexity functions by complexity (descending)
    results["high_complexity_functions"] = sorted(
        results["high_complexity_functions"], 
        key=lambda x: x["complexity"], 
        reverse=True
    )
    
    # Sort large files by line count (descending)
    results["large_files"] = sorted(
        results["large_files"], 
        key=lambda x: x["line_count"], 
        reverse=True
    )
    
    return results

def generate_code_issues_section(app_analysis):
    """Generate markdown section for code quality issues."""
    if not app_analysis:
        return "No code quality issues data available."
    
    markdown = "## Application-Specific Issues\n\n"
    
    # High complexity functions
    if app_analysis["high_complexity_functions"]:
        markdown += "### High Complexity Functions\n\n"
        markdown += "| File | Function | Complexity | Lines |\n"
        markdown += "|------|----------|------------|-------|\n"
        
        for func in app_analysis["high_complexity_functions"]:
            markdown += f"| {func['file']} | `{func['function']}` | {func['complexity']} | {func['lines']} |\n"
        
        markdown += "\n"
    
    # Large files
    if app_analysis["large_files"]:
        markdown += "### Large Files\n\n"
        markdown += "| File | Lines | Long Lines (>100 chars) |\n"
        markdown += "|------|-------|------------------------|\n"
        
        for file in app_analysis["large_files"]:
            markdown += f"| {file['file']} | {file['line_count']} | {file['long_lines']} |\n"
        
        markdown += "\n"
    
    # Code smells by category
    if app_analysis["code_smells"]:
        markdown += "### Code Smells\n\n"
        
        # Group code smells by category
        smells_by_category = defaultdict(list)
        for smell in app_analysis["code_smells"]:
            smells_by_category[smell["category"]].append(smell)
        
        for category, smells in smells_by_category.items():
            markdown += f"#### {category}\n\n"
            markdown += "| File | Line | Issue |\n"
            markdown += "|------|------|-------|\n"
            
            # Limit to 10 examples per category to avoid excessive length
            for smell in smells[:10]:
                content = smell["content"]
                if len(content) > 60:
                    content = content[:57] + "..."
                markdown += f"| {smell['file']} | {smell['line']} | `{content}` |\n"
            
            if len(smells) > 10:
                markdown += f"| ... | ... | _{len(smells) - 10} more issues of this type_ |\n"
            
            markdown += "\n"
    
    return markdown

def update_analysis_file_with_issues(app_name, app_analysis):
    """Update the analysis markdown file with code quality issues."""
    analysis_path = ANALYSIS_DIR / f"{app_name}.md"
    
    if not analysis_path.exists():
        print(f"Analysis file not found: {analysis_path}")
        return
    
    with open(analysis_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace issues section
    issues_section = generate_code_issues_section(app_analysis)
    content = re.sub(
        r"## Application-Specific Issues\n\n\[Detailed list of application-specific issues\]",
        issues_section,
        content
    )
    
    # Write updated content back to file
    with open(analysis_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Updated issues in analysis file: {analysis_path}")

def generate_prioritized_issues(app_analysis):
    """Generate the prioritized issues section based on analysis."""
    markdown = "## Prioritized Issues\n\n"
    
    issues = []
    
    # Add high complexity functions as high severity issues
    for func in app_analysis["high_complexity_functions"][:5]:  # Limit to top 5
        issues.append({
            "issue": f"High complexity in `{func['function']}` ({func['file']})",
            "severity": "High" if func["complexity"] > 15 else "Medium",
            "effort": "Medium" if func["lines"] > 50 else "Small",
            "impact": "Code maintainability and testability",
            "description": (
                f"Function has cyclomatic complexity of {func['complexity']} across {func['lines']} lines. "
                f"Consider refactoring into smaller functions with clear responsibilities. "
                f"Located at lines {func['start_line']}-{func['end_line']}."
            )
        })
    
    # Add large files as medium severity issues
    for file in app_analysis["large_files"][:3]:  # Limit to top 3
        issues.append({
            "issue": f"Overly large file {file['file']}",
            "severity": "Medium",
            "effort": "Large",
            "impact": "Code organization and maintainability",
            "description": (
                f"File has {file['line_count']} lines with {file['long_lines']} lines exceeding 100 characters. "
                f"Consider breaking into smaller modules with focused responsibilities."
            )
        })
    
    # Add selected code smells based on category severity
    high_priority_categories = ["Hardcoded Secret", "Potentially Risky", "Django Anti-patterns"]
    smells_by_category = defaultdict(list)
    
    for smell in app_analysis["code_smells"]:
        smells_by_category[smell["category"]].append(smell)
    
    for category in high_priority_categories:
        if category in smells_by_category:
            issues.append({
                "issue": f"Multiple {category} instances",
                "severity": "High" if category in ["Hardcoded Secret", "Potentially Risky"] else "Medium",
                "effort": "Medium",
                "impact": "Security and code quality",
                "description": (
                    f"Found {len(smells_by_category[category])} instances of {category}. "
                    f"These should be addressed to improve code quality and security."
                )
            })
    
    # Other code smell categories as lower priority
    for category, smells in smells_by_category.items():
        if category not in high_priority_categories and len(smells) > 5:
            issues.append({
                "issue": f"Multiple {category} instances",
                "severity": "Low",
                "effort": "Small" if category == "TODO/FIXME Comment" else "Medium",
                "impact": "Code quality and maintainability",
                "description": (
                    f"Found {len(smells)} instances of {category}. "
                    f"Consider addressing these to improve code quality."
                )
            })
    
    # Generate the markdown table
    if issues:
        markdown += "| Issue | Severity | Effort | Impact | Description |\n"
        markdown += "|-------|----------|--------|--------|-------------|\n"
        
        for issue in issues:
            markdown += (
                f"| {issue['issue']} | {issue['severity']} | {issue['effort']} | "
                f"{issue['impact']} | {issue['description']} |\n"
            )
    else:
        markdown += "No significant issues identified for prioritization.\n"
    
    return markdown

def update_analysis_file_with_prioritized_issues(app_name, app_analysis):
    """Update the analysis markdown file with prioritized issues."""
    analysis_path = ANALYSIS_DIR / f"{app_name}.md"
    
    if not analysis_path.exists():
        print(f"Analysis file not found: {analysis_path}")
        return
    
    with open(analysis_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace prioritized issues section
    prioritized_section = generate_prioritized_issues(app_analysis)
    content = re.sub(
        r"## Prioritized Issues\n\n\| Issue \| Severity \| Effort \| Impact \| Description \|\n\|\-+\|\-+\|\-+\|\-+\|\-+\|\n\| Issue 1 \| High/Medium/Low \| Small/Medium/Large \| Description of impact \| Detailed description with recommendation \|",
        prioritized_section,
        content
    )
    
    # Write updated content back to file
    with open(analysis_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Updated prioritized issues in analysis file: {analysis_path}")

def main():
    """Main function to identify code issues in all Django apps."""
    os.makedirs(ANALYSIS_DIR, exist_ok=True)
    
    # Save full analysis data as JSON for reference
    all_app_issues = {}
    
    for app_name in APPS:
        print(f"Analyzing code issues in {app_name}...")
        app_issues = analyze_app_for_issues(app_name)
        
        if app_issues:
            all_app_issues[app_name] = app_issues
            update_analysis_file_with_issues(app_name, app_issues)
            update_analysis_file_with_prioritized_issues(app_name, app_issues)
    
    # Save all issues data to JSON file
    with open(ANALYSIS_DIR / "app_issues_data.json", 'w', encoding='utf-8') as f:
        # Convert defaultdicts to regular dicts for JSON serialization
        json_data = json.dumps(all_app_issues, indent=2, default=lambda x: dict(x) if isinstance(x, defaultdict) else x)
        f.write(json_data)
    
    print("Code issues analysis complete. Data saved to analysis/app_issues_data.json")

if __name__ == "__main__":
    main() 