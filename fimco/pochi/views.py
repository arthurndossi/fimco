import datetime
import uuid

from core.utils import render_with_global_data
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from fimcosite.forms import EditProfileForm
from fimcosite.models import Account, Profile

from reportlab.pdfgen import canvas

from .models import Transaction, Group, GroupMember, ExternalAccount, Ledger, BalanceSnapshot, Charge, CashOut


@login_required
def home(request):
    profile = request.user.profile
    try:
        balance_data = Account.objects.get(profile_id=profile.profile_id)
    except Account.DoesNotExist:
        balance_data = None

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

    context = {
        'profile': profile,
        'account': balance_data,
        'groups': group_members_obj
    }
    return render_with_global_data(request, 'pochi/home.html', context)


@login_required
def admin(request):
    return render_with_global_data(request, 'pochi/admin.html', {})


@login_required
def statement(request):
    trans = None
    profile = request.user.profile

    if request.GET:
        if request.GET.get('range'):
            date_range = request.GET.get('range')
            start, end = date_range.split(' - ')
            start = datetime.datetime.strptime(start, '%m/%d/%Y').strftime('%Y-%m-%d')
            end = datetime.datetime.strptime(end, '%m/%d/%Y').strftime('%Y-%m-%d')
            trans = Transaction.objects.filter(profile_id=profile.profile_id, fulltimestamp__range=[start, end])
        elif request.GET.get('channel'):
            selected_account = request.GET.get('channel')
            trans = Transaction.objects.filter(profile_id=profile.profile_id, channel=selected_account)
        elif request.GET.get('service'):
            selected_account = request.GET.get('service')
            trans = Transaction.objects.filter(profile_id=profile.profile_id, service=selected_account)
    else:
        try:
            trans = Transaction.objects.filter(profile_id=request.user.profile.profile_id)
        except Transaction.DoesNotExist:
            trans = trans

    context = {
        "profile": profile,
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
def fund_transfer(request, service, ext_wallet, channel, profile_id, src, dest, bal, amount, msisdn, overdraft=0):
    try:
        close_bal = Ledger.objects.last().c_bal
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
                msisdn=msisdn,
                external_wallet_id=ext_wallet,
                service=service,
                dest_account=dest,
                amount=amount,
                status='DONE'
            )
            Ledger.objects.create(
                trans_type='DEBIT',
                service=service,
                amount=amount,
                o_bal=close_bal,
                c_bal=close_bal - amount
            )
            Ledger.objects.create(
                trans_type='CREDIT',
                service=service,
                amount=amount,
                o_bal=close_bal,
                c_bal=close_bal + amount
            )
    elif service == 'WITHDRAW':
        if amount <= bal or overdraft:
            Transaction.objects.create(
                profile_id=profile_id,
                account=src,
                msisdn=msisdn,
                external_wallet_id=ext_wallet,
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
                o_bal=close_bal,
                c_bal=close_bal - amount
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
            msisdn=msisdn,
            external_wallet_id=ext_wallet,
            service='DEPOSIT',
            amount=amount
        )
        Ledger.objects.create(
            profile_id=profile_id,
            trans_type='CREDIT',
            service=service,
            amount=amount,
            o_bal=close_bal,
            c_bal=close_bal + amount
        )


@login_required
def pochi2pochi(request, name=None):
    this_group = None
    acc = None
    extras = None
    if name:
        bal = ov = 0
        try:
            this_group = Group.objects.get(name=name)
            this_group_account = this_group.group_account
            try:
                acc = Account.objects.get(account=this_group_account)
                ov = acc.allow_overdraft
                bal = acc.balance
            except Account.DoesNotExist:
                acc = None
        except Group.DoesNotExist:
            pass

    else:
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

            if dest_profile_id:
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
        elif amount > bal and user_name is not None:
            messages.error(
                request,
                'You do not have enough balance to make to transfer TZS'+str(amount)+' to '+user_name+'.'
            )
        elif user_name is None:
            messages.error(
                request,
                'This user is not registered with a pochi account!'
            )
    if name:
        context = {
            'group': name,
            'account': this_group,
            'extra': extras,
        }
        return render_with_global_data(request, 'pochi/group_activity.html', context)
    else:
        context = {
            'extra': extras,
            'account': acc
        }
    return render_with_global_data(request, 'pochi/pochi2pochi.html', context)


