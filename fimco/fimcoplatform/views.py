import datetime

from core.utils import render_with_global_data
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Max, Min
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template.defaultfilters import register

from pochi.models import PaidUser
from .models import ExchangeRate, OvernightInterest, Tbill, Tbond, LiborRate


@register.simple_tag()
def inverse(rate):
    return 1 / rate


@login_required
def market_views(request, page):
    return render_with_global_data(request, 'fimcoplatform/' + page + '.html', {})


@login_required
def start_trial(request):
    profile = request.user.profile
    profile_id = profile.profile_id
    PaidUser.objects.create(
        profile_id=profile_id,
        start_date=datetime.datetime.today(),
        level='STANDARD'
    )
    messages.info(request, 'You now have limited access to market information, you can always try the paid version'
                           ' for unlimited information and unsubscribe at any time.')
    return redirect(request.META['HTTP_REFERER'])


class ExchangeRateDto:
    trend = None

    def __init__(self, base_currency, counter_currency, change, current_rate, modified_on):
        self.base_currency = base_currency
        self.counter_currency = counter_currency
        self.change = change
        self.current_rate = current_rate
        self.modified_on = modified_on

    def add_history(self, trend):
        self.trend = trend


class OvernightRateDto:

    def __init__(self, current_date, previous_date, current_rate, previous_rate):
        self.current_date = current_date
        self.previous_date = previous_date
        self.change = round((current_rate - previous_rate)/current_rate * 100, 3)
        # self.last_high = last_high
        # self.last_low = last_low


def get_chart_info(request, time, value):
    if 'min' in time:
        duration = int(time[0:-3])
        data = ExchangeRate.objects.filter(
            modified_on__gte=datetime.datetime.now()-datetime.timedelta(minutes=duration), counter_currency=value)
    elif 'hr' in time:
        duration = int(time[0:-2])
        data = ExchangeRate.objects.filter(modified_on__gte=datetime.datetime.now()-datetime.timedelta(hours=duration),
                                           counter_currency=value)
    elif 'day' in time:
        duration = int(time[0:-4])
        data = ExchangeRate.objects.filter(modified_on__gte=datetime.datetime.now()-datetime.timedelta(days=duration),
                                           counter_currency=value)
    elif 'month' in time:
        duration = int(time[0:-6])*4
        data = ExchangeRate.objects.filter(modified_on__gte=datetime.datetime.now()-datetime.timedelta(weeks=duration),
                                           counter_currency=value)
    elif 'year' in time:
        duration = int(time[0:-5])*52
        data = ExchangeRate.objects.filter(modified_on__gte=datetime.datetime.now()-datetime.timedelta(weeks=duration),
                                           counter_currency=value)
    else:
        data = ExchangeRate.objects.filter(counter_currency=value)

    data_list = []
    label_list = []
    for row in data:
        temp_label = row.modified_on
        temp_data = row.current_rate
        label_list.append(temp_label.strftime('%d/%m/%Y'))
        data_list.append(str(temp_data))

    chart_array = {'labels': label_list, 'data': data_list}
    # chart_data = serializers.serialize('json', data)

    context = {
        'success': True,
        'array': chart_array
    }

    return JsonResponse(context)


@login_required
def exchange_view(request, page):
    if page == 'single':
        if request.GET:
            if request.GET.get('time'):
                time = request.GET['time']
                currency_val = request.session['currency']
                return get_chart_info(request, time, currency_val)

            elif request.GET.get('exchangerange'):
                # TODO implement notification
                value = request.GET['currency']
                date_range = request.GET.get('exchangerange')
                start, end = date_range.split(' - ')
                start = datetime.datetime.strptime(start, '%m/%d/%Y').strftime('%Y-%m-%d')
                end = datetime.datetime.strptime(end, '%m/%d/%Y').strftime('%Y-%m-%d')

                data = ExchangeRate.objects.filter(modified_on__range=[start, end], counter_currency=value) \
                    .annotate(day_high=Max('current_rate'), day_low=Min('current_rate'))
                data_list = []
                label_list = []
                for row in data:
                    temp_label = row.modified_on
                    temp_data = row.current_rate
                    label_list.append(temp_label.strftime('%d/%m/%Y'))
                    data_list.append(str(temp_data))

                chart_array = {'labels': label_list, 'data': data_list}

                return render_with_global_data(request, 'fimcoplatform/single_exchange.html',
                                               {'data': data, 'array': chart_array})
            else:
                value = request.GET['currency']
                request.session['currency'] = value
                data = ExchangeRate.objects.filter(modified_on__date=datetime.datetime.today(), counter_currency=value)\
                    .annotate(day_high=Max('current_rate'), day_low=Min('current_rate'))

                return render_with_global_data(request, 'fimcoplatform/single_exchange.html', {'data': data})
        else:
            pass
    else:
        _table = ExchangeRate.objects.all()

        table = []
        for single_obj in _table:
            currency = single_obj.counter_currency

            dto = ExchangeRateDto(
                single_obj.base_currency,
                single_obj.counter_currency,
                single_obj.change,
                single_obj.current_rate,
                single_obj.modified_on
            )
            list_data = ExchangeRate.objects.filter(
                counter_currency=currency, modified_on__gte=datetime.datetime.now()-datetime.timedelta(days=7))\
                .values('current_rate')
            values_list = []
            for json in list_data:
                values_list.append(json['current_rate'])
            numeric_array = [float(decimal_value) for decimal_value in values_list]
            required_array = numeric_array[-2:]
            trends = (", ".join(repr(e) for e in required_array))

            dto.add_history(trends)
            table.append(dto)

        return render_with_global_data(request, 'fimcoplatform/exchange.html', {'data': table})


