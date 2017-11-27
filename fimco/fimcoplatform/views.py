import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Max, Min
from django.http import JsonResponse
from django.views import View

from core.utils import render_with_global_data
from .models import ExchangeRate, OvernightInterest, Tbill, Tbond, LiborRate


def post(request, *args, **kwargs):
    start = request.POST['from']
    end = request.POST['to']
    table = request.POST['table']

    rows = table.objects.filter(date__range=[start, end])

    return JsonResponse(rows)


class MarketTable(View):
    model_class = []
    table_arr = []
    template_name = 'fimcoplatform/exchange.html'

    def get(self, request, *args, **kwargs):
        if type(self.table_arr) is not list:
            rows = self.table_arr
        else:
            rows = [(i, table) for i, table in enumerate(self.table_arr)]

        return render_with_global_data(request, self.template_name, {'rows': rows})


@login_required
def market_views(request, page):
    return render_with_global_data(request, 'fimcoplatform/' + page + '.html', {})


@login_required
def exchange_view(request, page):
    charts = False
    if page == 'single':
        if request.GET:
            if request.GET.get('exchangerange'):
                # TODO implement notification
                value = request.GET['currency']
                date_range = request.GET.get('exchangerange')
                start, end = date_range.split(' - ')
                start = datetime.datetime.strptime(start, '%m/%d/%Y').strftime('%Y-%m-%d')
                end = datetime.datetime.strptime(end, '%m/%d/%Y').strftime('%Y-%m-%d')

                if start != end:
                    charts = True

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
                                               {'data': data, 'charts': charts, 'array': chart_array})
            else:
                value = request.GET['currency']
                data = ExchangeRate.objects.filter(created_on__date='2017-11-19', counter_currency=value) \
                    .annotate(day_high=Max('current_rate'), day_low=Min('current_rate'))

                return render_with_global_data(request, 'fimcoplatform/single_exchange.html',
                                               {'data': data, 'charts': charts})
        else:
            pass
    table = ExchangeRate.objects.filter(modified_on='2017-11-23')
    last_month = datetime.datetime.today() - datetime.timedelta(days=30)
    data = ExchangeRate.objects.filter(modified_on__gte=last_month, counter_currency='GBP')

    data_list = []
    label_list = []
    for row in data:
        temp_label = row.modified_on
        temp_data = row.current_rate
        label_list.append(temp_label.strftime('%d/%m/%Y'))
        data_list.append(str(temp_data))

    for single_obj in table:
        currency = single_obj.counter_currency
        list_data = ExchangeRate.objects.filter(counter_currency=currency,
                                                 modified_on__gte=datetime.datetime.now()-datetime.timedelta(days=15))\
            .values('current_rate')
        values_list = []
        for json in list_data:
            values_list.append(json['current_rate'])
        numeric_array = [float(decimal_value) for decimal_value in values_list]
        required_array = numeric_array[-2:]
        trends = (", ".join(repr(e) for e in required_array))
        table.annotate(day_high=Max('current_rate'), day_low=Min('current_rate'))

    chart_array = {'labels': label_list, 'data': data_list}

    return render_with_global_data(request, 'fimcoplatform/exchange.html',
                                   {'data': table, 'array': chart_array})


@login_required
def interests_view(request):
    if request.GET:
        interest_type = request.GET['type']
        if interest_type == 'overnight':
            on = OvernightInterest.objects.filter(created_on__date=datetime.date.today())
            return render_with_global_data(request, 'fimcoplatform/interests.html', {'data': on})
        elif interest_type == 'bill':
            tb = Tbill.objects.filter(created_on__date=datetime.date.today())
            return render_with_global_data(request, 'fimcoplatform/interests.html', {'data': tb})
        elif interest_type == 'bond':
            td = Tbond.objects.filter(created_on__date=datetime.date.today())
            return render_with_global_data(request, 'fimcoplatform/interests.html', {'data': td})
        elif interest_type == 'libor':
            lr = LiborRate.objects.filter(created_on__date=datetime.date.today())
            return render_with_global_data(request, 'fimcoplatform/interests.html', {'data': lr})
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

    on = OvernightInterest.objects.filter(created_on__date=datetime.date.today())
    tb = Tbill.objects.filter(created_on__date=datetime.date.today())
    td = Tbond.objects.filter(created_on__date=datetime.date.today())
    lr = LiborRate.objects.filter(created_on__date=datetime.date.today())
    context = {
        'overnight': on,
        'bill': tb,
        'bond': td,
        'libor': lr
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
