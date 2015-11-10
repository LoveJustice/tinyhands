from rest_framework import serializers
from accounts.models import Account, DefaultPermissionsSet

class AccountsSerializer(serializers.ModelSerializer):
    has_been_activated = serializers.BooleanField(source='has_usable_password')
    
    class Meta:
        model = Account
        exclude = ['password', 'activation_key', 'groups','user_permissions', 'is_staff', 'is_superuser']
        read_only_fields = ['has_been_activated']

class DefaultPermissionsSetSerializer(serializers.ModelSerializer):
    is_used_by_accounts = serializers.BooleanField();
    
    class Meta:
        model = DefaultPermissionsSet
        exclude = []
        read_only_fields = ['is_used_by_accounts']
