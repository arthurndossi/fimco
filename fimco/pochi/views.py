import uuid

from chartit import DataPool, Chart
from core.utils import render_with_global_data
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect
from fimcosite.forms import EditProfileForm
from fimcosite.models import Account, Profile

from .models import Transaction, Group, GroupMembers, ExternalAccount, Ledger, BalanceSnapshot


@login_required
def home(request):
    profile = request.user.profile
    group_members_obj = []
    try:
        group_account_obj = GroupMembers.objects.filter(profile_id=profile.profile_id).only('group_account')
        for group in group_account_obj:
            try:
                grp_name = Group.objects.get(group_account=group.group_account).name
                group_members_obj.append(grp_name)
            except Group.DoesNotExist:
                pass

    except GroupMembers.DoesNotExist:
        pass
    return render_with_global_data(request, 'pochi/home.html', {'groups': group_members_obj})


@login_required
def admin(request):
    balancedata = DataPool(
        series=[{
            'options': {
                'source': BalanceSnapshot.objects.all()
            },
            'terms': [
                {'Date': 'fulltimestamp'},
                {'Balance': 'closing_balance'},
                {'Interest': 'bonus_closing_balance'}
            ]
        }]
    )

    chart = Chart(
        datasource=balancedata,
        series_options=[{
            'options': {
                'type': 'line',
                'stacking': False
            },
            'terms': {
                'Date': [
                    'Balance',
                    'Interest'
                ]
            }
        }],
        chart_options={
            'title': {
                'text': 'BALANCE & INTEREST SUMMARY'
            },
            'xAxis': {
                'title': {
                    'text': 'Date'
                }
            }
        }
    )
    return render_with_global_data(request, 'pochi/admin.html', {'balanceChart': chart})


@login_required
def statement(request):
    user_accounts = trans = None
    profile = request.user.profile
    try:
        user_accounts = ExternalAccount.objects.filter(profile_id=profile.profile_id)
    except ExternalAccount.DoesNotExist:
        user_accounts = user_accounts
    if request.GET.get('channel'):
        selected_account = request.GET.get('channel')
        trans = Transaction.objects.filter(profile_id=profile.profile_id, channel=selected_account)
    else:
        try:
            trans = Transaction.objects.filter(profile_id=request.user.profile.profile_id)
        except Transaction.DoesNotExist:
            trans = trans

    context = {
        "profile": profile,
        "accounts": user_accounts,
        "transactions": trans,
    }
    return render_with_global_data(request, 'pochi/statement.html', context)


@login_required
def account(request):
    if request.method == 'POST':
        user = request.user.profile
        institution = request.POST['institution']
        name = request.POST['name'].upper()
        nickname = request.POST['nickname']
        account_num = request.POST['account']
        account_type = request.POST['type']
        ExternalAccount.objects.create(
            profile_id=user.profile_id,
            account_name=name,
            account_number=account_num,
            nickname=nickname,
            institution_name=institution,
            account_type=account_type
        )
        messages.success(
            request,
            'You have successfully added '+nickname+' account!'
        )
    return render_with_global_data(request, 'pochi/account.html', {})


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
    obj = GroupMembers.objects.filter(profile_id=user.profile.profile_id)
    context = {
        'pForm': form,
        'data': form_data,
        'groups': obj
    }

    return render_with_global_data(request, "pochi/profile.html", context)


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
def pochi2pochi(request):
    profile = request.user.profile
    extras = None
    try:
        acc = Account.objects.get(profile_id=profile.profile_id)
        bal = acc.balance
    except Account.DoesNotExist:
        acc = None
        bal = 0

    if request.method == "POST":
        user_obj = user_name = dest_account = dest_profile_id = None
        if request.POST['dest_mobile']:
            phone = request.POST['dest_mobile']
            try:
                user_obj = User.objects.select_related('profile').get(username=phone)
                dest_profile_id = user_obj.profile.profile_id
                user_name = user_obj.get_full_name()
            except Profile.DoesNotExist:
                user_name = None

            try:
                dest_account = Account.objects.get(profile_id=dest_profile_id).account
            except Account.DoesNotExist:
                dest_account = None

        elif request.POST['dest_account']:
            dest_account = request.POST['dest_account']

            try:
                dest_profile_id = Account.objects.get(account=dest_account).profile_id
            except Account.DoesNotExist:
                dest_profile_id = None

            try:
                user_obj = User.objects.select_related('profile').filter(profile_id=dest_profile_id)
                user_name = user_obj.get_full_name()
            except Profile.DoesNotExist:
                user_name = None

        amount = request.POST['amount']
        amount = float(amount)

        if amount <= bal and user_name is not None:
            messages.info(
                request,
                'You are about to transfer TZS' + str(
                    amount) + ' to ' + user_name + '.\r Proceed with the transfer?'
            )
            extras = {
                'dest_account': dest_account,
                'dest_profile_id': dest_profile_id,
                'user_object': user_obj,
                'amount': amount,
                'open_bal': bal
            }
        elif amount > bal:
            messages.error(
                request,
                'You do not have enough balance to make to transfer TZS'+str(amount)+' to '+user_name+'.'
            )
        elif user_name is None:
            messages.error(
                request,
                'This user is not registered with a pochi account!'
            )

    context = {
        'extra': extras,
        'account': acc
    }
    return render_with_global_data(request, 'pochi/pochi2pochi.html', context)


