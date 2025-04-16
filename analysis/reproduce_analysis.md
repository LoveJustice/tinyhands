# How to Reproduce the Technical Debt Analysis

This guide explains how to reproduce the Django technical debt analysis using the scripts provided in this directory.

## Step 1: Create a New Conversation with Claude

Start a new conversation with Claude and provide the following prompt:

```
I have a Django project that I want to analyze for technical debt. I've already created scripts to help with this analysis. Please help me run these scripts and interpret the results. The scripts are located in the `analysis/scripts` directory.

First, let's look at what scripts are available:

ls -la analysis/scripts/
```

## Step 2: Run the Update Script

Have Claude run the update script to ensure all paths are correctly set:

```
chmod +x analysis/scripts/update_scripts_path.sh
./analysis/scripts/update_scripts_path.sh
```

## Step 3: Run the Analysis Script

Have Claude run the main analysis script:

```
chmod +x analysis/scripts/run_analysis.sh
./analysis/scripts/run_analysis.sh
```

This will execute all the individual analysis steps in sequence:
1. Generate template files
2. Gather basic metrics
3. Identify code quality issues
4. Analyze architecture
5. Generate summaries

## Step 4: Explore the Results

Once the analysis is complete, have Claude help you explore the results:

```
ls -la analysis/*.md
cat analysis/technical_debt_summary.md
```

You can also examine individual application analyses:

```
cat analysis/accounts.md
```

## Step 5: Interpreting the Results

Ask Claude to help interpret the results and provide insights:

```
Based on the technical debt analysis, what are the most critical issues that should be addressed first? Which applications have the most technical debt?
```

## Step 6: Implementing Recommendations

For specific applications, ask Claude for guidance on implementing the recommendations:

```
Based on the analysis of the accounts application, how should we implement the service layer recommendation? Can you provide a detailed plan with example code?
```

## Understanding the Scripts

If you want to understand how the analysis works or customize it:

1. **generate_analysis_files.sh**: Creates template markdown files
2. **analyze_django_apps.py**: Gathers basic metrics (file counts, dependencies)
3. **identify_code_issues.py**: Analyzes code quality (complexity, smells)
4. **analyze_architecture.py**: Identifies architectural issues
5. **generate_summaries.py**: Creates executive summaries

You can ask Claude to explain any specific script:

```
Please explain how the identify_code_issues.py script works. How does it detect code complexity?
```

## Customizing the Analysis

To customize the analysis, ask Claude to modify specific thresholds or criteria:

```
I'd like to adjust the thresholds for file size in identify_code_issues.py. Currently, files over 300 lines are flagged as "large". Can you update the script to use a threshold of 500 lines instead?
```

---

By following these steps, you'll be able to reproduce the technical debt analysis and get meaningful insights about your Django project's codebase. 