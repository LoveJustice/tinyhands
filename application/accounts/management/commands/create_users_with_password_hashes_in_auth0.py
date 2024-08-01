from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from util.auth0 import create_auth0_user, create_all_auth0_users, delete_auth0_users_with_no_logins

User = get_user_model()

# Taken from https://community.auth0.com/t/wrong-password-for-imported-users-from-django/61105/2
class Command(BaseCommand):
    """
    Take all users in database creates a file that you can send to Auth0
    """
    help = 'Take all users in database creates a file that you can send to Auth0'

    def handle(self, *args, **options):
        delete_auth0_users_with_no_logins()
        create_all_auth0_users()


