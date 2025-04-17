import requests
import json
import time
import traceback

from django.core.management.base import BaseCommand

from dataentry.models import Person, LocationBoxCommon, CountryExchange


COUNTRIES_TO_TRY = [
    'Lesotho',
    'Rwanda',
    'India',
    'Mozambique',
    'Kenya',
    'Sierra Leone',
    'Zimbabwe'
]

# 1000 free requests
OPEN_EXCHANGE_RATES_HISTORICAL_BASE_URL = 'https://openexchangerates.org/api/historical/'
OPEN_EXCHANGE_RATES_APP_ID = '3f7c05ea105a4543b9acdd033d06bded'
class Command(BaseCommand):

    def handle(self, *args, **options):
        example_exchanges = CountryExchange.objects.filter(year_month__lt='202504', year_month__gte='202409', country__name__in=COUNTRIES_TO_TRY)

        print("Date,LJI,Open Exchange")
        for exchange in example_exchanges:
            date_in_iso = exchange.date_time_last_updated.date().isoformat()
            currency_symbol = exchange.country.currency_symbol
            # show_ask_bid is another parameter I would like to use, but it increases cost of API from free to >$100/mo
            open_exchange_rates_response = requests.get(OPEN_EXCHANGE_RATES_HISTORICAL_BASE_URL + date_in_iso + '.json', params={'app_id': OPEN_EXCHANGE_RATES_APP_ID,
                                                                                                  'base': 'USD',
                                                                                                  'symbols': currency_symbol})
            open_exchange_rates_data = open_exchange_rates_response.json()
            # print('open exchange rates json', open_exchange_rates_data)
            open_exchange_rates_exchange_rate = open_exchange_rates_data['rates'][currency_symbol]
            if currency_symbol == 'SLL':
                # Currency converter doesn't have symbol SLE, when Sierra Leone reissued currency as SLL * 1000
                open_exchange_rates_exchange_rate = open_exchange_rates_exchange_rate / 1000.0
            # print('open exchange rates:', open_exchange_rates_exchange_rate)

            lji_exchange_rate = exchange.exchange_rate
            # print('LJI entered: ', lji_exchange_rate)
            print(exchange.country,",",date_in_iso,",",lji_exchange_rate, "," , open_exchange_rates_exchange_rate)




