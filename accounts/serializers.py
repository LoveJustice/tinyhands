from rest_framework import serializers
from accounts.models import Account, DefaultPermissionsSet

class AccountsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        exclude = ['password', 'activation_key', 'groups','user_permissions', 'is_staff', 'is_superuser']

class DefaultPermissionsSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefaultPermissionsSet
        exclude = []
