from django.conf import settings
import json
from oauth2client.service_account import ServiceAccountCredentials
from urllib2 import Request, urlopen


TOPIC_INTERCEPTION_ALERT = "interception-alert"

FCM_SCOPE = "https://www.googleapis.com/auth/firebase.messaging"


def _get_project_id():
    try:
        with open(settings.FCM_KEY_PATH) as firebase_key:
            firebase_data = json.load(firebase_key)
        return firebase_data['project_id']
    except:
        print 'Unable to load firebase key file'


def _get_access_token():
    credentials = ServiceAccountCredentials.from_json_keyfile_name(settings.FCM_KEY_PATH, FCM_SCOPE)
    access_token_info = credentials.get_access_token()
    return access_token_info.access_token


def _get_fcm_messages_url_for_project(project_id):
    return 'https://fcm.googleapis.com/v1/projects/' + project_id + '/messages:send'


def _build_message_data(topic, title, body):
    return {
        'message': {
            'topic': topic,
            'notification': {
                'body': body,
                'title': title
            }
        }
    }


def _send_message(project_id, access_token, topic, title, body):
    request = Request(_get_fcm_messages_url_for_project(project_id))

    request.add_header('Authorization', 'Bearer ' + access_token)
    request.add_header('Content-Type', 'application/json')

    data = _build_message_data(topic, title, body)
    request.add_data(json.dumps(data))
    response = urlopen(request)
    if response.getcode() == 200:
        return True
    else:
        return False


def send_interception_alert_notification(message):
    return _send_message(_get_project_id(), _get_access_token(), TOPIC_INTERCEPTION_ALERT, 'Project Beautiful', message)

