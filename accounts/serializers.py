from rest_framework import serializers
from accounts.models import Account, DefaultPermissionsSet

class AccountsSerializer(serializers.ModelSerializer):
    has_been_activated = serializers.BooleanField(source='has_usable_password', read_only=True)
    
    class Meta:
        model = Account
        exclude = ['password', 'activation_key', 'groups','user_permissions', 'is_staff', 'is_superuser']

    def create(self, validated_data):
        account = Account.objects.create(**validated_data)
        account.send_activation_email()
        return account


class DefaultPermissionsSetSerializer(serializers.ModelSerializer):
    is_used_by_accounts = serializers.BooleanField(read_only=True);
    
    class Meta:
        model = DefaultPermissionsSet
        exclude = []