def process_g2p(request):
    if request.POST:
        src_account_no = request.POST['account_no']
        name = request.POST['name']
        group_name = request.POST['group_name']
        ext_wallet = request.POST['ext_wallet']
        dest_account_no = request.POST['dest_acc']
        dest_profile_id = request.POST['dest_profile_id']
        ov = request.POST['overdraft']
        amount = request.POST['amount']
        amount = float(amount)
        bal = request.POST['open_bal']
        bal = float(bal)
        phone = 'NA'
        src_profile_id = 'NA'

        fund_transfer(request, 'P2P', ext_wallet, 'NA', src_profile_id, src_account_no, dest_account_no, bal, amount,
                      phone, ov)

        src_account = None
        dest_account = None
        try:
            src_account = Account.objects.get(account=src_account_no)
            src_account.balance -= float(amount)
            src_account.save()
        except Account.DoesNotExist:
            pass

        try:
            dest_account = Account.objects.get(profile_id=dest_profile_id)
            dest_account.balance += float(amount)
            dest_account.save()
        except Account.DoesNotExist:
            pass

        if src_account and dest_account:
            resp = {
                'status': 'success',
                'msg': 'TZS' + str(amount) + ' has been transferred from '+group_name+' account to ' + name + '.'
            }
            return JsonResponse(resp)
        else:
            resp = {
                'status': 'fail',
                'msg': 'An invalid account was selected.'
            }
            return JsonResponse(resp)


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
        phone = request.user.username
        profile = request.user.profile
        src_profile_id = profile.profile_id

        fund_transfer(request, 'P2P', ext_wallet, 'NA', src_profile_id, src_account, dest_account, bal, amount,
                      phone, ov)

        src_account = dest_account = None
        try:
            src_account = Account.objects.get(profile_id=src_profile_id)
            src_account.balance -= float(amount)
            src_account.save()
        except Account.DoesNotExist:
            pass

        try:
            dest_account = Account.objects.get(profile_id=dest_profile_id)
            dest_account.balance += float(amount)
            dest_account.save()
        except Account.DoesNotExist:
            pass

        if src_account and dest_account:
            resp = {
                'status': 'success',
                'msg': 'TZS' + str(amount) + ' has been transferred from your account to ' + name + '.'
            }
            return JsonResponse(resp)
        else:
            resp = {
                'status': 'fail',
                'msg': 'An invalid account was selected.'
            }
            return JsonResponse(resp)


@login_required
def withdraw(request):
    profile = request.user.profile
    identifier = profile.profile_id
    phone = request.user.username
    msisdn_3 = phone[:3]

    tigo = ['065', '067', '071']
    airtel = ['068', '078']
    vodacom = ['074', '075', '076']

    if any(prefix in msisdn_3 for prefix in airtel):
        institution = 'AIRTEL MONEY'
    elif any(prefix in msisdn_3 for prefix in tigo):
        institution = 'TIGO PESA'
    elif any(prefix in msisdn_3 for prefix in vodacom):
        institution = 'M PESA'
    elif '062' in msisdn_3:
        institution = 'HALO PESA'
    elif '077' in msisdn_3:
        institution = 'HALO PESA'
    elif '073' in msisdn_3:
        institution = 'TTCL PESA'
    else:
        institution = None

    try:
        external_account = ExternalAccount.objects.filter(profile_id=identifier)
        ext_acc_obj = external_account.values('nickname')
    except ExternalAccount.DoesNotExist:
        ext_acc_obj = None

    if request.method == "POST":
        if request.POST['type'] == u"account":
            institution = request.POST['institution']
            bank_name = request.POST['name'].upper()
            nickname = request.POST['nickname']
            account_num = request.POST['account']
            account_type = request.POST['type']
            ExternalAccount.objects.create(
                profile_id=identifier,
                account_name=bank_name,
                account_number=account_num,
                nickname=nickname,
                institution_name=institution,
                account_type=account_type
            )
            messages.success(
                request,
                'You have successfully added ' + nickname + ' account!'
            )
        elif request.POST['type'] == u"mobile":
            amount = float(request.POST['amount'])

            try:
                _account = Account.objects.get(profile_id=identifier)
                pochi_id = _account.account
                bal = _account.balance
                ov = _account.allow_overdraft

                fund_transfer(request, 'WITHDRAW', 'NA', institution, identifier, pochi_id, phone, bal,
                              amount, phone, ov)

                if amount <= bal:
                    _account.balance -= amount
                    _account.save()
                    messages.info(
                        request,
                        'You have successfully withdrawn TZS' + str(
                            amount) + ' to your ' + institution + ' account'
                    )
                else:
                    messages.error(request, 'You have insufficient funds to withdraw money from your account!')

            except Account.DoesNotExist:
                pass
        elif request.POST['type'] == u"bank":
            selected_ext_account = request.POST['ext_account']
            amount = float(request.POST['amount'])

            selected_ext_acc_obj = ExternalAccount.objects.get(nickname=selected_ext_account)
            institution_name = selected_ext_acc_obj.institution_name
            dest_acc_num = selected_ext_acc_obj.account_number

            try:
                _account = Account.objects.get(profile_id=identifier)
                src_account = _account.account
                bal = _account.balance
                ov = _account.allow_overdraft

                fund_transfer(request, 'WITHDRAW', 'NA', institution_name, identifier, src_account, dest_acc_num, bal,
                              amount, phone, ov)

                if amount <= bal:
                    _account.balance -= amount
                    _account.save()
                    messages.info(
                        request,
                        'You have successfully withdrawn TZS'+str(amount)+' to your '+selected_ext_account+' account'
                    )
                else:
                    messages.error(request, 'You have insufficient funds to withdraw money from your account!')

            except Account.DoesNotExist:
                pass
    context = {
        'external_accounts': ext_acc_obj,
    }
    return render_with_global_data(request, 'pochi/withdrawal.html', context)


