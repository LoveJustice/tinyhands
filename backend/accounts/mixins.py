from django.core.exceptions import ImproperlyConfigured, PermissionDenied


class PermissionsRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if self.permissions_required is None:
            raise ImproperlyConfigured(
                'PermissionsRequiredMixin must be used on a view '
                'setting the `permissions_required` property, corresponding '
                'to a list of strings equal to the properties on the '
                'Account model that must be checked to True for this '
                'page to be shown to that user.')
        for permission_str in self.permissions_required:
            if not getattr(request.user, permission_str):
                raise PermissionDenied
        return super(PermissionsRequiredMixin, self).dispatch(request, *args, **kwargs)
