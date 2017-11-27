import datetime
import uuid

from core.utils import render_with_global_data
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect
from fimcosite.forms import EditProfileForm
from fimcosite.models import Account, Profile

from .models import Transaction, Group, GroupMember, ExternalAccount, Ledger, BalanceSnapshot, Charge, CashOut


@login_required
def home(request):
    profile = request.user.profile
    group_members_obj = []
    try:
        group_account_obj = GroupMember.objects.filter(profile_id=profile.profile_id).only('group_account')
        for group in group_account_obj:
            try:
                grp_name = Group.objects.get(group_account=group.group_account).name
                group_members_obj.append(grp_name)
            except Group.DoesNotExist:
                pass

    except GroupMember.DoesNotExist:
        pass
    return render_with_global_data(request, 'pochi/home.html', {'groups': group_members_obj})


@login_required
def admin(request):
    balance_data = BalanceSnapshot.objects.all()
    return render_with_global_data(request, 'pochi/admin.html', {'data': balance_data})


@login_required
def statement(request):
    user_accounts = trans = None
    profile = request.user.profile
    try:
        user_accounts = ExternalAccount.objects.filter(profile_id=profile.profile_id)
    except ExternalAccount.DoesNotExist:
        user_accounts = user_accounts

    if request.GET:
        if request.GET.get('range'):
            date_range = request.GET.get('range')
            start, end = date_range.split(' - ')
            start = datetime.datetime.strptime(start, '%m/%d/%Y').strftime('%Y-%m-%d')
            end = datetime.datetime.strptime(end, '%m/%d/%Y').strftime('%Y-%m-%d')
            trans = Transaction.objects.filter(profile_id=profile.profile_id, fulltimestamp__range=[start, end])
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
    obj = GroupMember.objects.filter(profile_id=user.profile.profile_id)
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


@transaction.atomic
def fund_transfer(request, service, ext_wallet, channel, profile_id, src, dest, bal, amount, overdraft=0):
    try:
        close_bal = Ledger.objects.last().cbal
    except Ledger.DoesNotExist:
        close_bal = 0

    try:
        charges = Charge.objects.get(service=service).charge
    except Ledger.DoesNotExist:
        charges = 0

    if service == 'P2P':
        total = amount + charges
        if bal > total or overdraft:
            Transaction.objects.create(
                profile_id=profile_id,
                account=src,
                msisdn=request.user.username,
                external_walletid=ext_wallet,
                service=service,
                dest_account=dest,
                amount=amount
            )
            Ledger.objects.create(
                trans_type='DEBIT',
                service=service,
                amount=amount,
                obal=close_bal,
                cbal=close_bal - amount
            )
            Ledger.objects.create(
                trans_type='CREDIT',
                service=service,
                amount=amount,
                obal=close_bal,
                cbal=close_bal + amount
            )
    elif service == 'WITHDRAW':
        if amount <= bal or overdraft:
            Transaction.objects.create(
                profile_id=profile_id,
                account=src,
                msisdn=request.user.username,
                external_walletid=ext_wallet,
                service=service,
                channel=channel,
                dest_account=dest,
                amount=amount
            )
            Ledger.objects.create(
                profile_id=profile_id,
                trans_type='DEBIT',
                service=service,
                amount=amount,
                obal=close_bal,
                cbal=close_bal - amount
            )
            CashOut.objects.create(
                ext_entity=channel,
                ext_acc_no=ext_wallet,
                amount=amount
            )
    elif service == 'DEPOSIT':
        Transaction.objects.create(
            profile_id=profile_id,
            account=dest,
            msisdn=request.user.username,
            external_walletid=ext_wallet,
            service='DEPOSIT',
            amount=amount
        )
        Ledger.objects.create(
            profile_id=profile_id,
            trans_type='CREDIT',
            service=service,
            amount=amount,
            obal=close_bal,
            cbal=close_bal + amount
        )


@login_required
def pochi2pochi(request):
    profile = request.user.profile
    extras = None
    try:
        acc = Account.objects.get(profile_id=profile.profile_id)
        bal = acc.balance
        ov = acc.allow_overdraft
    except Account.DoesNotExist:
        acc = None
        bal = ov = 0

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
                'allow_overdraft': ov,
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
        src_account = request.POST['account_no']
        name = request.POST['name']
        ext_wallet = request.POST['ext_wallet']
        dest_account = request.POST['dest_acc']
        dest_profile_id = request.POST['dest_profile_id']
        ov = request.POST['overdraft']
        amount = request.POST['amount']
        amount = float(amount)
        bal = request.POST['open_bal']
        bal = float(bal)
        profile = request.user.profile
        src_profile_id = profile.profile_id

        fund_transfer('P2P', ext_wallet, 'NA', src_profile_id, src_account, dest_account, bal, amount, ov)

        src_account = dest_account = None
        while src_account is None:
            try:
                src_account = Account.objects.get(profile_id=src_profile_id)
                src_account.balance -= float(amount)
                src_account.save()
            except:
                pass
        while dest_account is None:
            try:
                dest_account = Account.objects.get(profile_id=dest_profile_id)
                dest_account.balance += float(amount)
                dest_account.save()
            except:
                pass

        resp = {
            'status': 'success',
            'msg': 'TZS' + str(amount) + ' has been transferred from your account to ' + name + '.'
        }
        return JsonResponse(resp)


@login_required
def withdraw(request):
    profile = request.user.profile
    profile_id = profile.profile_id
    try:
        external_account = ExternalAccount.objects.filter(profile_id=profile_id)
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
                _account = Account.objects.get(profile_id=profile_id)
                src_account = _account.account
                bal = _account.balance
                ov = _account.allow_overdraft

                fund_transfer('WITHDRAW', 'NA', institution_name, profile_id, src_account, dest_acc_num, bal, amount, ov)

                if amount <= bal:
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
    src_profile_id = profile.profile_id
    if request.method == "POST":
        amount = float(request.POST['amount'])

        try:
            _account = Account.objects.get(profile_id=profile.profile_id)
            bal = _account.balance
            dest_account = _account.account

            fund_transfer('DEPOSIT', 'NA', 'NA', src_profile_id, 'NA', dest_account, bal, amount)

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
        GroupMember.objects.create(
            group_account=grp_acc,
            profile_id=first_admin,
            admin=1
        )
        for member in members:
            is_admin = 0
            if member == sec_admin:
                is_admin = 1
            GroupMember.objects.create(
                group_account=grp_acc,
                profile_id=member,
                admin=is_admin
            )
            # import httplib, urllib
            # conn = httplib.HTTPSConnection("api.pushover.net:443")
            # conn.request("POST", "/1/messages.json",
            #              urllib.urlencode({
            #                  "token": "APP_TOKEN",
            #                  "user": "USER_KEY",
            #                  "message": "hello world",
            #              }), {"Content-type": "application/x-www-form-urlencoded"})
            # conn.getresponse()
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
            GroupMember.objects.create(group_account=grp_acc, profile_id=members)
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
