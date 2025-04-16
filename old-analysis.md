# Technical Debt Analysis Report

## Executive Summary

This analysis identifies significant technical debt in the Django application, which appears to be a system for tracking and managing operations related to human trafficking prevention. The codebase exhibits several concerning patterns: permissions management is duplicated across model definitions, there's excessive coupling between views and business logic, and the application lacks a service layer. The models are overly complex with numerous boolean fields for permissions rather than using Django's built-in permissions system. API endpoints are numerous and poorly organized, suggesting organic growth without architectural planning. Authentication is handled through multiple mechanisms (Django authentication, Auth0, tokens) without clear separation of concerns. The budget app contains excessive business logic in models with numerous calculation methods, while the export_import module performs complex ETL operations with little standardization. The legal app implements a redundant inheritance pattern rather than using Django's standard capabilities. The application would benefit from refactoring to introduce a proper service layer, consolidate permission management, improve API organization, modernize authentication handling, extract business logic from models, and introduce type hints across the codebase.

## Table of Contents

- [Technical Debt Analysis Report](#technical-debt-analysis-report)
  - [Executive Summary](#executive-summary)
  - [Table of Contents](#table-of-contents)
  - [Analysis by Django App](#analysis-by-django-app)
    - [Accounts App](#accounts-app)
    - [REST API](#rest-api)
    - [Data Entry App](#data-entry-app)
    - [Budget App](#budget-app)
    - [Export Import App](#export-import-app)
    - [Legal App](#legal-app)
    - [Settings and Configuration](#settings-and-configuration)
  - [Project-Wide Issues](#project-wide-issues)
    - [Architecture Concerns](#architecture-concerns)
    - [Code Quality Issues](#code-quality-issues)
    - [Django-Specific Issues](#django-specific-issues)
    - [Testing Gaps](#testing-gaps)
    - [Performance Bottlenecks](#performance-bottlenecks)
    - [Security Vulnerabilities](#security-vulnerabilities)
    - [Maintainability Issues](#maintainability-issues)
    - [Deployment and Infrastructure Concerns](#deployment-and-infrastructure-concerns)
  - [Prioritized Issues](#prioritized-issues)
  - [Implementation Timeline](#implementation-timeline)
    - [Short-term Fixes (1-2 sprints)](#short-term-fixes-1-2-sprints)
    - [Medium-term Improvements (1-2 quarters)](#medium-term-improvements-1-2-quarters)
    - [Long-term Strategic Refactoring (6+ months)](#long-term-strategic-refactoring-6-months)

## Analysis by Django App

### Accounts App

#### Code Quality Issues

1. **Duplicated Permission Fields** - Severity: High, Effort: Medium
   
   The `DefaultPermissionsSet` and `Account` models have an identical set of permission boolean fields duplicated between them:

   ```python
   # In DefaultPermissionsSet
   permission_irf_view = models.BooleanField(default=False)
   permission_irf_add = models.BooleanField(default=False)
   # ... 20+ more permission fields
   
   # Almost identical in Account model
   permission_irf_view = models.BooleanField(default=False)
   permission_irf_add = models.BooleanField(default=False)
   # ... 20+ more permission fields
   ```

   This creates maintenance challenges as any new permission must be added in multiple places.

2. **Outdated Python 2 Compatibility Methods** - Severity: Medium, Effort: Small
   
   The models use `__unicode__` methods instead of the Python 3 standard `__str__`:

   ```python
   def __unicode__(self):
       return self.name
   ```

3. **Lack of Type Hints** - Severity: Medium, Effort: Medium
   
   No type hints are used anywhere in the codebase, making it harder to understand function signatures and return types.

4. **Complex Authentication Flow** - Severity: High, Effort: Large
   
   The application mixes multiple authentication methods (Django's built-in, custom tokens, and Auth0) without clear boundaries:

   ```python
   class ObtainExpiringAuthToken(ObtainAuthToken):
       model = ExpiringToken
       
       def post(self, request):
           # Custom token generation
           # ...
   ```

#### Architecture Concerns

1. **Fat Models** - Severity: High, Effort: Large
   
   The `Account` model has business logic that should be in a service layer:

   ```python
   def email_user(self, template, alert, context={}):
       context['site'] = settings.SITE_DOMAIN
       context['account'] = self
       context['alert'] = alert
       send_templated_mail(
           template_name=template,
           from_email=settings.ADMIN_EMAIL_SENDER,
           recipient_list=[self.email],
           context=context
       )
   ```

2. **Permission Management Anti-pattern** - Severity: High, Effort: Large
   
   Instead of using Django's permission system, the application has implemented a custom boolean field-based system that's duplicated across models.

### REST API

#### Code Quality Issues

1. **Monolithic URLs File** - Severity: High, Effort: Medium
   
   The `urls.py` file is over 200 lines long with more than 100 URL patterns defined in one place:

   ```python
   urlpatterns = [
       # Data Entry App
       # Addresses
       re_path(r'^address1/$', Address1ViewSet.as_view(list), name='Address1'),
       re_path(r'^address1/all/$', Address1ViewSet.as_view({'get': 'list_all'}), name='Address1all'),
       # ... 100+ more URLs
   ]
   ```

   This makes maintenance difficult and indicates poor separation of concerns.

2. **Inconsistent URL Pattern Style** - Severity: Medium, Effort: Medium
   
   The API uses a mix of URL styles, sometimes using trailing slashes, sometimes not:

   ```python
   re_path(r'^address1/$', Address1ViewSet.as_view(list), name='Address1'),
   re_path(r'^forms/config/(?P<form_name>\w+)/$', FormViewSet.as_view({'get':'form_config'}), name='formConfig'),
   re_path(r'^cif/(?P<station_id>\d+)/(?P<pk>\d+)', CifFormViewSet.as_view({'get': 'my_retrieve', 'put': 'update'}), name='cifDetail'),
   ```

#### Architecture Concerns

1. **API Versioning Missing** - Severity: High, Effort: Large
   
   The API lacks versioning, making it difficult to evolve the API while maintaining backward compatibility.

2. **Inconsistent View Naming** - Severity: Medium, Effort: Medium
   
   Some views follow REST conventions, others have custom method names:

   ```python
   # Standard REST methods
   def retrieve(self, request):
       # ...
   
   # Custom method names
   def my_retrieve(self, request):
       # ...
   ```

### Data Entry App

Based on imported views in `rest_api/urls.py`, the data entry app appears to handle a significant portion of the application's business logic:

#### Architecture Concerns

1. **Excessive View Responsibilities** - Severity: High, Effort: Large
   
   Views like `InterceptionRecordViewSet`, `VictimInterviewViewSet`, and many others are imported from `dataentry.views`, suggesting these views handle both data presentation and business logic.

2. **Form-focused Instead of Domain-focused** - Severity: High, Effort: Large
   
   The application appears to be structured around forms (`IrfFormViewSet`, `CifFormViewSet`, etc.) rather than domain concepts, leading to a form-driven architecture instead of a domain-driven one.

### Budget App

#### Code Quality Issues

1. **Massive Model Class** - Severity: High, Effort: Large

   The `BorderStationBudgetCalculation` model is nearly 800 lines long with dozens of fields and calculation methods all within the model class:

   ```python
   class BorderStationBudgetCalculation(models.Model):
       # 30+ field definitions
       # 25+ calculation methods
       
       def staff_project_items_total(self, the_type, project):
           items = self.staffbudgetitem_set.filter(type_name=the_type,work_project=project).exclude(cost__isnull=True)
           return sum(item.cost for item in items)
       
       def administration_total(self):
           total = 0
           total += self.administration_intercepts_total()
           total += self.administration_meetings_total()
           total += self.travel_manager_chair_total()
           total += self.communication_manager_chair_total();
           return total + self.administration_extra_items_total()
       
       # Many more calculation methods...
   ```

2. **Magic Numbers** - Severity: Medium, Effort: Medium

   The budget models use numerous magic numbers for constants instead of using enumerations or named constants:

   ```python
   class BorderStationBudgetCalculation(models.Model):
       TRAVEL = 1
       MISCELLANEOUS = 2
       AWARENESS = 3
       POTENTIAL_VICTIM_CARE = 5
       COMMUNICATION = 7
       # ...
   ```

   There are gaps in the numbering (no 4 or 6) which suggests removed categories that could cause issues.

#### Architecture Concerns

1. **Business Logic in Models** - Severity: High, Effort: Large

   The budget app places all business logic directly in model methods rather than in a service layer:

   ```python
   def food_and_gas_intercepted_girls_total(self):
       return self.number_of_intercepted_pvs * self.food_per_pv_amount * self.number_of_pv_days
   
   def food_and_gas_limbo_girls_total(self):
       return self.limbo_girls_multiplier * self.other_project_items_total(self.LIMBO, self.border_station)
   ```

2. **Complex Data Relationships** - Severity: High, Effort: Medium

   The budget models have complex interrelationships that could lead to performance issues:

   ```python
   def staff_salary_and_benefits_total(self, project):
       total = sum([staff.cost for staff in self.staffbudgetitem_set.filter(work_project=project).
                  exclude(cost__isnull=True).exclude(type_name='Travel').exclude(type_name='Deductions')])
       total -= self.staff_salary_and_benefits_deductions(project)
       return total
   ```

   This method performs multiple database queries inside what could be a loop, potentially causing N+1 query problems.

### Export Import App

#### Code Quality Issues

1. **Complex Data Transformation Logic** - Severity: High, Effort: Large

   The export_import app contains complex ETL (Extract, Transform, Load) logic with minimal abstraction or standardization:

   ```python
   # in irf_io.py
   irf_data = [
       CopyCsvField("irf_number", "IRF Number", False),
       BorderStationExportOnlyCsv("station_name", "Station", "irf_number"),
       DateTimeCsvField("date_time_of_interception", "Date/Time of Interception"),
       # 100+ more field mappings
   ]
   ```

2. **Brittle Field Mappings** - Severity: High, Effort: Medium

   The export and import mechanisms rely on direct field mappings that would break if the underlying data models change:

   ```python
   MapFieldCsv("Noticed", "How Was Interception Made",
           {
               "Interception made as a result of a contact": "contact_noticed",
               "Interception made as a result of staff": "staff_noticed",
               "Unknown": MapFieldCsv.set_no_field
           }),
   ```

#### Architecture Concerns

1. **Lack of Consistency Across Import/Export** - Severity: Medium, Effort: Large

   Different forms (IRF, VIF, etc.) have their own import/export mechanisms with duplicated code patterns:

   ```python
   # Files with similar patterns but different implementations:
   # - irf_io.py
   # - vif_io.py
   # - mdf_io.py
   # - trafficker_io.py
   # etc.
   ```

2. **Direct SQL Dependencies** - Severity: Medium, Effort: Medium

   The import/export code depends directly on database structure, making schema changes risky:

   ```python
   def import_irf_row(irfDict):
       # Logic directly bound to database structure
       # ...
   ```

### Legal App

#### Code Quality Issues

1. **Redundant Inheritance Pattern** - Severity: Medium, Effort: Medium

   The legal app uses a custom inheritance pattern with `BaseForm` and `BaseCard` instead of leveraging Django's built-in inheritance capabilities:

   ```python
   class LegalCharge(BaseForm):
       # Fields and methods...
   
   class CourtCase(BaseCard):
       # Fields and methods...
   ```

2. **String Field Length Inconsistency** - Severity: Low, Effort: Small

   String field lengths are inconsistent throughout the models:

   ```python
   class LegalCharge(BaseForm):
       legal_charge_number = models.CharField(max_length=20, unique=True)
       source = models.CharField(max_length=127, null=True)
       location = models.CharField(max_length=255, null=True)
       # ...
   ```

   Some fields use 20, others 127, 126, or 255 with no clear pattern.

#### Architecture Concerns

1. **Manual Foreign Key Management** - Severity: Medium, Effort: Medium

   The models include manual handling of relationships that should use Django's built-in features:

   ```python
   class LegalChargeSuspectCharge(BaseCard):
       # Manual comment about relationship management
       # Current framework will not support storing a foreign key to CourtCase or LegalChargeSuspect.
       # We can use the sequence number from the court case to identify the corresponding CourtCase
       # and the SF reference to identify the LegalChargeSuspect
       
       court_cases = models.CharField(max_length=255, null=True) # delimited list of CourtCase sequence numbers
   ```

   String-based lists in fields like `court_cases` instead of proper relationships.

2. **Redundant Parent Setting** - Severity: Medium, Effort: Small

   Models include redundant `set_parent` methods instead of using Django's relationship features:

   ```python
   def set_parent(self, the_parent):
       self.legal_charge = the_parent
   ```

### Settings and Configuration

#### Code Quality Issues

1. **Environment Variable Management** - Severity: Medium, Effort: Small
   
   The settings use direct environment variable access without validation:

   ```python
   SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
   SITE_DOMAIN = os.environ['SITE_DOMAIN']
   CLIENT_DOMAIN = os.environ['CLIENT_DOMAIN']
   ```

   This approach can lead to crashes if variables are missing rather than providing useful error messages.

2. **Commented-Out Code** - Severity: Low, Effort: Small
   
   The settings file contains significant commented-out sections:

   ```python
   # We are no longer backing up Linux, we are copying files from one Azure blob storage to another blob storage
   # "mediabackups": {
   #     "BACKEND": "storages.backends.azure_storage.AzureStorage",
   #     # ... more commented code
   # },
   ```

## Project-Wide Issues

### Architecture Concerns

1. **Missing Service Layer** - Severity: High, Effort: Large
   
   Business logic is spread across models and views rather than being centralized in a service layer. This makes the code harder to test, maintain, and evolve.

2. **Improper Separation of Concerns** - Severity: High, Effort: Large
   
   Views often handle business logic, authentication, permission checks, and presentation concerns all at once.

3. **Inconsistent Design Patterns** - Severity: Medium, Effort: Large
   
   The application mixes different architectural approaches without clear boundaries or reasons.

### Code Quality Issues

1. **Duplicate Code** - Severity: High, Effort: Medium
   
   Permission-related code is duplicated across models and views.

2. **Lack of Type Annotations** - Severity: Medium, Effort: Medium
   
   The codebase would benefit from Python type hints to improve developer experience and catch type-related errors early.

3. **Inconsistent Naming** - Severity: Medium, Effort: Medium
   
   The codebase has inconsistent naming patterns, with some classes following Django conventions and others using custom approaches.

### Django-Specific Issues

1. **Custom Permission System** - Severity: High, Effort: Large
   
   Instead of using Django's built-in permission system, a custom system using boolean fields is implemented.

2. **Fat Models and Views** - Severity: High, Effort: Large
   
   Models and views contain business logic that should be in a service layer.

3. **Inconsistent URL Patterns** - Severity: Medium, Effort: Medium
   
   URL routes are inconsistently structured, sometimes with trailing slashes, sometimes without.

### Testing Gaps

Without direct access to test files, we can infer:

1. **Difficulty Testing Business Logic** - Severity: High, Effort: Large
   
   With business logic embedded in views and models, testing it in isolation is likely difficult.

2. **Potential Authentication Testing Issues** - Severity: High, Effort: Medium
   
   The mixture of authentication methods likely complicates testing.

### Performance Bottlenecks

1. **Potential N+1 Query Problems** - Severity: High, Effort: Medium
   
   The complex model relationships suggest potential for N+1 query issues, especially with multiple foreign keys and many-to-many relationships.

2. **Missing Database Indexes** - Severity: Medium, Effort: Small
   
   Models don't explicitly define indexes on fields likely to be queried frequently.

### Security Vulnerabilities

1. **Multiple Authentication Mechanisms** - Severity: High, Effort: Large
   
   Using multiple authentication systems (Django, Auth0, custom tokens) increases the attack surface.

2. **Direct Environment Variable Access** - Severity: Medium, Effort: Small
   
   Accessing environment variables directly without validation could lead to runtime errors.

### Maintainability Issues

1. **Outdated Compatibility Code** - Severity: Medium, Effort: Small
   
   `__unicode__` methods suggest the codebase was originally written for Python 2 and partially migrated to Python 3.

2. **Long URL Routing File** - Severity: Medium, Effort: Medium
   
   The URLs configuration file is over 200 lines long, making it difficult to maintain.

### Deployment and Infrastructure Concerns

1. **Azure Blob Storage Configuration** - Severity: Medium, Effort: Medium
   
   The application has complex Azure Blob Storage configuration with commented-out sections suggesting previous iterations:

   ```python
   STORAGES = {
       "default": {
           # "BACKEND": "storages.backends.azure_storage.AzureStorage",
           "BACKEND": "azure_storage.azure_storage_with_reverse_proxy.AzureStorageWithReverseProxy",
           # ... complex configuration
       },
   }
   ```

## Prioritized Issues

| Issue | Severity | Effort | Impact |
|-------|----------|--------|--------|
| Missing Service Layer | High | Large | Creates maintenance challenges, hinders testing, couples components |
| Business Logic in Models (Budget App) | High | Large | Makes code harder to understand, test, and maintain |
| Custom Permission System | High | Large | Increases code complexity, creates duplication, harder to maintain |
| Complex Data Transformation (Export/Import) | High | Large | Makes data flow hard to understand and maintain |
| Fat Models and Views | High | Large | Makes code harder to test, maintain, and understand |
| Duplicated Permission Fields | High | Medium | Increases risk of inconsistencies and errors when updating |
| Monolithic URLs File | High | Medium | Makes route management difficult, indicates poor organization |
| Complex Authentication Flow | High | Large | Increases security risks, complicates testing |
| Potential N+1 Query Problems | High | Medium | Could cause performance issues, especially as data grows |
| API Versioning Missing | High | Large | Makes API evolution difficult without breaking clients |
| Outdated Python 2 Compatibility | Medium | Small | Technical debt indicating incomplete migration |
| Environment Variable Handling | Medium | Small | Could cause runtime crashes rather than helpful errors |

## Implementation Timeline

### Short-term Fixes (1-2 sprints)

1. **Update Python 2 Compatibility Methods**
   
   Replace `__unicode__` with `__str__` methods in models:
   
   ```python
   # Replace this
   def __unicode__(self):
       return self.name
   
   # With this
   def __str__(self):
       return self.name
   ```

2. **Improve Environment Variable Handling**
   
   Use get with default or validation:
   
   ```python
   # Replace this
   SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
   
   # With this
   SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
   if not SECRET_KEY:
       raise ImproperlyConfigured("DJANGO_SECRET_KEY environment variable is required")
   ```

3. **Add Database Indexes**
   
   Add indexes to frequently queried fields:
   
   ```python
   class Account(AbstractBaseUser, PermissionsMixin):
       email = models.EmailField(max_length=255, unique=True, db_index=True)
       # ...
   ```

4. **Clean Up Commented Code**
   
   Remove commented-out code blocks that are no longer needed.

### Medium-term Improvements (1-2 quarters)

1. **Break Up Monolithic URLs File**
   
   Restructure URL patterns by app and include them in the main `urls.py`:
   
   ```python
   # In each app's urls.py:
   app_patterns = [
       re_path(r'^endpoint/$', SomeViewSet.as_view(list), name='endpoint'),
       # ...
   ]
   
   # In main urls.py:
   urlpatterns = [
       path('api/accounts/', include('accounts.urls')),
       path('api/dataentry/', include('dataentry.urls')),
       # ...
   ]
   ```

2. **Introduce API Versioning**
   
   Add API versioning to routes:
   
   ```python
   urlpatterns = [
       path('api/v1/', include('api.v1.urls')),
       # Future version
       # path('api/v2/', include('api.v2.urls')),
   ]
   ```

3. **Add Type Hints**
   
   Introduce type hints to improve code quality:
   
   ```python
   # Replace this
   def get_form_versions(self, request, form_id, country_id):
       # ...
   
   # With this
   def get_form_versions(self, request: Request, form_id: int, country_id: int) -> Response:
       # ...
   ```

4. **Address N+1 Query Problems**
   
   Use `select_related` and `prefetch_related` appropriately:
   
   ```python
   # Replace this
   accounts = Account.objects.all()
   
   # With this
   accounts = Account.objects.select_related('user_designation').all()
   
   # In Budget app
   def staff_salary_and_benefits_total(self, project):
       # Replace this pattern:
       total = sum([staff.cost for staff in self.staffbudgetitem_set.filter(...)])
       
       # With this to reduce DB calls:
       staff_items = self.staffbudgetitem_set.filter(...).values_list('cost', flat=True)
       total = sum(staff_items)
   ```

### Long-term Strategic Refactoring (6+ months)

1. **Introduce a Service Layer**
   
   Create a proper service layer to encapsulate business logic:
   
   ```python
   # accounts/services.py
   class AccountService:
       @staticmethod
       def send_activation_email(account: Account, email_type: str) -> None:
           # Logic moved from model to service
           
   # In views
   def post(self, request, pk=None):
       account = get_object_or_404(Account, pk=pk)
       AccountService.send_activation_email(account, 'activate')
       return Response(True)
   
   # For Budget app
   # budget/services.py
   class BudgetCalculationService:
       @staticmethod
       def calculate_administration_total(budget_calculation):
           # Move logic from model to service
   ```

2. **Migrate to Django's Permission System**
   
   Replace custom permission booleans with Django's permission system:
   
   ```python
   # Create proper Django permissions
   class Meta:
       permissions = (
           ("view_irf", "Can view IRF"),
           ("add_irf", "Can add IRF"),
           # ...
       )
   
   # Use Django's permission checks
   @permission_required('app.view_irf')
   def view_irf(request):
       # ...
   ```

3. **Consolidate Authentication Approaches**
   
   Choose one primary authentication method and refactor:
   
   ```python
   # If choosing Django REST Framework's token auth:
   REST_FRAMEWORK = {
       'DEFAULT_AUTHENTICATION_CLASSES': [
           'rest_framework.authentication.TokenAuthentication',
       ],
       # ...
   }
   ```

4. **Implement Domain-Driven Design**
   
   Restructure apps around domain concepts rather than forms or technical concerns:
   
   ```
   trafficking_prevention/
     interception/  # Domain concept
       services.py
       models.py
       views.py
     victim_support/  # Domain concept
       services.py
       models.py
       views.py
   ```

5. **Standardize Import/Export**
   
   Create a standard framework for data import/export:
   
   ```python
   # Create a base class for all import/export operations
   class DataImportExport:
       def __init__(self, model_class):
           self.model_class = model_class
       
       def get_field_mapping(self):
           # Must be implemented by subclasses
           pass
       
       def export_data(self, queryset):
           # Standardized export logic
           
       def import_data(self, data):
           # Standardized import logic
   ```

6. **Adopt GraphQL for Complex API Needs**
   
   Consider GraphQL for complex, nested data needs:
   
   ```python
   # schema.py example
   class InterceptionType(DjangoObjectType):
       class Meta:
           model = Interception
           
   class Query(graphene.ObjectType):
       interception = graphene.Field(InterceptionType, id=graphene.ID())
       
       def resolve_interception(self, info, id):
           return Interception.objects.get(pk=id)
   