def process_p2p(request):
    if request.POST:
        account_no = request.POST['account_no']
        name = request.POST['name']
        msisdn = request.POST['msisdn']
        ext_wallet = request.POST['ext_wallet']
        dest_account = request.POST['dest_acc']
        dest_profile_id = request.POST['dest_profile_id']
        amount = request.POST['amount']
        amount = float(amount)
        open_bal = request.POST['open_bal']
        open_bal = float(open_bal)
        profile = request.user.profile
        Transaction.objects.create(
            profile_id=profile.profile_id,
            account=account_no,
            msisdn=msisdn,
            external_walletid=ext_wallet,
            service='P2P',
            dest_account=dest_account,
            amount=amount
        )
        Ledger.objects.create(
            profile_id=profile.profile_id,
            account=account_no,
            trans_type='DEBIT',
            service='P2P',
            amount=amount,
            obal=open_bal,
            cbal=open_bal - amount
        )
        Ledger.objects.create(
            profile_id=dest_profile_id,
            account=dest_account,
            trans_type='CREDIT',
            service='P2P',
            amount=amount,
            obal=open_bal,
            cbal=open_bal + amount
        )
        src_account = Account.objects.get(profile_id=profile.profile_id)
        src_account.balance -= float(amount)
        src_account.save()
        dest_account = Account.objects.get(profile_id=dest_profile_id)
        dest_account.balance += float(amount)
        dest_account.save()
        resp = {
            'status': 'success',
            'msg': 'TZS' + str(amount) + ' has been transferred from your account to ' + name + '.'
        }
        return JsonResponse(resp)


@login_required
def withdraw(request):
    profile = request.user.profile
    try:
        external_account = ExternalAccount.objects.filter(profile_id=profile.profile_id)
        ext_acc_obj = external_account.values('nickname')
    except ExternalAccount.DoesNotExist:
        ext_acc_obj = None

    if request.method == "POST":
        if request.POST['type'] == u"BANK":
            user = request.user.profile
            institution = request.POST['institution']
            name = request.POST['name'].upper()
            nickname = request.POST['nickname']
            account_num = request.POST['account']
            account_type = request.POST['type']
            ExternalAccount.objects.create(
                profile_id=user.profile_id,
                account_name=name,
                account_number=account_num,
                nickname=nickname,
                institution_name=institution,
                account_type=account_type
            )
            messages.success(
                request,
                'You have successfully added ' + nickname + ' account!'
            )
        else:
            selected_ext_account = request.POST['ext_account']
            amount = float(request.POST['amount'])

            selected_ext_acc_obj = ExternalAccount.objects.get(nickname=selected_ext_account)
            institution_name = selected_ext_acc_obj.institution_name
            dest_acc_num = selected_ext_acc_obj.account_number

            try:
                _account = Account.objects.get(profile_id=profile.profile_id)
                user_balance = _account.balance

                if amount <= user_balance:
                    Transaction.objects.create(
                        profile_id=profile.profile_id,
                        account=_account.account,
                        msisdn=request.user.username,
                        external_walletid=_account.external_walletid,
                        service='WITHDRAW',
                        channel=institution_name,
                        dest_account=dest_acc_num,
                        amount=amount
                    )
                    Ledger.objects.create(
                        profile_id=profile.profile_id,
                        account=_account.account,
                        trans_type='DEBIT',
                        service='WITHDRAW',
                        amount=amount,
                        obal=user_balance,
                        cbal=user_balance - amount
                    )
                    _account.balance -= amount
                    _account.save()
                    messages.info(
                        request,
                        'You have successfully withdrawn TZS'+str(amount)+' to your '+selected_ext_account+' account'
                    )
                else:
                    messages.error(request, 'You have insufficient funds to withdraw money to your account!')

            except Account.DoesNotExist:
                pass

    context = {
        'external_accounts': ext_acc_obj,
    }
    return render_with_global_data(request, 'pochi/withdrawal.html', context)


