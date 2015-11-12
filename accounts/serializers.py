from rest_framework import serializers
from accounts.models import Account


class AccountsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        exclude = ['password', 'activation_key', 'groups','user_permissions', 'is_staff', 'is_superuser']