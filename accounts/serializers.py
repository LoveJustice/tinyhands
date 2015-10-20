from rest_framework import serializers
from accounts.models import Account, DefaultPermissionsSet

class AccountsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        exclude = ['password','last_login','activation_key', 'groups','user_permissions']

class DefaultPermissionsSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefaultPermissionsSet
        exclude = []
