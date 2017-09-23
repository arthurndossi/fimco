from django.contrib.auth.decorators import login_required
from django.core.serializers import json
from django.http import JsonResponse
from django.shortcuts import render, redirect


# class RatesTable:
#     def __init__(self, duration, current_date, previous_date, high_date, low_date, change):
#         self.duration = duration
#         self.currentDate = current_date
#         self.previousDate = previous_date
#         self.highDate = high_date
#         self.lowDate = low_date
#         self.change = change


# @login_required
from django.template.response import TemplateResponse
from djpjax import pjax


@login_required
def admin(request):
    if request.user is not None and request.user.is_authenticated():
        return render(request, 'pochi/admin.html', {})
    else:
        return redirect('login')


def statements(request):
    return render(request, 'pochi/statements.html', {})


def pochi2pochi(request):
    return render(request, 'pochi/pochi2pochi.html', {})


def withdrawal(request):
    return render(request, 'pochi/withdrawal.html', {})


def deposit(request):
    return render(request, 'pochi/deposit.html', {})


@login_required
def markets(request):
    if request.user is not None and request.user.is_authenticated():
        return render(request, 'pochi/markets.html', {})
    else:
        return redirect('login')


def exchange_rates(request):
    # if request.user is not None and request.user.is_authenticated():
    return render(request, 'pochi/exchange.html', {})
    # else:
    #     return redirect('login')


@pjax("all_rates")
def interest_rates(request):
    # if request.user is not None and request.user.is_authenticated():
    interests = {
        "T-Bill": [
            {
                "duration": "1-month",
                "currentDate": "08/09/2017",
                "previousDate": "07/09/2017",
                "highDate": "02/09/2017",
                "lowDate": "04/09/2017",
                "change": "200"
            },
            {
                "duration": "3-months",
                "currentDate": "08/09/2017",
                "previousDate": "07/09/2017",
                "highDate": "02/09/2017",
                "lowDate": "04/09/2017",
                "change": "200"
            },
            {
                "duration": "6-months",
                "currentDate": "08/09/2017",
                "previousDate": "07/09/2017",
                "highDate": "02/09/2017",
                "lowDate": "04/09/2017",
                "change": "200"
            },
            {
                "duration": "1-year",
                "currentDate": "08/09/2017",
                "previousDate": "07/09/2017",
                "highDate": "02/09/2017",
                "lowDate": "04/09/2017",
                "change": "200"
            }
        ],
        "T-Bond": [
            {
                "duration": "2-years",
                "currentDate": "08/09/2017",
                "previousDate": "07/09/2017",
                "highDate": "02/09/2017",
                "lowDate": "04/09/2017",
                "change": "200"
            },
            {
                "duration": "5-years",
                "currentDate": "08/09/2017",
                "previousDate": "07/09/2017",
                "highDate": "02/09/2017",
                "lowDate": "04/09/2017",
                "change": "200"
            },
            {
                "duration": "7-years",
                "currentDate": "08/09/2017",
                "previousDate": "07/09/2017",
                "highDate": "02/09/2017",
                "lowDate": "04/09/2017",
                "change": "200"
            },
            {
                "duration": "10-years",
                "currentDate": "08/09/2017",
                "previousDate": "07/09/2017",
                "highDate": "02/09/2017",
                "lowDate": "04/09/2017",
                "change": "200"
            },
            {
                "duration": "15-years",
                "currentDate": "08/09/2017",
                "previousDate": "07/09/2017",
                "highDate": "02/09/2017",
                "lowDate": "04/09/2017",
                "change": "200"
            }
        ],
        "USD-LIBOR": [
            {
                "duration": "overnight",
                "currentDate": "08/09/2017",
                "previousDate": "07/09/2017",
                "highDate": "02/09/2017",
                "lowDate": "04/09/2017",
                "change": "200"
            },
            {
                "duration": "1-month",
                "currentDate": "08/09/2017",
                "previousDate": "07/09/2017",
                "highDate": "02/09/2017",
                "lowDate": "04/09/2017",
                "change": "200"
            },
            {
                "duration": "2-months",
                "currentDate": "08/09/2017",
                "previousDate": "07/09/2017",
                "highDate": "02/09/2017",
                "lowDate": "04/09/2017",
                "change": "200"
            },
            {
                "duration": "3-months",
                "currentDate": "08/09/2017",
                "previousDate": "07/09/2017",
                "highDate": "02/09/2017",
                "lowDate": "04/09/2017",
                "change": "200"
            },
            {
                "duration": "6-months",
                "currentDate": "08/09/2017",
                "previousDate": "07/09/2017",
                "highDate": "02/09/2017",
                "lowDate": "04/09/2017",
                "change": "200"
            },
            {
                "duration": "12-months",
                "currentDate": "08/09/2017",
                "previousDate": "07/09/2017",
                "highDate": "02/09/2017",
                "lowDate": "04/09/2017",
                "change": "200"
            }
        ]
    }
    overnight = {
        "currentDate": "08/09/2017",
        "previousDate": "07/09/2017",
        "highDate": "02/09/2017",
        "lowDate": "04/09/2017",
        "change": "200",
    }
    return TemplateResponse(request, 'pochi/interests.html', {'interests': interests, 'overnight': overnight})
    # else:
    #     return redirect('login')


