import os

import requests
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


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
