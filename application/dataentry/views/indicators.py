import datetime

from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings

from dataentry.models import Country, IndicatorHistory, SiteSettings

class IndicatorsViewSet(viewsets.ViewSet):
    def calculate_indicators(self, request, country_id):
        end_date = datetime.datetime.now().date()
        start_date = end_date - datetime.timedelta(30)
        results = {}
        site_settings = SiteSettings.objects.all()[0]
        try:
            goals = site_settings.get_setting_value_by_name('indicator_goals')
        except:
            goals = {
                    'irfLag': 5,
                    'photosLag': 5,
                    'vdfLag': 5,
                    'cifLag': 5,
                    'v1Lag': 4,
                    'v1Backlog': 10,
                    'v2Lag': 7,
                    'v2Backlog': 10,
                    }
        
        country = Country.objects.get(id=country_id)
        current_results = IndicatorHistory.calculate_indicators(start_date, end_date, country)
        current_results['title'] = 'Last 30 days'
        results['latest'] = current_results
        results['goals'] = goals
        
        history = []
        history_entries = IndicatorHistory.objects.filter(country=country).order_by("-year","-month")
        for history_entry in history_entries:
            results_entry = history_entry.indicators
            results_entry['title']=str(history_entry.year) + '-' + str(history_entry.month)
            history.append(results_entry)
        
        results['history'] = history
        return Response(results)
 