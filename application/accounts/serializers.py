from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from accounts.models import Account, DefaultPermissionsSet


class AccountsSerializer(serializers.ModelSerializer):
    has_been_activated = serializers.BooleanField(source='has_usable_password', read_only=True)
    user_designation_name = serializers.SerializerMethodField(read_only=True)

    def create(self, validated_data):
        # Assumes all email addresses are valid.
        # You should probably be creating emails through Auth0 syncing and not manually through the django UI
        account: Account = Account.objects.create(**validated_data)
        return account

    def get_user_designation_name(self, obj):
        if obj.user_designation is None or obj.user_designation.name is None:
            return ""
        else:
            return obj.user_designation.name

    class Meta:
        model = Account
        exclude = ['password', 'activation_key', 'groups', 'user_permissions', 'is_staff', 'is_superuser']


class AccountMDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'email', 'first_name', 'last_name', 'receives_money_distribution_form']

    def get_receives_money_distribution_form(self, obj):
        return True

    receives_money_distribution_form = serializers.SerializerMethodField(read_only=True)


class DefaultPermissionsSetSerializer(serializers.ModelSerializer):
    is_used_by_accounts = serializers.BooleanField(read_only=True)
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
