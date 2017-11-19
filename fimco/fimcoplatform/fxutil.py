import json
from datetime import timedelta, date
from urllib2 import Request, urlopen, URLError

from decimal import Decimal
from fimcoplatform.models import ExchangeRates


def date_range(start, end):
    for n in range(int((end - start).days)):
        yield start + timedelta(n)


def import_data(start, end):
    for single_date in date_range(start, end):
        _date = single_date.strftime("%Y-%m-%d")
        request = Request('https://api.fixer.io/'+_date+'?base=USD')

        try:
            response = urlopen(request)
            data = json.loads(response.read())
            rates = data['rates']

            yesterday = (single_date - timedelta(1)).strftime('%Y-%m-%d')

            for key, value in rates.items():
                # print("%s:  %s" % (key, value))
                try:
                    prev_rate = ExchangeRates.objects.filter(counter_currency=key).latest('counter_currency').change
                except ExchangeRates.DoesNotExist:
                    prev_rate = 0
                change = Decimal(value) - prev_rate
                ExchangeRates.objects.create(
                    modified_on=data['date'],
                    base_currency=data['base'],
                    counter_currency=key,
                    change=round(change, 3),
                    current_rate=round(value, 3),
                    prev_rate=round(prev_rate, 3),
                    prev_rate_timestamp=yesterday,
                    record_datetime=single_date
                )
        except URLError, e:
            print 'No exchange data. Got an error code:', e


if __name__ == "__main__":
    start_date = date(2017, 11, 1)
    end_date = date(2017, 11, 18)
    import_data(start_date, end_date)
