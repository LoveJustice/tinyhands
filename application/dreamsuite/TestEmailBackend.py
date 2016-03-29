import sys
import smtplib
import threading

from django.core.mail.backends.base import BaseEmailBackend
from django.utils import six

SMTP_EMAIL = "fail@smtperror.com"

class EmailBackend(BaseEmailBackend):
    def __init__(self, *args, **kwargs):
        self.stream = kwargs.pop('stream', sys.stdout)
        self._lock = threading.RLock()
        super(EmailBackend, self).__init__(*args, **kwargs)

    def write_message(self, message):
        msg = message.message()
        msg_data = msg.as_bytes()
        if six.PY3:
            charset = msg.get_charset().get_output_charset() if msg.get_charset() else 'utf-8'
            msg_data = msg_data.decode(charset)
        self.stream.write('%s\n' % msg_data)
        self.stream.write('-' * 79)
        self.stream.write('\n')

    def send_messages(self, email_messages):
        """Write all messages to the stream in a thread-safe way."""
        if not email_messages:
            return
        msg_count = 0
        with self._lock:
            try:
                stream_created = self.open()
                for message in email_messages:
                    if message.from_email == SMTP_EMAIL:
                        raise smtplib.SMTPException()
                    self.write_message(message)
                    self.stream.flush()  # flush after each message
                    msg_count += 1
                if stream_created:
                    self.close()
            except smtplib.SMTPException:
                if not self.fail_silently:
                    raise
            except Exception:
                if not self.fail_silently:
                    raise
        return msg_count