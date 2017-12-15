from calendar import timegm
from datetime import timedelta
from django.utils import timezone


class FirebaseNotificationBuilder:

    PRIORITY_NORMAL = 5
    PRIORITY_HIGH = 10

    _PRIORITY_EXCEPTION_MESSAGE = 'Priority must be PRIORITY_HIGH or PRIORITY_NORMAL'
    _TTL_EXCEPTION_MESSAGE = 'TTL must be a timedelta'

    def __init__(self):
        self._topic = ""
        self._title = ""
        self._body = ""
        self._badge = 1
        self._priority = self.PRIORITY_NORMAL
        self._ttl = timedelta()

    def with_badge(self, badge):
        self._badge = badge
        return self

    def with_body(self, body):
        self._body = body
        return self

    def with_priority(self, priority):
        if priority != self.PRIORITY_HIGH and priority != self.PRIORITY_NORMAL:
            raise ValueError(self._PRIORITY_EXCEPTION_MESSAGE)
        else:
            self._priority = priority
            return self

    def with_topic(self, topic):
        self._topic = topic
        return self

    def with_title(self, title):
        self._title = title
        return self

    def with_ttl(self, ttl):
        if not isinstance(ttl, timedelta):
            raise ValueError(self._TTL_EXCEPTION_MESSAGE)
        self._ttl = ttl
        return self

    def _android_priority_enum(self):
        if self._priority == self.PRIORITY_HIGH:
            return 'high'
        elif self._priority == self.PRIORITY_NORMAL:
            return 'normal'
        else:
            raise ValueError(self._PRIORITY_EXCEPTION_MESSAGE)

    def _apple_priority_value(self):
        if self._priority == self.PRIORITY_HIGH:
            return '10'
        elif self._priority == self.PRIORITY_NORMAL:
            return '5'
        else:
            raise ValueError(self._PRIORITY_EXCEPTION_MESSAGE)

    def _android_ttl(self):
        return str(self._ttl.total_seconds()) + 's'

    def _apple_expiration(self):
        utc_timestamp = timegm((timezone.now() + self._ttl).timetuple())
        return str(utc_timestamp)

    def build(self):
        return {
            'message': {
                'topic': self._topic,
                'notification': {
                    'title': self._title,
                    'body': self._body
                },
                'android': {
                    'priority': self._android_priority_enum(),
                    'ttl': self._android_ttl()
                },
                'apns': {
                    'headers': {
                        'apns-priority': self._apple_priority_value(),
                        'apns-expiration': self._apple_expiration()
                    },
                    'payload': {
                        'aps': {
                            'badge': self._badge
                        }
                    }
                }
            }
        }