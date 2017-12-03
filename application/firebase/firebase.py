from django.conf import settings
import json
from oauth2client.service_account import ServiceAccountCredentials
from urllib2 import Request, urlopen


TOPIC_INTERCEPTION_ALERT = "irf-alert"

FCM_SCOPE = "https://www.googleapis.com/auth/firebase.messaging"


def get_firebase_service():
    return FirebaseMessageService(settings.FCM_PROJECT_ID, _get_access_token())


def _get_access_token():
    credentials = ServiceAccountCredentials.from_json_keyfile_name(settings.FCM_KEY_FILE, FCM_SCOPE)
    access_token_info = credentials.get_access_token()
    return access_token_info.access_token


def _get_fcm_messages_url_for_project(project_id):
    return 'https://fcm.googleapis.com/v1/projects/' + project_id + '/messages:send'


class FirebaseMessageService:

    def __init__(self, project_id, access_token):
        self._project_id = project_id
        self._access_token = access_token

    def send_message(self, topic, title, body):
        request = Request(_get_fcm_messages_url_for_project(self._project_id))

        request.add_header('Authorization', 'Bearer ' + self._access_token)
        request.add_header('Content-Type', 'application/json')

        data = self._build_request_data(topic, title, body)
        request.add_data(json.dumps(data))
        response = urlopen(request)
        if response.getcode() == 200:
            return True
        else:
            return False

    @staticmethod
    def _build_request_data(topic, title, body):
        return {
            'message': {
                'topic': topic,
                'notification': {
                    'body': body,
                    'title': title
                }
            }
        }