@login_required
def how_to_deposit(request):
    return render_with_global_data(request, 'pochi/deposit.html', {})


def deposit(request):
    message = None
    if request.method == "GET":
        amount = float(request.GET['amount'])
        if 'msisdn' in request.GET:
            phone = request.GET['msisdn']

            try:
                src_profile_id = Profile.objects.get(user__username=phone).profile_id
            except Profile.DoesNotExist:
                src_profile_id = None

            if src_profile_id:
                try:
                    _account = Account.objects.get(profile_id=src_profile_id)
                    bal = _account.balance
                    dest_account = _account.account

                    fund_transfer(request, 'DEPOSIT', 'NA', 'NA', src_profile_id, 'NA', dest_account, bal, amount, phone)

                    _account.balance += amount
                    _account.save()

                    message = 'You have successfully deposited ' + str(amount) + ' to your account'

                except Account.DoesNotExist:
                    message = 'System unavailable, Try again later!'
                    pass
            else:
                message = 'Sorry!, This phone number is not registered in the system!'
        elif 'account' in request.GET:
            this_account = request.GET['account']

            try:
                _group = Group.objects.get(group_account=this_account)
                bal = _group.balance

                fund_transfer(request, 'DEPOSIT', 'NA', 'NA', 'NA', 'NA', this_account, bal, amount, 'NA')

                _group.balance += amount
                _group.save()

                message = 'You have successfully deposited ' + str(amount) + ' to your group account'

            except Group.DoesNotExist:
                message = 'Sorry!, This account number does not belong to any group in the system!'
                pass
    return JsonResponse({'message': message})


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
    count = 0
    administrators = []
    members = []
    try:
        this_group = Group.objects.get(name=name)
        grp_acc = this_group.group_account
        count = GroupMember.objects.filter(group_account=grp_acc).count()
        admins_profile_obj = GroupMember.objects.filter(group_account=grp_acc, admin=1).only('profile_id')
        for admin_profile_obj in admins_profile_obj:
            profile = Profile.objects.get(profile_id=admin_profile_obj.profile_id).user_id
            administrator = User.objects.get(id=profile).get_full_name()
            administrators.append(administrator)

        members_profile_obj = GroupMember.objects.filter(group_account=grp_acc).only('profile_id')
        for member_profile_obj in members_profile_obj:
            profile = Profile.objects.get(profile_id=member_profile_obj.profile_id).user_id
            member = User.objects.get(id=profile).get_full_name()
            members.append(member)
    except Account.DoesNotExist:
        pass
    context = {
        'group': name,
        'number': count,
        'members': members,
        'administrators': administrators,
    }
    return render_with_global_data(request, 'pochi/group_settings.html', context)