@login_required
def interests_view(request):
    if request.GET['type']:
        interest_type = request.GET['type']

        if interest_type == 'overnight':
            ovi = OvernightInterest.objects.all()
            ovi_table = []
            for single_obj in ovi:
                ovi_dto = OvernightRateDto(
                    single_obj.record_datetime,
                    single_obj.prev_rate_timestamp,
                    single_obj.weighted_avg_rate,
                    single_obj.prev_rate,
                )
                ovi_table.append(ovi_dto)
            context = {
                'type': interest_type,
                'data': ovi_table
            }

            return render_with_global_data(request, 'fimcoplatform/interests.html', context)

        elif interest_type == '1mo-bill':
            one_month_t_bill = Tbill.objects.filter(type='1month').values('record_datetime', 'weighted_avg_price_success')
            context = {
                'type': '1-month Treasury bill rate',
                'data': one_month_t_bill
            }

            return render_with_global_data(request, 'fimcoplatform/interests.html', context)

        elif interest_type == '3mos-bill':
            three_month_t_bill = Tbill.objects.filter(type='3month').values('record_datetime', 'weighted_avg_price_success')
            context = {
                'type': '3-months Treasury bill rate',
                'data': three_month_t_bill
            }

            return render_with_global_data(request, 'fimcoplatform/interests.html', context)

        elif interest_type == '6mos-bill':
            six_month_t_bill = Tbill.objects.filter(type='6month').values('record_datetime', 'weighted_avg_price_success')
            context = {
                'type': '6-months Treasury bill rate',
                'data': six_month_t_bill
            }

            return render_with_global_data(request, 'fimcoplatform/interests.html', context)

        elif interest_type == '1yr-bill':
            one_year_t_bill = Tbill.objects.filter(type='1year').values('record_datetime', 'weighted_avg_price_success')
            context = {
                'type': '1-year Treasury bill rate',
                'data': one_year_t_bill
            }

            return render_with_global_data(request, 'fimcoplatform/interests.html', context)

        elif interest_type == '2yr-bond':
            two_year_t_bond = Tbill.objects.filter(type='2year').values('record_datetime', 'weighted_avg_price_success')
            context = {
                'type': '2-year Treasury bond rate',
                'data': two_year_t_bond
            }

            return render_with_global_data(request, 'fimcoplatform/interests.html', context)

        elif interest_type == '5yr-bond':
            five_year_t_bond = Tbill.objects.filter(type='5year').values('record_datetime', 'weighted_avg_price_success')
            context = {
                'type': '5-year Treasury bond rate',
                'data': five_year_t_bond
            }

            return render_with_global_data(request, 'fimcoplatform/interests.html', context)

        elif interest_type == '7yr-bond':
            seven_year_t_bond = Tbill.objects.filter(type='7year').values('record_datetime', 'weighted_avg_price_success')
            context = {
                'type': '7-year Treasury bond rate',
                'data': seven_year_t_bond
            }

            return render_with_global_data(request, 'fimcoplatform/interests.html', context)

        elif interest_type == '10yr-bond':
            ten_year_t_bond = Tbill.objects.filter(type='10year').values('record_datetime', 'weighted_avg_price_success')
            context = {
                'type': '10-year Treasury bond rate',
                'data': ten_year_t_bond
            }

            return render_with_global_data(request, 'fimcoplatform/interests.html', context)

        elif interest_type == '15yr-bond':
            five_ten_year_t_bond = Tbill.objects.filter(type='15year').values('record_datetime', 'weighted_avg_price_success')
            context = {
                'type': '15-year Treasury bond rate',
                'data': five_ten_year_t_bond
            }

            return render_with_global_data(request, 'fimcoplatform/interests.html', context)

        elif interest_type == 'libor':
            libor = LiborRate.objects.all()
            context = {
                'type': 'USD libor Rate',
                'data': libor
            }

            return render_with_global_data(request, 'fimcoplatform/interests.html', context)

        else:
            pass

    if request.POST:
        # TODO implement notification
        start = request.POST['from']
        end = request.POST['to']
        interest_type = request.POST['type']
        if interest_type == 'overnight':
            on = OvernightInterest.objects.filter(date__range=[start, end])
            return render_with_global_data(request, 'fimcoplatform/interests.html', {'data': on})
        elif interest_type == 'bill':
            tb = Tbill.objects.filter(date__range=[start, end])
            return render_with_global_data(request, 'fimcoplatform/interests.html', {'data': tb})
        elif interest_type == 'bond':
            td = Tbond.objects.filter(date__range=[start, end])
            return render_with_global_data(request, 'fimcoplatform/interests.html', {'data': td})
        elif interest_type == 'libor':
            lr = LiborRate.objects.filter(date__range=[start, end])
            return render_with_global_data(request, 'fimcoplatform/interests.html', {'data': lr})
        else:
            pass

    ovi = OvernightInterest.objects.filter(record_datetime__date=datetime.date.today())\
        .values('current_rate', 'record_datetime', 'weighted_avg_rate', 'prev_rate', 'prev_rate_timestamp')

    ovi_dto = OvernightRateDto(
        ovi.record_datetime,
        ovi.prev_rate_timestamp,
        ovi.weighted_avg_rate,
        ovi.prev_rate
    )
    ovi_table = [ovi_dto]

    one_month_t_bill = Tbill.objects.filter(record_datetime__date=datetime.date.today(), type='1month')
    three_month_t_bill = Tbill.objects.filter(record_datetime__date=datetime.date.today(), type='3month')
    six_month_t_bill = Tbill.objects.filter(record_datetime__date=datetime.date.today(), type='6month')
    one_year_t_bill = Tbill.objects.filter(record_datetime__date=datetime.date.today(), type='1year')

    t_bill_table = {
        '1-month': one_month_t_bill,
        '3-month': three_month_t_bill,
        '6-month': six_month_t_bill,
        '1-year': one_year_t_bill
    }

    two_year_t_bond = Tbond.objects.filter(record_datetime__date=datetime.date.today(), type='2year')
    five_year_t_bond = Tbond.objects.filter(record_datetime__date=datetime.date.today(), type='5year')
    seven_year_t_bond = Tbond.objects.filter(record_datetime__date=datetime.date.today(), type='7year')
    ten_year_t_bond = Tbond.objects.filter(record_datetime__date=datetime.date.today(), type='10year')
    five_ten_year_t_bond = Tbond.objects.filter(record_datetime__date=datetime.date.today(), type='15year')

    t_bond_table = {
        '2-years': two_year_t_bond,
        '5-years': five_year_t_bond,
        '7-years': seven_year_t_bond,
        '10-years': ten_year_t_bond,
        '15-years': five_ten_year_t_bond
    }

    libor_table = LiborRate.objects.filter(created_on__date=datetime.date.today())

    context = {
        'overnight': ovi_table,
        'bill': t_bill_table,
        'bond': t_bond_table.items(),
        'libor': libor_table
    }
    return render_with_global_data(request, 'fimcoplatform/interests.html', {'data': context})


