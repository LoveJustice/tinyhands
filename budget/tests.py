from datetime import timedelta

from django.core.urlresolvers import reverse
from django.utils import timezone
from django_webtest import WebTest

from budget.factories import *

class BudgetCalcApiTests(WebTest):

    def setUp(self):
        #timezone.now() gets utc time but timezone.now().now() gets local Nepal time
        self.day1 = timezone.now().now()
        self.day2 = timezone.now().now() - timedelta(days=1)
        self.irf_one = IrfFactory.create(date_time_of_interception=self.day1);
        self.irf_two = IrfFactory.create(date_time_of_interception=self.day2);
        self.int1 = IntercepteeFactory.create(interception_record=self.irf_one);
        self.int2 = IntercepteeFactory.create(interception_record=self.irf_one);
        self.int3 = IntercepteeFactory.create(interception_record=self.irf_two);
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

        today_interceptions = today['interceptions']
        station_code = self.irf_one.irf_number[:3]
        self.assertEquals(today_interceptions[station_code], 2)

        #Test that yesterday entry is right
        yesterday = json['1']
        self.assertEquals(yesterday['dayOfWeek'], self.days[self.day2.weekday()])
        yesterday_interceptions = yesterday['interceptions']
        station_code = self.irf_two.irf_number[:3]
        self.assertEquals(yesterday_interceptions[station_code], 1)