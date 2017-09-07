from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


# @login_required
def admin(request):
    # if request.user is not None and request.user.is_authenticated():
        return render(request, 'admin.html', {})
    # else:
    #     return redirect('login')


def markets(request):
    # if request.user is not None and request.user.is_authenticated():
        return render(request, 'markets.html', {})
    # else:
    #     return redirect('login')


def exchange_rates(request):
    # if request.user is not None and request.user.is_authenticated():
        return render(request, 'exchange.html', {})
    # else:
    #     return redirect('login')


def interest_rates(request):
    # if request.user is not None and request.user.is_authenticated():
        return render(request, 'interests.html', {})
    # else:
    #     return redirect('login')


def share_prices(request):
    if request.user is not None and request.user.is_authenticated():
        return render(request, 'shares.html', {})
    else:
        return redirect('login')


def macro_data(request):
    if request.user is not None and request.user.is_authenticated():
        return render(request, 'macros.html', {})
    else:
        return redirect('login')


def auction_data(request):
    if request.user is not None and request.user.is_authenticated():
        return render(request, 'auction.html', {})
    else:
        return redirect('login')


def commodity_prices(request):
    if request.user is not None and request.user.is_authenticated():
        return render(request, 'commodities.html', {})
    else:
        return redirect('login')


def notifications(request):
    if request.user is not None and request.user.is_authenticated():
        return render(request, 'messages.html', {})
    else:
        return redirect('login')


def edit_profile(request):
    if request.user is not None and request.user.is_authenticated():
        return render(request, 'profile.html', {})
    else:
        return redirect('login')


def lock(request):
    if request.user is not None and request.user.is_authenticated():
        return render(request, 'lock.html', {})
    else:
        return redirect('login')


def rates(request):
    return render(request, 'rate.html', {})
