import logging
import os

import requests
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from util.auth0 import get_auth0_user, create_or_update_django_user

logger = logging.getLogger(__name__)


# Patch because it modifies a user in the database
# However it doesn't need any body
@api_view(["PATCH"])
@permission_classes((IsAuthenticated,))
def update_auth0_user_view(request, username):
    auth0_user: dict = get_auth0_user(username)
    django_username = username.replace('|', '.')
    if auth0_user is not None and ('email' in auth0_user):
        account = create_or_update_django_user(auth0_user)
        return JsonResponse({'status': 'OK'})
    else:
        logger.warning('No Auth0 account found for ' + django_username)
        return JsonResponse({})


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def send_current_user_password_reset_email(request):
    domain = os.environ.get('AUTH0_DOMAIN', 'UNSET_AUTH0_DOMAIN')
    client_id = os.environ.get('AUTH0_BACKEND_CLIENT_ID', 'UNSET_AUTH0_BACKEND_CLIENT_ID')
    reset_api_url = 'https://' + domain + '/dbconnections/change_password'
    account = request.user
    body = {"client_id": client_id, "email": account.email, "connection": "Username-Password-Authentication"}
    response = requests.post(url=reset_api_url, data=body)
    if not response.ok:
        raise Exception(
            'send_password_reset_email was not ok: ' + str(response.status_code) + '\njson: ' + str(response.json()))
    return JsonResponse({'status': 'OK'})
