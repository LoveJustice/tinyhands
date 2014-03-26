from django_webtest import WebTest
from dataentry.models import InterceptionRecord


class TestModels(WebTest):

    def test_interception_record_model(self):
        record = InterceptionRecord(
            who_in_group=0,
            drugged_or_drowsy=True,
            meeting_someone_across_border=True
        )
        self.assertEqual(record.calculate_total(), 70)
