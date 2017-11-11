import datetime
import json

from django.contrib.auth.decorators import login_required
from django.db.models import Max, Min
from django.http import JsonResponse
from django.views import View

from fimco.core.utils import render_with_global_data
from .models import ExchangeRates, OvernightInterest, Tbill, Tbond, LiborRates


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
    return render_with_global_data(request, 'fimcoplatform/'+page+'.html', {})


def exchange_view(request):
    data = ExchangeRates.objects.filter(created_on__date=datetime.date.today()) \
        .annotate(day_high=Max('current_rate'), day_low=Min('current_rate'))
    if request.GET:
        value = request.GET['currency']
        data = ExchangeRates.objects.filter(created_on__date=datetime.date.today(), counter_currency=value) \
            .annotate(day_high=Max('current_rate'), day_low=Min('current_rate'))
        return render_with_global_data(request, 'fimcoplatform/exchange.html', {'data': data})

    if request.POST:
        # TODO implement notification
        start = request.POST['from']
        end = request.POST['to']
        value = request.POST['currency']
        data = ExchangeRates.objects.filter(date__range=[start, end], counter_currency=value) \
            .annotate(day_high=Max('current_rate'), day_low=Min('current_rate'))
        return render_with_global_data(request, 'fimcoplatform/exchange.html', {'data': data})

    return render_with_global_data(request, 'fimcoplatform/exchange.html', {'data': data})


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
            lr = LiborRates.objects.filter(created_on__date=datetime.date.today())
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
            lr = LiborRates.objects.filter(date__range=[start, end])
            return render_with_global_data(request, 'fimcoplatform/interests.html', {'data': lr})
        else:
            pass

    on = OvernightInterest.objects.filter(created_on__date=datetime.date.today())
    tb = Tbill.objects.filter(created_on__date=datetime.date.today())
    td = Tbond.objects.filter(created_on__date=datetime.date.today())
    lr = LiborRates.objects.filter(created_on__date=datetime.date.today())
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
