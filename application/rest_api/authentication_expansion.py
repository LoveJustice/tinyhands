from rest_framework import permissions
from dataentry.models import UserLocationPermission

# Permission Based Permissions
class RequestPermission(permissions.BasePermission):
    message = 'You do not have the right permission to access this data'

    # Check if permission is enabled at any level
    def custom_has_permission(self, request, view, method, permissions_required):
        if request.method == method or method == "ANY":
            for permission in permissions_required:
                perms = UserLocationPermission.objects.filter(account__id=request.user.id, permission__permission_group=permission['permission_group'], permission__action=permission['action'])
                if len(perms) == 0:
                    self.message = self.message.format(permission)
                    return False
        return True
    
    # Check if permission is enabled for specific object (e.g for a particular country or station)
    def custom_has_object_permission(self, request, view, method, permissions_required, obj):
        if request.method == method or method == "ANY":
            # Need to have a way to access the country id and border station id from the object
            # Assume each model will implement property get methods for country_id and border_station_id
            get_country_id = getattr(obj, 'get_country_id', None)
            if get_country_id is not None and callable(get_country_id):
                country_id = obj.get_country_id()
            else:
                country_id = None
            get_station_id = getattr(obj, 'get_border_station_id', None)
            if get_station_id is not None and callable(get_station_id):
                station_id = obj.get_border_station_id()
            else:
                station_id = None
            
            for permission in permissions_required:
                if not UserLocationPermission.has_session_permission(request, permission['permission_group'], permission['action'], country_id, station_id):
                    self.message = self.message.format(permission)
                    return False
        
        return True

class HasPermission(RequestPermission):
    def has_permission(self, request, view):
        return self.custom_has_permission(request, view, "ANY", view.permissions_required)
    
    def has_object_permission(self, request, view, obj):
        return self.custom_has_object_permission(request, view, "ANY", view.permissions_required, obj)


class HasDeletePermission(RequestPermission):
    def has_permission(self, request, view):
        return self.custom_has_permission(request, view, "DELETE", view.delete_permissions_required)
    
    def has_object_permission(self, request, view, obj):
        return self.custom_has_object_permission(request, view, "DELETE", view.delete_permissions_required, obj)


class HasGetPermission(RequestPermission):
    def has_permission(self, request, view):
        return self.custom_has_permission(request, view, "GET", view.get_permissions_required)
    
    def has_object_permission(self, request, view, obj):
        return self.custom_has_object_permission(request, view, "GET", view.get_permissions_required, obj)


class HasPostPermission(RequestPermission):
    def has_permission(self, request, view):
        return self.custom_has_permission(request, view, "POST", view.post_permissions_required)

    def has_object_permission(self, request, view, obj):
        return self.custom_has_object_permission(request, view, "POST", view.post_permissions_required, obj)

class HasPutPermission(RequestPermission):
    def has_permission(self, request, view):
        return self.custom_has_permission(request, view, "PUT", view.put_permissions_required)
    
    def has_object_permission(self, request, view, obj):
        return self.custom_has_object_permission(request, view, "PUT", view.put_permissions_required, obj)


class HasUserDesignation(permissions.BasePermission):  # Designation Based Permissions
    message = 'You do not have the right user designation to access this data'

    def custom_has_permission(self, request, view, required_user_designation):
        if request.user.user_designation.name != required_user_designation:
            return False
        return True


class IsSuperAdministrator(HasUserDesignation):
    def has_permission(self, request, view):
        return custom_has_permission(request, view, 'Super Administrator')