@login_required
def deposit(request):
    profile = request.user.profile
    if request.method == "POST":
        amount = float(request.POST['amount'])

        try:
            _account = Account.objects.get(profile_id=profile.profile_id)
            user_balance = _account.balance
            user_account = _account.account

            Transaction.objects.create(
                profile_id=profile.profile_id,
                account=user_account,
                msisdn=request.user.username,
                external_walletid=_account.external_walletid,
                service='DEPOSIT',
                amount=amount
            )
            Ledger.objects.create(
                profile_id=profile.profile_id,
                account=_account.account,
                trans_type='CREDIT',
                service='DEPOSIT',
                amount=amount,
                obal=user_balance,
                cbal=user_balance + amount
            )
            _account.balance += amount
            _account.save()
            messages.info(
                request,
                'You have successfully deposited ' + str(amount) + ' to your account'
            )
        except Account.DoesNotExist:
            pass
    return render_with_global_data(request, 'pochi/deposit.html', {})


@login_required
def new_group(request):
    return render_with_global_data(request, 'pochi/create_group.html', {})


@login_required
def create_group(request):
    profile = request.user.profile
    import json
    if request.method == 'POST':
        groupName = request.POST['profileGroupName'].capitalize()
        member_list = request.POST['members']
        first_admin = profile.profile_id
        sec_admin = request.POST['admin']
        members = json.loads(member_list)
        grp_acc = uuid.uuid4().hex[:10].upper()
        Group.objects.create(
            group_account=grp_acc,
            name=groupName,
        )
        Account.objects.create(
            profile_id=grp_acc,
            account=grp_acc,
            nickname=groupName,
        )
        GroupMembers.objects.create(
            group_account=grp_acc,
            profile_id=first_admin,
            admin=1
        )
        for member in members:
            is_admin = 0
            if member == sec_admin:
                is_admin = 1
            GroupMembers.objects.create(
                group_account=grp_acc,
                profile_id=member,
                admin=is_admin
            )
    return render_with_global_data(request, 'pochi/create_group.html', {})


@login_required
def edit_group(request):
    return render_with_global_data(request, 'pochi/edit_group.html', {})


@login_required
def lock(request):
    return render_with_global_data(request, 'pochi/lock.html', {})


@login_required
def group_settings(request, name=None):
    return render_with_global_data(request, 'pochi/group_settings.html', {'group': name})


@login_required
def add_member(request, name=None):
    if request.POST:
        members = request.POST['option[]']
        try:
            this_group = Group.objects.get(name=name)
            grp_acc = this_group.group_account
            GroupMembers.objects.create(group_account=grp_acc, profile_id=members)
        except Account.DoesNotExist:
            pass
    return render_with_global_data(request, 'pochi/add_member.html', {'group': name})


@login_required
def group_statement(request, name=None):
    group_transactions = None
    try:
        this_group = Group.objects.get(name=name)
        grp_acc = this_group.group_account
        try:
            group_transactions = Transaction.objects.filter(account=grp_acc) \
                .values('service', 'channel', 'dest_account', 'currency', 'amount', 'charge', 'status', 'message')
        except Transaction.DoesNotExist:
            group_transactions = None
    except Account.DoesNotExist:
        pass
    return render_with_global_data(request, 'pochi/group_statement.html', {'statement': group_transactions})


@login_required
def group_profile(request, name=None):
    this_account = group_transactions = None
    try:
        this_group = Group.objects.get(name=name)
        grp_acc = this_group.group_account
        try:
            group_transactions = Transaction.objects.filter(account=grp_acc)\
                .values('service', 'channel', 'dest_account', 'currency', 'amount', 'charge', 'status', 'message')
        except Transaction.DoesNotExist:
            group_transactions = None
    except Account.DoesNotExist:
        grp_acc = None
    if grp_acc:
        try:
            this_account = Account.objects.get(account=grp_acc)
        except Account.DoesNotExist:
            this_account = None
    context = {
        'group': name,
        'account': this_account,
        'statement': group_transactions
    }
    return render_with_global_data(request, 'pochi/group_profile.html', context)
