from django_webtest import WebTest
from django.core.urlresolvers import reverse
from datetime import timedelta
from django.utils import timezone

from dataentry.tests.factories import IntercepteeFactory, IrfFactory

class TallyApiTests(WebTest):

    def setUp(self):
        self.day1 = timezone.now()
        self.day2 = timezone.now() - timedelta(days=1)
        self.irfOne = IrfFactory.create(date_time_of_interception=self.day1);
        self.irfTwo = IrfFactory.create(date_time_of_interception=self.day2);
        self.int1 = IntercepteeFactory.create(interception_record=self.irfOne);
        self.int2 = IntercepteeFactory.create(interception_record=self.irfOne);
        self.int3 = IntercepteeFactory.create(interception_record=self.irfTwo);
        self.days = ['Monday', 'Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

    def test(self):
        response = self.app.get(reverse('tally_day_api'))
        json = response.json

        self.assertEquals(response.status_code, 200)

        #make sure we are getting the past 7 days
        self.assertEquals(len(json), 7)

        #Test that today entry is right
        today = json['0']
        self.assertEquals(today['dayOfWeek'], 'Today')
        todayInterceptions = today['interceptions']
        stationCode = self.irfOne.irf_number[:3]
        self.assertEquals(todayInterceptions[stationCode], 2)

        #Test that yesterday entry is right
        yesterday = json['1']
        self.assertEquals(yesterday['dayOfWeek'], self.days[self.day2.weekday()])
        yesterdayInterceptions = yesterday['interceptions']
        stationCode = self.irfTwo.irf_number[:3]
        self.assertEquals(yesterdayInterceptions[stationCode], 1)
