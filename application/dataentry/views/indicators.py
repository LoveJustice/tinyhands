import datetime

from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from dataentry.models import Country, IndicatorHistory, SiteSettings

class IndicatorsViewSet(viewsets.ViewSet):
    def calculate_indicators(self, request, country_id):
        end_date = datetime.datetime.now().date()
        start_date = end_date - datetime.timedelta(30)
        results = {}
        months = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        
        
        country = Country.objects.get(id=country_id)
        if country.verification_goals is None:
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
        else:
            goals = country.verification_goals
            
        current_results = IndicatorHistory.calculate_indicators(start_date, end_date, country, include_latest_date=True)
        current_results['title1'] = 'Last 30'
        current_results['title2'] = 'Days'
        results['latest'] = current_results
        results['goals'] = goals
        
        history = []
        history_entries = IndicatorHistory.objects.filter(country=country).order_by("-year","-month")
        for history_entry in history_entries:
            results_entry = history_entry.indicators
            results_entry['title1']=months[history_entry.month]
            results_entry['title2']=str(history_entry.year)
            history.append(results_entry)
        
        results['history'] = history
        return Response(results)
 