from rest_framework import serializers
from accounts.models import Account

class AccountsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        exclude = ['password','last_login','activation_key', 'groups','user_permissions']