def share_prices(request):
    # if request.user is not None and request.user.is_authenticated():
        companies = [
            {
                "symbol": "A",
                "companyName": "Acacia Mining Plc.",
                "time": "13:08:52",
                "last": "1300",
                "opening": "1500",
                "change": "200",
                "percent": "13.7",
            },
            {
                "symbol": "I",
                "companyName": "IPP Media",
                "time": "13:08:52",
                "last": "812",
                "opening": "800",
                "change": "-12",
                "percent": "-12.3",
            },
            {
                "symbol": "TCC",
                "companyName": "Tanzania Cigarette Co.",
                "time": "13:08:52",
                "last": "535",
                "opening": "513",
                "change": "-22",
                "percent": "-4.1",
            },
            {
                "symbol": "TBL",
                "companyName": "Tanzania Breweries Ltd.",
                "time": "13:08:52",
                "last": "4560",
                "opening": "5670",
                "change": "1110",
                "percent": "21.2",
            }
        ]
        return render(request, 'pochi/shares.html', {'companies': companies})
    # else:
        # return redirect('login')


def stocks(request):
    # if request.user is not None and request.user.is_authenticated():
        markets = [
            {
                "name": "Acacia Mining Plc.",
                "sector": "Mining",
                "change": "-18.3%"
            },
            {
                "name": "IPP Media",
                "sector": "Media",
                "change": "13%"
            },
            {
                "name": "Tanzania Cigarette Co.",
                "sector": "Manufacturing",
                "change": "2.2%"
            },
            {
                "name": "Tanzania Breweries Ltd.",
                "sector": "Manufacturing",
                "change": "21.2%"
            },
            {
                "name": "Vodacom Tanzania Ltd.",
                "sector": "Telecommunications",
                "change": "18.2%"
            }
        ]

        currencies = [
            {
                "name": "USD/TZS",
                "exchange": "2242",
                "change": "1.7%"
            },
            {
                "name": "GBP/TZS",
                "exchange": "2971.86",
                "change": "3.1%"
            },
            {
                "name": "EUR/TZS",
                "exchange": "2676.61",
                "change": "1.4%"
            },
            {
                "name": "ZAR/TZS",
                "exchange": "172.24",
                "change": "-2.8%"
            },
            {
                "name": "KES/TZS",
                "exchange": "21.77",
                "change": "1.3%"
            }
        ]

        commodities = [
            {
                "name": "GOLD",
                "price": "1554",
                "change": "1.3%"
            },
            {
                "name": "OIL",
                "price": "54",
                "change": "2.1%"
            },
            {
                "name": "DIAMOND",
                "price": "2104",
                "change": "3.4%"
            },
            {
                "name": "TANZANITE",
                "price": "2372",
                "change": "4.8%"
            },
            {
                "name": "GAS",
                "price": "30",
                "change": "4.2%"
            }
        ]
        return render(request, 'pochi/stock.html', {'markets': markets, 'currencies': currencies, 'commodities': commodities})
    # else:
    #     return redirect('login')


def macro_data(request):
    # if request.user is not None and request.user.is_authenticated():
        macros = {
            "GDP": {
                "quarterly": {},
                "annual": {}
            },
            "Inflation": {
                "monthly": {},
                "annual": {}
            },
            "Imports": {
                "monthly": {},
                "annual": {}
            },
            "Exports": {
                "monthly": {},
                "annual": {}
            },
            "Current Account Deficit": {
                "monthly": {},
                "annual": {}
            },
            "National Debt": {
                "Internal": {
                    "monthly": {},
                    "annual": {}
                },
                "External": {
                    "monthly": {},
                    "annual": {}
                }
            },
            "Private Sector Growth": {
                "monthly": {},
                "annual": {}
            },
        }

        return render(request, 'pochi/macros.html', {"macros": macros})
    # else:
    #     return redirect('login')


def auction_data(request):
    # if request.user is not None and request.user.is_authenticated():
        return render(request, 'pochi/auction.html', {})
    # else:
    #     return redirect('login')


def commodity_prices(request):
    # if request.user is not None and request.user.is_authenticated():
        return render(request, 'pochi/commodities.html', {})
    # else:
    #     return redirect('login')


def notifications(request):
    if request.user is not None and request.user.is_authenticated():
        return render(request, 'pochi/messages.html', {})
    else:
        return redirect('login')


def edit_profile(request):
    if request.user is not None and request.user.is_authenticated():
        return render(request, 'profile.html', {})
    else:
        return redirect('login')


def lock(request):
    if request.user is not None and request.user.is_authenticated():
        return render(request, 'pochi/lock.html', {})
    else:
        return redirect('login')


def rates(request):
    return render(request, 'pochi/rate.html', {})
