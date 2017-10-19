import json
import uuid

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect

from .models import Transactions, JointAccount
from fimcosite.forms import EditProfileForm


@login_required
def home(request):
    json_data = open('C:/Users/MADS/PycharmProjects/FIMCO/fimco/pochi/static/pochi/statements.json', 'r')
    data = json.load(json_data)
    try:
        group_set = JointAccount.objects.filter(pochi_id=request.user.profile.pochi_id)
    except JointAccount.DoesNotExist:
        group_set = ''
    return render(request, 'pochi/home.html', {'statements': data, 'groups': group_set})


@login_required
def admin(request):
    if request.user is not None and request.user.is_authenticated():
        return render(request, 'pochi/admin.html', {})
    else:
        return redirect('login')


@login_required
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


@login_required
def account(request):
    return render(request, 'pochi/account.html', {})


@login_required
def view_profile(request):
    user = request.user
    form = EditProfileForm(request.POST or None, initial={
        'fName': user.first_name,
        'lName': user.last_name,
        'phone': user.username,
        'email': user.email,
        'dob': user.profile.dob,
        'gender': user.profile.gender,
        'client_id': user.profile.client_id,
        'bot_cds': user.profile.bot_cds,
        'dse_cds': user.profile.dse_cds
    })
    form_data = {
        'fName': user.first_name,
        'lName': user.last_name,
        'phone': user.username,
        'email': user.email,
        'dob': user.profile.dob,
        'gender': user.profile.gender,
        'client_id': user.profile.client_id,
        'bot_cds': user.profile.bot_cds,
        'dse_cds': user.profile.dse_cds
    }
    obj = JointAccount.objects.filter(pochi_id=user.profile.pochi_id)
    context = {
        'pForm': form,
        'data': form_data,
        'groups': obj
    }

    return render(request, "pochi/profile.html", context)


@login_required
def edit_profile(request):
    user = request.user
    form = EditProfileForm(request.POST, request.FILES)
    if request.method == 'POST':
        if form.is_valid():
            user.first_name = request.POST['fName']
            user.last_name = request.POST['lName']
            user.email = request.POST['email']
            user.username = request.POST['phone']
            user.profile.dob = request.POST['dob']
            user.profile.gender = request.POST['gender']
            user.profile.avatar = request.FILES['avatar']
            user.profile.client_id = request.POST['id_number']
            user.profile.bot_cds = request.POST['bot_account']
            user.profile.dse_cds = request.POST['dse_account']
            user.save()
            user.profile.save()

            return redirect(view_profile)
    else:
        return redirect(edit_profile)


@login_required
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


@login_required
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


@login_required
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


@login_required
def new_group(request):
    return render(request, 'pochi/group.html', {})


@login_required
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
            pochi_id=uuid.uuid4().hex[:6].upper(),
            group_name=groupName,
            purpose=purpose,
            members=members,
            first_admin=first_admin,
            sec_admin=sec_admin
        )
        group.save()
    return render(request, 'pochi/group.html', {})


@login_required
def edit_group(request):
    return render(request, 'pochi/edit_group.html', {})


@login_required
def notifications(request):
    return render(request, 'pochi/messages.html', {})


@login_required
def lock(request):
    return render(request, 'pochi/lock.html', {})
