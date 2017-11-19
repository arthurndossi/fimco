import json
from urllib2 import Request, urlopen, URLError

from datetime import timedelta, date

# from django.utils import timezone

# from .models import ExchangeRates


def date_range(start, end):
    for n in range(int((end - start).days)):
        yield start + timedelta(n)


def import_data(start_date, end_date):
    for single_date in date_range(start_date, end_date):
        _date = single_date.strftime("%Y-%m-%d")
        request = Request('https://api.fixer.io/'+_date+'?base=USD')

        try:
            response = urlopen(request)
            data = json.loads(response.read())
            rates = data['rates']

            yesterday = (single_date - timedelta(1)).strftime('%Y-%m-%d')

            for key, value in rates.items():
                print("%s:  %s" % (key, value))
            #     try:
            #         prev_rate = ExchangeRates.objects.get(counter_currency=key).latest('counter_currency').change
            #     except ExchangeRates.DoesNotExist:
            #         prev_rate = 0
            #     change = value - prev_rate
            # print("%s:  %s" % (key, value))
            #     ExchangeRates.objects.create(
            #         modified_on=data['date'],
            #         base_currency=data['base'],
            #         counter_currency=key,
            #         change=change,
            #         current_rate=value,
            #         prev_rate=2.260,
            #         prev_rate_timestamp=yesterday,
            #         record_datetime=timezone.now()
            #     )
        except URLError, e:
            print 'No exchange data. Got an error code:', e


if __name__ == "__main__":
    start_date = date(2017,11,17)
    end_date = date(2017,11,18)
    import_data(start_date,end_date)