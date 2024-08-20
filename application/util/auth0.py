# https://auth0.com/docs/quickstart/backend/django/01-authorization
import datetime
import json
import logging
import os
import time
from base64 import b64encode
from json import JSONDecodeError
from typing import List

import jwt
import requests
from dateutil.relativedelta import relativedelta
from django.contrib.auth import authenticate
from django.core.cache import cache

from accounts.models import Account

logger = logging.getLogger(__name__)


# Hooked into settings.py
def jwt_get_username_from_payload_handler(payload):
    auth0_id = payload.get('sub').replace('|', '.')
    try:
        # TODO This db hit could be make all calls a bit slower
        account = Account.objects.get(auth0_id=auth0_id)
        username = account.get_username()
    except Account.DoesNotExist:
        username = None
    authenticate(remote_user=username)
    return username


# Hooked into settings.py
def jwt_decode_token(token):
    header = jwt.get_unverified_header(token)
    domain = os.environ.get('AUTH0_DOMAIN', 'UNSET_AUTH0_DOMAIN')

    # Lol a reddit link in code!
    # https://www.reddit.com/r/django/comments/bvvsa5/best_way_to_work_with_cached_parameters/
    jwks = get_jwks(domain)
    public_key = get_public_key_from_jwks_and_header(jwks, header)

    if public_key is None:
        # Clear cache and try again
        cache.delete("jwks")
        public_key = get_public_key_from_jwks_and_header(jwks, header)

    if public_key is None:
        raise Exception('Public key not found.')

    domain = os.environ.get('AUTH0_DOMAIN', 'UNSET_AUTH0_DOMAIN')
    audience = os.environ.get('AUTH0_AUDIENCE_ID', 'UNSET_AUTH0_AUDIENCE_ID')
    issuer = 'https://{}/'.format(domain)
    return jwt.decode(token, public_key, audience=audience, issuer=issuer, algorithms=['RS256'])


def get_jwks(domain):
    jwks = cache.get('jwks', [])
    if len(jwks) == 0:
        # Connection error here? Check internet connection. Can you connect to Auth0 cloud servers?
        response = requests.get('https://{}/.well-known/jwks.json'.format(domain))
        if response.ok:
            jwks = response.json()
            cache.set('jwks', jwks, timeout=7776000)  # cache for 90 days
        else:
            raise Exception('Issue fetching public key.')

    return jwks


def get_public_key_from_jwks_and_header(jwks, header):
    public_key = None
    for jwk in jwks['keys']:
        # Problem here? Did you correctly set up your Auth0's api page and JWT_AUTH setting?
        if jwk['kid'] == header['kid']:
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))
    return public_key


ONLY_UPDATE_AUTH0_ID = True


# Example of the full auth0 user DICT returned:
# {
#     "created_at": "2021-12-21T08:51:09.330Z",
#     "email": "brad@example.com",
#     "email_verified": false,
#     "identities": [
#         {
#             "connection": "Username-Password-Authentication",
#             "provider": "auth0",
#             "user_id": "61c1957df64d4a0072b034a1",
#             "isSocial": false
#         }
#     ],
#     "name": "Bradley Wells",
#     "nickname": "brad",
#     "picture": "https://s.gravatar.com/avatar/600b3d8cd238e5944a462d3eb53b7277?s=480&r=pg&d=https%3A%2F%2Fcdn.auth0.com%2Favatars%2Fbr.png",
#     "updated_at": "2021-12-28T08:20:04.242Z",
#     "user_id": "auth0|61c1957df64d4a0072b034a1",
#     "family_name": "Wells",
#     "given_name": "Bradley",
#     "last_ip": "1.2.3.4",
#     "last_login": "2021-12-28T08:20:04.242Z",
#     "logins_count": 10
# }


def get_auth0_users() -> List[dict]:
    api_token_result = get_auth0_api_token()
    access_token = api_token_result['access_token']
    headers = {'Authorization': 'Bearer ' + access_token}
    domain = os.environ.get('AUTH0_DOMAIN', 'UNSET_AUTH0_DOMAIN')
    # Auth0 limits the number of users you can return.
    # If you exceed this threshold, please redefine your search
    url_without_params = 'https://' + domain + '/api/v2/users'

    list_of_users = []
    has_more_users = True
    page_index = 0
    num_per_page = 20
    while has_more_users:
        logger.debug(f'getting page {page_index} of auth0 users')
        response = requests.get(url=url_without_params + '?page=' + str(page_index)
                                    + '&per_page=' + str(num_per_page), headers=headers)
        if not response.ok:
            logger.warning(
                'get_auth0_user_by_email was not ok: ' + str(response.status_code) + '\njson: ' + str(response.json()))
            raise Exception('Problem with getting Auth0 users')
        page_of_users: list = response.json()
        list_of_users.extend(page_of_users)
        if len(page_of_users) == 0:
            has_more_users = False
        page_index += 1
    return list_of_users