@login_required
def add_remove_member(request, name=None, action=None):
    if action == 'add':
        if request.POST:
            members = request.POST['members']
            count = len(eval(members))
            invalid = 0
            for member in eval(members):
                profile = Profile.objects.filter(profile_id=member)
                if profile.exists():
                    try:
                        this_group = Group.objects.get(name=name)
                        grp_acc = this_group.group_account
                        GroupMember.objects.create(group_account=grp_acc, profile_id=member)
                    except Account.DoesNotExist:
                        pass
                else:
                    count -= 1
                    invalid += 1
            if count > 0 and invalid == 0:
                messages.info(
                    request,
                    'You have successfully added ' + str(count) + ' valid members to your group'
                )
            elif count > 0 and invalid > 0:
                messages.info(
                    request,
                    'You have successfully added ' + str(count) + ' valid members to your group'
                )
                messages.error(
                    request,
                    'Could not add ' + str(invalid) + ' invalid members in your list'
                )
            elif count == 0 and invalid > 0:
                messages.error(
                    request,
                    'Could not add ' + str(invalid) + ' invalid members in your list'
                )
        if action == 'remove':
            if request.POST:
                names = request.POST['rejected']
                count = len(eval(names))
                for name in eval(names):
                    first_name = name.split[0]
                    rejected_profile_id = Profile.objects.get(user__first_name=first_name).profile_id
                    try:
                        this_group = Group.objects.get(name=name)
                        grp_acc = this_group.group_account
                        GroupMember.objects.filter(group_account=grp_acc, profile_id=rejected_profile_id).delete()
                    except Account.DoesNotExist:
                        pass
                messages.info(
                    request,
                    'You have successfully removed ' + str(count) + ' members from your group'
                )
    return redirect(request.META['HTTP_REFERER'])


@login_required
def group_statement(request, name=None):
    group_transactions = None
    try:
        this_group = Group.objects.get(name=name)
        grp_acc = this_group.group_account
    except Account.DoesNotExist:
        grp_acc = None
    if grp_acc:
        if request.GET:
            if request.GET.get('range'):
                date_range = request.GET.get('range')
                start, end = date_range.split(' - ')
                start = datetime.datetime.strptime(start, '%m/%d/%Y').strftime('%Y-%m-%d')
                end = datetime.datetime.strptime(end, '%m/%d/%Y').strftime('%Y-%m-%d')
                group_transactions = Transaction.objects.filter(account=grp_acc, fulltimestamp__range=[start, end])
            elif request.GET.get('channel'):
                selected_account = request.GET.get('channel')
                group_transactions = Transaction.objects.filter(account=grp_acc, channel=selected_account)
            elif request.GET.get('service'):
                selected_account = request.GET.get('service')
                group_transactions = Transaction.objects.filter(account=grp_acc, service=selected_account)
        else:
            try:
                group_transactions = Transaction.objects.filter(account=grp_acc)
            except Transaction.DoesNotExist:
                group_transactions = None
        context = {
            'group': name,
            'account': grp_acc,
            'transactions': group_transactions
        }
        return render_with_global_data(request, 'pochi/group_statement.html', context)
    else:
        return render_with_global_data(request, 'pochi/group_statement.html', {'group': name})


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


def delete_group(request, name=None):
    profile = request.user.profile
    try:
        group = Group.objects.filter(name=name)
        group_acc = group.group_account
    except Group.DoesNotExist:
        group_acc = None
        group = None
    if group_acc:
        group_member_obj = GroupMember.objects.get(profile_id=profile.profile_id)
        is_admin = group_member_obj.admin
        if is_admin:
            if group.balance > 0:
                admin_id = group_member_obj.profile_id
                Account.objects.get(profile_id=admin_id).balance += group.balance
            GroupMember.objects.filter(group_account=group_acc).delete()
            Group.objects.get(name=name).delete()
    return redirect(request.META['HTTP_REFERER'])


def exit_group(request, name=None):
    profile = request.user.profile
    try:
        group = Group.objects.filter(name=name)
        group_acc = group.group_account
    except Group.DoesNotExist:
        group_acc = None
        group = None

    if group_acc:
        try:
            members_queryset = GroupMember.objects.filter(group_account=group_acc)
        except GroupMember.DoesNotExist:
            members_queryset = None

        members_count = members_queryset.count()

        if members_count <= 2:
            if group.balance > 0:
                remaining_member_queryset = GroupMember.objects.exclude(profile_id=profile.profile_id)
                remaining_member_id = remaining_member_queryset.profile_id
                Account.objects.get(profile_id=remaining_member_id).balance += group.balance
            GroupMember.objects.get(profile_id=profile.profile_id).delete()
            Group.objects.get(name=name).delete()
        else:
            is_admin = GroupMember.objects.get(profile_id=profile.profile_id).admin
            if is_admin:
                remaining_member_queryset = GroupMember.objects.exclude(profile_id=profile.profile_id)
                new_admin_queryset = remaining_member_queryset.first()
                new_admin_queryset.admin = 1
            GroupMember.objects.get(profile_id=profile.profile_id).delete()
    return redirect(request.META['HTTP_REFERER'])


def delete_account(request):
    pass


def create_form(request):
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="indemnity.pdf"'

    # Create the PDF object, using the response object as its "file."
    p = canvas.Canvas(response)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(100, 100, "Hello world.")

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()
    return response