def shares_view(request):
    if request.GET:
        stock = request.GET['stock']
        # get_data = call API for dse and pass stock as filter appendix 11
        # return render_with_global_data(request, 'fimcoplatform/shares.html', {'data': get_data})
    if request.POST:
        # TODO implement notification
        start = request.POST['from']
        end = request.POST['to']
        stock = request.POST['stock']
        # post_data = call API for dse and pass start, end and stock as filter
        # return render_with_global_data(request, 'fimcoplatform/shares.html', {'data': post_data})
    # call API for dse and get all stocks appendix 10
    return render_with_global_data(request, 'fimcoplatform/shares.html', {})


def macro_data_view(request):
    if request.GET:
        duration = request.GET['duration']
        # get_data = call API for dse and pass duration as filter
        # return render_with_global_data(request, 'fimcoplatform/macro.html', {'data': get_data})
    if request.POST:
        # TODO implement notification
        start = request.POST['from']
        end = request.POST['to']
        duration = request.POST['duration']
        # post_data = call API for dse and pass start, end and duration as filter
        # return render_with_global_data(request, 'fimcoplatform/macro.html', {'data': post_data})
    # call API for dse and get summary appendix 13A and 13B
    return render_with_global_data(request, 'fimcoplatform/macro.html', {})


def auction_view(request):
    if request.GET:
        auction = request.GET['auction']
        # get_data = call API for bot and pass auction as filter
        # return render_with_global_data(request, 'fimcoplatform/auctions.html', {'data': get_data})
    if request.POST:
        # TODO implement notification
        start = request.POST['from']
        end = request.POST['to']
        auction = request.POST['auction']
        # post_data = call API for dse and pass start, end and auction as filter
        # return render_with_global_data(request, 'fimcoplatform/auctions.html', {'data': post_data})
    # call API for bot and get auctions for t-bills and t-bonds
    return render_with_global_data(request, 'fimcoplatform/macro.html', {})