# This takes about 5 mins
# See the page number going down at https://manage.auth0.com/dashboard/us/dev-oiz87mbf/users
def delete_auth0_users_with_no_logins():
    auth0_users = get_auth0_users()
    print(json.dumps(auth0_users, indent=4))
    for auth0_user in auth0_users:
        logins_count = auth0_user.get('logins_count')
        if logins_count is not None and logins_count > 0:
            logger.debug(f'skipping {auth0_user["email"]}, has {logins_count} logins')
        else:
            logger.info(f'Deleting {auth0_user["email"]}')
            delete_auth0_user(auth0_user)

def delete_auth0_user(auth0_user: dict):
    api_token_result = get_auth0_api_token()
    access_token = api_token_result['access_token']
    headers = {'Authorization': 'Bearer ' + access_token}
    domain = os.environ.get('AUTH0_DOMAIN', 'UNSET_AUTH0_DOMAIN')
    url = 'https://' + domain + '/api/v2/users/' + auth0_user.get('user_id')
    response = requests.delete(url=url, headers=headers)
    if not response.ok:
        try:
            logger.warning(
                'delete_auth0_user was not ok: ' + str(response.status_code) + '\njson: ' + str(response.json()))
        except JSONDecodeError:
            logger.warning(
                'delete_auth0_user was not 200: ' + str(response.status_code))


def get_auth0_user_by_email(email) -> dict:
    # In django we save them with a dot, but auth0 knows pipe.
    # See jwt_get_username_from_payload_handler for the reverse
    api_token_result = get_auth0_api_token()
    access_token = api_token_result['access_token']
    headers = {'Authorization': 'Bearer ' + access_token}
    domain = os.environ.get('AUTH0_DOMAIN', 'UNSET_AUTH0_DOMAIN')
    url = 'https://' + domain + '/api/v2/users?q=email:\"' + email + '\"'
    response = requests.get(url=url, headers=headers)
    if not response.ok:
        logger.warning(
            'get_auth0_user_by_email was not ok: ' + str(response.status_code) + '\njson: ' + str(response.json()))
    list_of_users: list = response.json()
    if len(list_of_users) == 0:
        raise Exception('User with email ' + email + ' was not found')
    if len(list_of_users) > 1:
        raise Exception('Expected to find user with email ' + email + ' but found ' + len(list_of_users))
    content = list_of_users[0]
    return content


def get_auth0_user(username) -> dict:
    # In django we save them with a dot, but auth0 knows pipe.
    # See jwt_get_username_from_payload_handler for the reverse
    auth0_username = username.replace('.', '|')
    api_token_result = get_auth0_api_token()
    access_token = api_token_result['access_token']
    headers = {'Authorization': 'Bearer ' + access_token}
    domain = os.environ.get('AUTH0_DOMAIN', 'UNSET_AUTH0_DOMAIN')
    url = 'https://' + domain + '/api/v2/users/' + auth0_username
    response = requests.get(url=url, headers=headers)
    content = response.json()
    return content


def get_auth0_api_token():
    # NOTE: WE ONLY GET 1000 FREE TOKENS PER MONTH FOR THIS!!!!
    headers = {'content-type': "application/x-www-form-urlencoded"}
    client_id = os.environ.get('AUTH0_BACKEND_CLIENT_ID', 'UNSET_AUTH0_BACKEND_CLIENT_ID')
    client_secret = os.environ.get('AUTH0_BACKEND_CLIENT_SECRET', 'UNSET_AUTH0_BACKEND_CLIENT_SECRET')
    domain = os.environ.get('AUTH0_DOMAIN', 'UNSET_AUTH0_DOMAIN')
    request_data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        # This is not AUTH0_AUDIENCE_ID! We are calling the auth0 api, not our own!
        'audience': 'https://' + domain + '/api/v2/'
    }
    url = 'https://' + domain + '/oauth/token'
    response = requests.post(url=url, data=request_data, headers=headers)
    if not response.ok:
        logger.warning(
            'get_auth0_api_token was not ok: ' + str(response.status_code) + '\njson: ' + str(response.json()))
    # TODO decode utf-8?
    return response.json()


# def create_django_account(auth0_user):
#     email = auth0_user['email']
#     logger.info('Creating django account with email: ' + email)
#     django_account = Account()
#     # Try getting credentials from SSO first (based on email), otherwise they must not be in there yet
#     # Eventually we always want them in SSO first
#     django_username = auth0_user['user_id'].replace('|', '.')
#     django_account.auth0_id = django_username
#     django_account.date_joined = auth0_user['created_at']
#     if 'given_name' in auth0_user:
#         django_account.first_name = auth0_user['given_name']
#     if 'family_name' in auth0_user:
#         django_account.last_name = auth0_user['family_name']
#     django_account.email = auth0_user['email']
#     django_account.is_active = True
#     django_account.is_staff = False
#     logger.debug('Auth0 account found for email: ' + email + ', inserting')
#     # django_account.activation_key = '?????'
#     django_account.save()
#     return django_account


