from django.core.management.base import BaseCommand

from accounts.models import Account
from rest_framework.authtoken.models import Token


class Command(BaseCommand):
    help = 'Create API Tokens for all users in DB if they do not already have one'

    def handle(self, *args, **options):
        for user in Account.objects.all():
            Token.objects.get_or_create(user=user)
