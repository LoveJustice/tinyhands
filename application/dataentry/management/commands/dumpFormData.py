import warnings
from collections import OrderedDict

from django.apps import apps
from django.core import serializers
from django.core.management.base import BaseCommand, CommandError
from django.core.management.utils import parse_apps_and_model_labels
from django.db import DEFAULT_DB_ALIAS, router
from django.conf import settings

from dataentry.models.form import FormType

class ProxyModelWarning(Warning):
    pass


class Command(BaseCommand):
    
    def handle(self, *app_labels, **options):
        reference_apps = [
            'dataentry.FormType',
            'dataentry.CategoryType',
            'dataentry.AnswerType',
            'dataentry.FormValidationLevel',
            'dataentry.FormValidationType'
            ]
        form_filtered_apps = [
            'dataentry.Storage',
            'dataentry.Form',
            'dataentry.Category',
            'dataentry.FormCategory',
            'dataentry.Question',
            'dataentry.QuestionLayout',
            'dataentry.QuestionStorage',
            'dataentry.Answer',
            'dataentry.FormValidation',
            'dataentry.FormValidationQuestion',
            'dataentry.ExportImport',
            'dataentry.ExportImportCard',
            'dataentry.ExportImportField',
            'dataentry.GoogleSheetConfig',
            ]
        
        form_data_base = settings.BASE_DIR + '/fixtures/initial-required-data/form_data'
        
        app_labels = reference_apps + form_filtered_apps
        form_types = FormType.objects.filter(tag_enabled = False).values_list('name', flat=True)
        self.dump_set(app_labels, form_types, 'form_data_id', form_data_base + '.json')
        
        app_labels = form_filtered_apps
        form_types = FormType.objects.filter(tag_enabled = True)
        for form_type in form_types:
            self.dump_set(app_labels, [form_type.name], 'form_data_tag', form_data_base + '_' + form_type.name + '.json')
        
        
    
    def dump_set(self, app_labels, form_types, format, output):
        indent = 3
        using = DEFAULT_DB_ALIAS
        excludes = []
        show_traceback = True
        use_natural_foreign_keys = False
        use_natural_primary_keys = False
        use_base_manager = False
        pks = None
        options = {
            'verbosity':0
            }

        if pks:
            primary_keys = [pk.strip() for pk in pks.split(',')]
        else:
            primary_keys = []

        excluded_models, excluded_apps = parse_apps_and_model_labels(excludes)

        if len(app_labels) == 0:
            if primary_keys:
                raise CommandError("You can only use --pks option with one model")
            app_list = OrderedDict(
                (app_config, None) for app_config in apps.get_app_configs()
                if app_config.models_module is not None and app_config not in excluded_apps
            )
        else:
            if len(app_labels) > 1 and primary_keys:
                raise CommandError("You can only use --pks option with one model")
            app_list = OrderedDict()
            for label in app_labels:
                try:
                    app_label, model_label = label.split('.')
                    try:
                        app_config = apps.get_app_config(app_label)
                    except LookupError as e:
                        raise CommandError(str(e))
                    if app_config.models_module is None or app_config in excluded_apps:
                        continue
                    try:
                        model = app_config.get_model(model_label)
                    except LookupError:
                        raise CommandError("Unknown model: %s.%s" % (app_label, model_label))

                    app_list_value = app_list.setdefault(app_config, [])

                    # We may have previously seen a "all-models" request for
                    # this app (no model qualifier was given). In this case
                    # there is no need adding specific models to the list.
                    if app_list_value is not None:
                        if model not in app_list_value:
                            app_list_value.append(model)
                except ValueError:
                    if primary_keys:
                        raise CommandError("You can only use --pks option with one model")
                    # This is just an app - no model qualifier
                    app_label = label
                    try:
                        app_config = apps.get_app_config(app_label)
                    except LookupError as e:
                        raise CommandError(str(e))
                    if app_config.models_module is None or app_config in excluded_apps:
                        continue
                    app_list[app_config] = None

        # Check that the serialization format exists; this is a shortcut to
        # avoid collating all the objects and _then_ failing.
        if format not in serializers.get_public_serializer_formats():
            try:
                serializers.get_serializer(format)
            except serializers.SerializerDoesNotExist:
                pass

            raise CommandError("Unknown serialization format: %s" % format)

        def get_objects(count_only=False):
            """
            Collate the objects to be serialized. If count_only is True, just
            count the number of objects to be serialized.
            """
            models = serializers.sort_dependencies(app_list.items())
            for model in models:
                if model in excluded_models:
                    continue
                if model._meta.proxy and model._meta.proxy_for_model not in models:
                    warnings.warn(
                        "%s is a proxy model and won't be serialized." % model._meta.label,
                        category=ProxyModelWarning,
                    )
                if not model._meta.proxy and router.allow_migrate_model(using, model):
                    if use_base_manager:
                        objects = model._base_manager
                    else:
                        objects = model._default_manager
                    
                    if getattr(model, 'get_objects_by_form_type', None) is not None:
                        queryset = model.get_objects_by_form_type(form_types)
                    else:
                        queryset = objects.using(using).order_by(model._meta.pk.name)
                    if primary_keys:
                        queryset = queryset.filter(pk__in=primary_keys)
                    if count_only:
                        yield queryset.order_by().count()
                    else:
                        for obj in queryset.iterator():
                            yield obj

        try:
            self.stdout.ending = None
            progress_output = None
            object_count = 0
            # If dumpdata is outputting to stdout, there is no way to display progress
            if (output and self.stdout.isatty() and options['verbosity'] > 0):
                progress_output = self.stdout
                object_count = sum(get_objects(count_only=True))
            stream = open(output, 'w') if output else None
            try:
                serializers.serialize(
                    format, get_objects(), indent=indent,
                    use_natural_foreign_keys=use_natural_foreign_keys,
                    use_natural_primary_keys=use_natural_primary_keys,
                    stream=stream or self.stdout, progress_output=progress_output,
                    object_count=object_count,
                )
            finally:
                if stream:
                    stream.close()
        except Exception as e:
            if show_traceback:
                raise
            raise CommandError("Unable to serialize database: %s" % e)
