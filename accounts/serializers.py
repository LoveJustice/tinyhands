from rest_framework import serializers
from accounts.models import Account, DefaultPermissionsSet

class AccountsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        exclude = ['password', 'activation_key', 'groups','user_permissions', 'is_staff', 'is_superuser']

class DefaultPermissionsSetSerializer(serializers.ModelSerializer):
    is_used_by_accounts = serializers.BooleanField();
    
    class Meta:
        model = DefaultPermissionsSet
        exclude = []
        read_only_fields = ['is_used_by_accounts']
