from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.response import TemplateResponse

from .models import Transactions


@login_required
def admin(request):
    if request.user is not None and request.user.is_authenticated():
        return render(request, 'pochi/admin.html', {})
    else:
        return redirect('login')


def statements(request):
    first_name = 'Anonymous'
    last_name = None
    try:
        trans = Transactions.objects.get(user=request.user)
        full_name = trans.user.get_full_name()
        if full_name:
            first_name = full_name.split()[0]
            last_name = full_name.split()[1]
    except Transactions.DoesNotExist:
        trans = None

    context = {
        "first": first_name, "last": last_name, "trans": trans
    }
    return render(request, 'pochi/statements.html', context)


def account(request):
    return render(request, 'pochi/account.html', {})


def p2p(request):
    try:
        bal = Transactions.objects.filter(user=request.user).latest('trans_timestamp').open_bal
    except Transactions.DoesNotExist:
        bal = 0
    if request.method == "POST":
        phone = request.POST['phone'].strip()
        amount = request.POST['amount']
        trans = Transactions(user=request.user, msisdn=phone, amount=amount, type='P', open_bal=bal)
        trans.save()
        # TODO
        # Call API
        resp = {
            'status': 'success',
            'msg': 'TZS ' + amount + ' has been transferred to ' + phone + '.'
        }
        return JsonResponse(resp)
    else:
        return JsonResponse({'status': 'fail'})


def withdraw(request):
    try:
        bal = Transactions.objects.filter(user=request.user).latest('trans_timestamp').open_bal
    except Transactions.DoesNotExist:
        bal = 0
    if request.method == "POST":
        phone = request.POST['phone'].strip()
        amount = request.POST['amount']
        trans = Transactions(user=request.user, msisdn=phone, amount=amount, type='W', open_bal=bal)
        trans.save()
        resp = {
            'status': 'success',
            'msg': 'TZS ' + amount + ' has been deducted from your account.'
        }
        return JsonResponse(resp)
    else:
        return JsonResponse({'status': 'fail'})


def add_funds(request):
    try:
        bal = Transactions.objects.filter(user=request.user).latest('trans_timestamp').open_bal
    except Transactions.DoesNotExist:
        bal = 0
    if request.method == "POST":
        phone = request.POST['phone']
        amount = request.POST['amount']
        trans = Transactions(user=request.user, msisdn=phone, amount=amount, type='D', open_bal=bal)
        trans.save()
        resp = {
            'status': 'success',
            'msg': 'TZS ' + amount + ' has been added to your account.'
        }
        return JsonResponse(resp)
    else:
        return JsonResponse({'status': 'fail'})


def new_group(request):
    return render(request, 'pochi/group.html', {})


def create_group(request):
    if request.method == 'POST':
        groupName = request.POST['profileGroupName'].capitalize()
        purpose = request.POST['groupPurpose']
        member_list = request.POST['members']
        first_admin = request.POST['first']
        sec_admin = request.POST['second']
        import json
        members = json.loads(member_list)
        print (members)
        from .models import JointAccount
        group = JointAccount.objects.create(
            group_name=groupName,
            purpose=purpose,
            members=members,
            first_admin=first_admin,
            sec_admin=sec_admin
        )
        group.save()
    return render(request, 'pochi/group.html', {})


def edit_group(request):
    return render(request, 'pochi/edit_group.html', {})


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
