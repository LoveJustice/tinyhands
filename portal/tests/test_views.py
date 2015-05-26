from datetime import timedelta
from django.core.urlresolvers import reverse
from django.utils import timezone
from django_webtest import WebTest

from dataentry.tests.factories import IntercepteeFactory, IrfFactory
from accounts.tests.factories import SuperUserFactory

class TallyApiTests(WebTest):

    def setUp(self):
        #timezone.now() gets utc time but timezone.now().now() gets local Nepal time
        self.superuser = SuperUserFactory.create()
        self.day1 = timezone.now().now()
        self.day2 = timezone.now().now() - timedelta(days=1)
        self.irf_one = IrfFactory.create(date_time_of_interception=self.day1);
        self.irf_two = IrfFactory.create(date_time_of_interception=self.day2);
        self.int1 = IntercepteeFactory.create(interception_record=self.irf_one);
        self.int2 = IntercepteeFactory.create(interception_record=self.irf_one);
        self.int3 = IntercepteeFactory.create(interception_record=self.irf_two);
        self.days = ['Monday', 'Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

    def test(self):
        response = self.app.get(reverse('tally_day_api'), user=self.superuser)
        json = response.json
        self.assertEquals(response.status_code, 200)

        #make sure we are getting the past 7 days
        self.assertEquals(len(json), 2)
        self.assertEquals(json['id'], self.superuser.id)

        #Test that today entry is right
        today = json['days'][0]
        todayDate = timezone.datetime.strptime(today['date'], '%Y-%m-%dT%H:%M:%S.%f')
        self.assertEquals(todayDate.year, self.day1.year)
        self.assertEquals(todayDate.month, self.day1.month)
        self.assertEquals(todayDate.day, self.day1.day)

        today_interceptions = today['interceptions']
        station_code = self.irf_one.irf_number[:3]
        self.assertEquals(today_interceptions[station_code], 2)
        
        #Test that yesterday entry is right
        yesterday = json['days'][1]
        yesterdayDate = timezone.datetime.strptime(yesterday['date'], '%Y-%m-%dT%H:%M:%S.%f')
        self.assertEquals(yesterdayDate.year, self.day2.year)
        self.assertEquals(yesterdayDate.month, self.day2.month)
        self.assertEquals(yesterdayDate.day, self.day2.day)
    
        yesterday_interceptions = yesterday['interceptions']
        station_code = self.irf_two.irf_number[:3]
        self.assertEquals(yesterday_interceptions[station_code], 1)