def update_django_user_if_exists(auth0_user: dict):
    auth0_id = auth0_user['user_id'].replace('|', '.')
    email = auth0_user['email']
    try:
        account = Account.objects.get(email__iexact=email)
    except Account.DoesNotExist:
        logger.debug(f'No SL user for auth0 user with email {email}, skipping.')
        return None

    account.auth0_id = auth0_id

    if not ONLY_UPDATE_AUTH0_ID:
        # Name seems to be the easy field to edit on the Auth0 API
        # When I updated Auth0 through the website, name changed but given_name and family_name didn't
        if 'name' in auth0_user:
            # (' ', 1) splits on only the FIRST space, preserving middle names in the last name field
            split_name = auth0_user['name'].split(' ', 1)
            account.first_name = split_name[0]
            if len(split_name) == 2:
                account.last_name = split_name[1]
        elif 'given_name' in auth0_user or 'family_name' in auth0_user:
            if 'given_name' in auth0_user:
                account.first_name = auth0_user['given_name']
            if 'family_name' in auth0_user:
                account.last_name = auth0_user['family_name']
        if 'last_login' in auth0_user:
            # This pulls the last login from Auth0
            #   That means the last login to any of our apps.
            account.last_login = auth0_user['last_login']
    logger.info('Updating django account with email: ' + email)
    account.save()
    return account


def create_all_auth0_users():
    accounts: List[Account] = Account.objects.all()
    auth0_user_dicts = []
    for account in accounts:
        three_years_ago_today = datetime.datetime.now().date() - relativedelta(years=3)
        if account.is_active \
                and account.email \
                and account.password \
                and not account.password.startswith('!')\
                and account.last_login \
                and account.last_login.date() > three_years_ago_today:
            auth0_user_dict = get_auth0_dict_for_django_user(account)
            logger.info(f'Trying to create auth0 account for {account.email}, adding information to import')
            auth0_user_dicts.append(auth0_user_dict)
        else:
            logger.info(
                f'skipping account {account.email}, is_active={account.is_active}, last_login={account.last_login}')
    print(json.dumps(auth0_user_dicts, indent=4))

    job_id = update_auth0_users_with_dicts(auth0_user_dicts)

    # For debugging, this assumes it is failing and querys for why it failed
    time.sleep(50)
    get_auth0_job_errors(job_id)


def create_auth0_user(account):
    auth0_user_dict = get_auth0_dict_for_django_user(account)
    if auth0_user_dict is not None:
        job_id = update_auth0_users_with_dicts([auth0_user_dict])

        # For debugging, this assumes it is failing and querys for why it failed
        time.sleep(5)
        get_auth0_job_errors(job_id)


# Mostly for failures of update_auth0_users_with_dicts
# These records get deleted after 24 hours so check immediately!
def get_auth0_job_errors(job_id: str):
    api_token_result = get_auth0_api_token()
    access_token = api_token_result['access_token']
    # From https://auth0.com/docs/manage-users/user-migration/bulk-user-imports
    headers = {
        'Authorization': 'Bearer ' + access_token
    }
    domain = os.environ.get('AUTH0_DOMAIN', 'UNSET_AUTH0_DOMAIN')
    url = f'https://{domain}/api/v2/jobs/{job_id}/errors'
    error_response = requests.get(url=url, headers=headers)
    print(error_response.status_code, error_response.json())


def update_auth0_users_with_dicts(auth0_user_dicts: List[any]):
    api_token_result = get_auth0_api_token()
    access_token = api_token_result['access_token']
    # From https://auth0.com/docs/manage-users/user-migration/bulk-user-imports
    headers = {
        'Authorization': 'Bearer ' + access_token
    }
    domain = os.environ.get('AUTH0_DOMAIN', 'UNSET_AUTH0_DOMAIN')
    url = 'https://' + domain + '/api/v2/jobs/users-imports'
    form_values = {
        # Get this at manage.auth0.com -> Authentication -> Database
        'connection_id': os.environ.get('AUTH0_DATABASE_CONNECTION_ID'),
        'upsert': 'true'
    }
    form_files = {
        'users': ('users.json', json.dumps(auth0_user_dicts), 'text/json')
    }
    response = requests.post(url=url, files=form_files, data=form_values, headers=headers)
    response.raise_for_status()
    job_id = response.json()['id']
    # print('Job id for failure checking: ' + response.json()['id'])
    return job_id


def get_auth0_dict_for_django_user(account: Account):
    if not account.email:
        logger.info(f'User {account.id} has no email.')
        return None

    if not account.password:
        logger.info(f'User {account.id} has no password.')
        return None

    password_parts = account.password.split('$')
    password_parts[0] = password_parts[0].replace('_', '-')
    password_parts[2] = b64encode(password_parts[2].encode()).decode().replace('=', '')
    password_parts[3] = password_parts[3].replace('=', '')
    password_hash = f'${password_parts[0]}$i={password_parts[1]},l=32${password_parts[2]}${password_parts[3]}'
    name = str(account.first_name + ' ' + account.last_name).strip()
    user_dict = {
        'email': account.email,
        'email_verified': True,
        'custom_password_hash': {
            'algorithm': 'pbkdf2',
            'hash': {
                'value': password_hash,
                'encoding': 'utf8'
            }
        },
        'given_name': account.first_name,
        'family_name': account.last_name,
        'name': name,
    }
    return user_dict
