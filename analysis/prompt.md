Analyze this Django application to identify and prioritize technical debt. Take a systematic approach to analyze each Django application one at a time, thoroughly and in depth. For each application, save the analysis to a separate markdown file named after the application (e.g., accounts.md, budget.md, legal.md) at the project root. Focus on the following aspects:

1. Code Quality Issues:
   - Duplicate code patterns
   - Overly complex functions/methods (high cyclomatic complexity)
   - Inconsistent coding style
   - Poor naming conventions
   - Magic numbers/strings
   - Lack of type hints where beneficial
   - Missing or inadequate documentation

2. Architecture Concerns:
   - Tight coupling between components
   - Violations of SOLID principles
   - Improper separation of concerns
   - Monolithic structures that could be modularized
   - Inconsistent architectural patterns
   - Missing service layer (business logic in views/models)
   - Lack of domain-driven design principles
   - Fat models/views that should be refactored into services

3. Django-Specific Issues:
   - Django ORM misuse (raw SQL where ORM would be better, or vice versa)
   - Improper use of Django's caching mechanisms
   - Inefficient model relationships and indexing
   - Suboptimal middleware implementation
   - View-based vs class-based view inconsistencies
   - Anti-patterns in URL routing
   - Form validation issues
   - Business logic embedded in views instead of service classes
   - Missing use of Django signals for cross-cutting concerns

4. Testing Gaps:
   - Missing test coverage
   - Brittle tests
   - Lack of unit tests
   - Missing integration tests
   - Test duplication
   - Absence of Django-specific test utilities and fixtures
   - Difficulty testing business logic due to tight coupling with views/models

5. Performance Bottlenecks:
   - N+1 query problems
   - Inefficient database queries
   - Unoptimized loops
   - Memory leaks
   - Synchronous operations that could be async
   - Unoptimized template rendering
   - Missing database indexes

6. Security Vulnerabilities:
   - Insecure direct object references
   - Missing input validation
   - Improper error handling
   - Hardcoded credentials
   - Insecure dependencies
   - CSRF/XSS vulnerabilities
   - Missing permission checks

7. Maintainability Issues:
   - Outdated dependencies
   - Deprecated API usage
   - Legacy code patterns
   - Technical obsolescence
   - Complex configuration
   - Difficulty in introducing new features due to lack of service abstraction

8. Deployment and Infrastructure Concerns:
   - Inadequate containerization
   - Manual deployment steps
   - Environment configuration issues
   - Lack of infrastructure as code
   - Missing or incomplete CI/CD pipelines
   - Suboptimal static file handling

9. Code Metrics to Include:
   - Lines of code per module/app
   - Code churn (frequently modified files)
   - Test coverage percentages
   - Complexity metrics by file
   - Django app dependencies graph
   - Business logic distribution (views vs models vs services)

Analysis Approach for Each Application:
1. Begin with a comprehensive inventory of all files in the application
2. Read and analyze each file in its entirety, not just portions
3. Examine all models, views, forms, serializers, urls, and other relevant files
4. Analyze relationships between files within the application
5. Identify dependencies with other applications
6. Review tests to assess coverage and quality
7. Analyze migrations to understand database schema evolution
8. Review application-specific documentation if available
9. Examine template files if present
10. Analyze static assets and JavaScript if relevant

For each identified issue:
1. Provide a severity rating (High/Medium/Low)
2. Estimate the effort required to fix (Small/Medium/Large)
3. Suggest specific refactoring approaches
4. List any dependencies or prerequisites for fixing
5. Identify potential risks of not addressing the issue

Prioritize the issues based on:
- Impact on system stability
- Impact on development velocity
- Cost of maintenance
- Risk of failure
- Business impact

Format the output in each application-specific markdown file (e.g., accounts.md) as follows:
- Executive summary at the top (maximum 500 words)
- Table of contents with hyperlinks to sections
- File inventory section listing all files analyzed
- Analysis of key components (models, views, etc.)
- Application-specific issues section
- External dependencies and integration points
- Prioritized issues in markdown tables with columns for severity, effort, and impact
- Code snippets formatted with appropriate syntax highlighting
- Implementation timeline section with:
  - Short-term fixes (1-2 sprints)
  - Medium-term improvements (1-2 quarters)
  - Long-term strategic refactoring (6+ months)

After analyzing all applications individually, create a summary file (technical_debt_summary.md) that:
- Provides a high-level overview of technical debt across the entire project
- Identifies patterns that span multiple applications
- Prioritizes issues across the entire codebase
- Suggests a roadmap for addressing technical debt systematically

Each issue should include actionable recommendations with specific code examples where relevant. For service layer implementations, provide example patterns that could be applied to refactor existing code.