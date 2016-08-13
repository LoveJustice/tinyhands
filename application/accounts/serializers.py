from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from accounts.models import Account, DefaultPermissionsSet

class AccountsSerializer(serializers.ModelSerializer):
    has_been_activated = serializers.BooleanField(source='has_usable_password', read_only=True)
    user_designation_name = serializers.SerializerMethodField(read_only=True)

    def create(self, validated_data):
        account = Account.objects.create(**validated_data)
        try:
            account.send_activation_email()
        except:
            account.delete()
            raise serializers.ValidationError({'email': ["Email address is invalid"]})
        return account

    def get_user_designation_name(self, obj):
        return obj.user_designation.name;

    class Meta:
        model = Account
        exclude = ['password', 'activation_key', 'groups','user_permissions', 'is_staff', 'is_superuser']

class DefaultPermissionsSetSerializer(serializers.ModelSerializer):
    is_used_by_accounts = serializers.BooleanField(read_only=True);
    name = serializers.CharField(
        max_length=255,
        validators=[
            UniqueValidator(
                queryset=DefaultPermissionsSet.objects.all(),
                message="There is already a designation with the same name."
            )
        ]
     )

    class Meta:
        model = DefaultPermissionsSet
        exclude = []
