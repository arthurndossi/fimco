import datetime
import uuid

from core.utils import render_with_global_data
from django.contrib import messages
from django.contrib.auth import user_logged_out
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction, IntegrityError
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.dispatch import receiver
from django.http import JsonResponse
from django.shortcuts import redirect
from easy_pdf.views import PDFTemplateView
from fimcosite.forms import EditProfileForm, BankAccountForm
from fimcosite.models import Account, Profile

from core import demo_settings
from fimcosite.views import index

from .models import Transaction, Group, GroupMember, ExternalAccount, Ledger, Charge, CashOut, BalanceSnapshot, Rate, \
    PaidUser


class CumulativeBonusDto:
    def __init__(self, profile_id, bonus, time, cumulative):
        self.profile = profile_id
        self.bonus = bonus
        self.time = time
        self.cumulative = cumulative


class IndemnityPDF(PDFTemplateView):
    template_name = 'pochi/indemnity_form_template.html'

    base_url = 'file://' + demo_settings.STATIC_ROOT
    download_filename = 'indemnity_form.pdf'

    def get_context_data(self, **kwargs):
        return super(IndemnityPDF, self).get_context_data(
            pagesize='A4',
            title='Indemnity Form',
            **kwargs
        )

    def post(self, request, *args, **kwargs):
        if request.POST:
            form = BankAccountForm(request.POST or None)
            if form.is_valid():
                name = form.cleaned_data['account_name']
                account_no = form.cleaned_data['account_no']
                bank = form.cleaned_data['bank_name']
                branch = form.cleaned_data['branch_name']
                address = form.cleaned_data['bank_address']
                if form.cleaned_data['swift_code']:
                    swift = form.cleaned_data['swift_code']
                else:
                    swift = None
                values = {
                    'name': name,
                    'account': account_no,
                    'bank': bank,
                    'branch': branch,
                    'address': address,
                    'swift': swift
                }
                context = self.get_context_data(**kwargs)
                context.update(values)

                return self.render_to_response(context)

        return redirect(request.META['HTTP_REFERER'])


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

    try:
        transactions = Transaction.objects.filter(profile_id=profile.profile_id, status='PENDING')\
            .values('full_timestamp', 'service', 'channel', 'mode', 'amount', 'charge')
    except Transaction.DoesNotExist:
        transactions = None

    context = {
        'pendings': transactions,
        'account': balance_data,
        'groups': group_members_obj
    }
    return render_with_global_data(request, 'pochi/home.html', context)


def get_rates():
    try:
        all_rates = Rate.objects.all()
    except Rate.DoesNotExist:
        all_rates = None
    if all_rates:
        last_30_days = datetime.datetime.today() - datetime.timedelta(days=30)
        rates_30 = all_rates.filter(full_timestamp__gte=last_30_days).only('rate')
        rates_arr = []
        for rate in rates_30:
            rates_arr.append(rate.rate)
        decimal_array = [float(decimal_value) for decimal_value in rates_arr]
        rates_list = (", ".join(repr(e) for e in decimal_array))
        try:
            today_rate = all_rates.get(full_timestamp__date=datetime.date.today()).rate
        except Rate.DoesNotExist:
            today_rate = None
        if today_rate:
            context = {
                'month': rates_list,
                'today': today_rate
            }
        else:
            context = {
                'month': rates_list,
                'today': 'Nil'
            }
    else:
        context = {
            'month': [],
            'today': 'Nil'
        }
    return context


def daily_rates(request):
    profile_id = request.user.profile.profile_id
    try:
        all_daily = BalanceSnapshot.objects.filter(profile_id=profile_id) \
            .values('full_timestamp', 'bonus_closing_balance')
    except BalanceSnapshot.DoesNotExist:
        all_daily = None
    if all_daily:
        last_30_days = datetime.datetime.today() - datetime.timedelta(days=30)
        daily_30 = all_daily.filter(full_timestamp__gte=last_30_days)
        bonus_arr = []
        for bonus in daily_30:
            bonus_arr.append(bonus['bonus_closing_balance'])
        numeric_array = [float(numeric_value) for numeric_value in bonus_arr]
        bonus_list = (", ".join(repr(e) for e in numeric_array))
        try:
            today_bonus = all_daily.get(full_timestamp__date=datetime.date.today())['bonus_closing_balance']
        except BalanceSnapshot.DoesNotExist:
            today_bonus = None
        if today_bonus:
            context = {
                'month': bonus_list,
                'today': today_bonus
            }
        else:
            context = {
                'month': bonus_list,
                'today': 'Nil'
            }
    else:
        context = {
            'month': [],
            'today': 'Nil'
        }
    return context


def get_monthly(request):
    profile_id = request.user.profile.profile_id
    try:
        all_monthly = BalanceSnapshot.objects.filter(profile_id=profile_id) \
            .annotate(month=TruncMonth('full_timestamp')) \
            .values('month') \
            .annotate(bonus=Sum('bonus_closing_balance')) \
            .values('month', 'bonus')
    except BalanceSnapshot.DoesNotExist:
        all_monthly = None
    if all_monthly:
        last_12 = all_monthly.reverse()[:12]
        bonus_arr = []
        for bonus in last_12:
            bonus_arr.append(bonus['bonus'])
        numeric_array = [float(numeric_value) for numeric_value in bonus_arr]
        bonus_list = (", ".join(repr(e) for e in numeric_array))
        monthly_bonus = all_monthly.reverse()[:1]
        context = {
            'year': bonus_list,
            'month': monthly_bonus
        }
    else:
        context = {
            'year': [],
            'month': 'Nil'
        }
    return context


def get_total(request):
    profile_id = request.user.profile.profile_id
    try:
        bs = BalanceSnapshot.objects.filter(profile_id=profile_id)
    except BalanceSnapshot.DoesNotExist:
        bs = None
    if bs:
        bs_arr = []
        cumulative = 0
        for individual in bs:
            cumulative += individual.bonus_closing_balance
            dto = CumulativeBonusDto(
                individual.profile_id,
                individual.bonus_closing_balance,
                individual.full_timestamp,
                cumulative
            )
            bs_arr.append(dto.cumulative)
        total_bonuses = bs.aggregate(Sum('bonus_closing_balance'))
        cumulative_30 = bs_arr[-30:]
        numeric_array = [float(numeric_value) for numeric_value in cumulative_30]
        cumulative_list = (", ".join(repr(e) for e in numeric_array))
        context = {
            'total': total_bonuses,
            'month': cumulative_list
        }
    else:
        context = {
            'month': [],
            'total': 'Nil'
        }
    return context


@login_required
def admin(request, name=None):
    if name:
        try:
            group = Group.objects.get(name=name)
            profile_id = group.name
        except Group.DoesNotExist:
            profile_id = None
    else:
        profile_id = request.user.profile.profile_id

    rates = get_rates()
    daily_earnings = daily_rates(request)
    monthly_earnings = get_monthly(request)
    total = get_total(request)

    context = {
        'rates': rates,
        'daily': daily_earnings,
        'monthly': monthly_earnings,
        'total': total
    }

    if profile_id:
        snap_obj = BalanceSnapshot.objects.filter(profile_id=profile_id)\
            .values('closing_balance', 'bonus_closing_balance', 'full_timestamp')
        bal_list = []
        bonus_list = []
        label_list = []
        for row in snap_obj:
            temp_label = row['full_timestamp']
            temp_bal = row['closing_balance']
            temp_bonus = row['bonus_closing_balance']
            label_list.append(temp_label.strftime('%d/%m/%Y'))
            bal_list.append(float(temp_bal))
            bonus_list.append(float(temp_bonus))

        if name:
            context.update({'labels': label_list, 'balance': bal_list, 'bonus': bonus_list, 'group': name})
        else:
            context.update({'labels': label_list, 'balance': bal_list, 'bonus': bonus_list})

        return render_with_global_data(request, 'pochi/admin.html', context)
    else:
        messages.info(request, 'This group has no transactions yet!')
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


def confirm_transfer(request):
    if request.session['confirm'] == u'mobile':
        institution = request.session['institution']
        identifier = request.session['identifier']
        pochi_id = request.session['pochi_id']
        phone = request.session['phone']
        bal = request.session['bal']
        amount = request.session['amount']
        ov = request.session['overdraft']

        del request.session['confirm']
        del request.session['institution']
        del request.session['identifier']
        del request.session['pochi_id']
        del request.session['phone']
        del request.session['bal']
        del request.session['amount']
        del request.session['overdraft']

        fund_transfer(request, 'WITHDRAW', 'NA', institution, identifier, pochi_id, phone, bal, amount, phone, ov)

        messages.success(
            request,
            'You have successfully withdrawn TZS' + str(amount) + ' to your ' + institution + ' account ' + phone
        )
        return render_with_global_data(request, 'pochi/mobile_withdraw.html', {})

    elif request.session['confirm'] == u'bank':
        institution = request.session['institution']
        ext_account_no = request.session['ext_account']
        identifier = request.session['identifier']
        pochi_id = request.session['pochi_id']
        phone = request.session['phone']
        bal = request.session['bal']
        amount = request.session['amount']
        ov = request.session['overdraft']

        del request.session['confirm']
        del request.session['institution']
        del request.session['ext_account']
        del request.session['identifier']
        del request.session['pochi_id']
        del request.session['phone']
        del request.session['bal']
        del request.session['amount']
        del request.session['overdraft']

        ext_account = ExternalAccount.objects.get(profile_id=identifier)

        fund_transfer(request, 'WITHDRAW', 'NA', institution, identifier, pochi_id, ext_account_no, bal, amount, phone,
                      ov)

        messages.success(
            request,
            'You have successfully withdrawn TZS' + str(amount) + ' to your ' + institution + ' account ' + phone
        )
        return render_with_global_data(request, 'pochi/withdrawal.html', {'bank_account': ext_account})

    elif request.session['confirm'] == u'P2P':
        src_account = request.session['account_no']
        name = request.session['name']
        ext_wallet = request.session['ext_wallet']
        dest_account = request.session['dest_account']
        dest_profile_id = request.session['dest_profile_id']
        amount = request.session['amount']
        ov = request.session['overdraft']
        bal = request.session['open_bal']

        del request.session['confirm']
        del request.session['dest_account']
        del request.session['dest_profile_id']
        del request.session['amount']
        del request.session['overdraft']
        del request.session['open_bal']
        del request.session['account_no']
        del request.session['name']
        del request.session['ext_wallet']

        amount = float(amount)
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
            messages.success(request, 'TZS' + str(amount) + ' has been transferred from your account to ' + name + '.')
        else:
            messages.error(request, 'An invalid account was selected.')
        return render_with_global_data(request, 'pochi/pochi2pochi.html', {})

    elif request.session['confirm'] == u'G2P':
        src_account_no = request.session['account_no']
        name = request.session['name']
        group_name = request.session['group_name']
        ext_wallet = request.session['ext_wallet']
        dest_account_no = request.session['dest_account']
        dest_profile_id = request.session['dest_profile_id']
        amount = request.session['amount']
        ov = request.session['overdraft']
        bal = request.session['open_bal']

        amount = float(amount)
        bal = float(bal)
        phone = 'NA'
        src_profile_id = name

        del request.session['confirm']
        del request.session['dest_account']
        del request.session['dest_profile_id']
        del request.session['amount']
        del request.session['overdraft']
        del request.session['open_bal']
        del request.session['account_no']
        del request.session['name']
        del request.session['ext_wallet']
        del request.session['group_name']

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
            messages.success(request, 'TZS' + str(amount) + ' has been transferred from ' + group_name + ' account to '
                             + name + '.')
        else:
            messages.error(request, 'An invalid account was selected.')

        return render_with_global_data(request, 'pochi/group_activity.html', {})


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
    total = amount + charges
    if service == 'P2P':
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
                c_bal=close_bal
            )
            Ledger.objects.create(
                trans_type='CREDIT',
                service=service,
                amount=amount,
                o_bal=close_bal,
                c_bal=close_bal
            )
            BalanceSnapshot.objects.create(
                profile_id=profile_id,
                account=src,
                closing_balance=close_bal - total
            )
    elif service == 'WITHDRAW':
        if total <= bal or overdraft:
            Transaction.objects.create(
                profile_id=profile_id,
                account=src,
                msisdn=msisdn,
                external_wallet_id=ext_wallet,
                service=service,
                channel=channel,
                dest_account=dest,
                amount=amount,
                charge=charges
            )
            Ledger.objects.create(
                profile_id=profile_id,
                trans_type='DEBIT',
                service=service,
                amount=amount,
                o_bal=close_bal,
                c_bal=close_bal - total
            )
            CashOut.objects.create(
                ext_entity=channel,
                ext_acc_no=ext_wallet,
                amount=total
            )
            BalanceSnapshot.objects.create(
                profile_id=profile_id,
                account=src,
                closing_balance=close_bal - total
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
        BalanceSnapshot.objects.create(
            profile_id=profile_id,
            account=src,
            closing_balance=close_bal + amount
        )


@login_required
def pochi2pochi(request, name=None):
    this_group = None
    acc = None
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
        try:
            acc = Account.objects.get(profile_id=profile.profile_id)
            bal = acc.balance
            ov = acc.allow_overdraft
        except Account.DoesNotExist:
            acc = None
            bal = ov = 0

    if request.method == "POST":
        user_name = dest_account = dest_profile_id = None
        if request.POST['dest_mobile']:
            phone = request.POST['dest_mobile']
            if phone == request.user.username:
                messages.error(request, 'Sorry!, you cannot transfer money to your own account!')
                return redirect(request.META['HTTP_REFERER'])
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
            if acc.account == dest_account:
                messages.error(request, 'Sorry!, you cannot transfer money to your own account!')
                return redirect(request.META['HTTP_REFERER'])

            try:
                dest_profile_id = Account.objects.get(account=dest_account).profile_id
            except Account.DoesNotExist:
                dest_profile_id = None

            if dest_profile_id:
                try:
                    user_obj = User.objects.get(profile__profile_id=dest_profile_id)
                    user_name = user_obj.get_full_name()
                except Profile.DoesNotExist:
                    user_name = None

        amount = request.POST['amount']
        request.session['confirm'] = request.POST['type']
        amount = float(amount)

        if dest_account:
            if amount <= bal and user_name is not None:
                messages.info(
                    request,
                    'You are about to transfer TZS' + str(amount) + ' to ' + user_name +
                    '.\r Proceed with the transfer?'
                )

                request.session['dest_account'] = dest_account
                request.session['dest_profile_id'] = dest_profile_id
                request.session['account_no'] = acc.account
                request.session['name'] = user_name
                request.session['ext_wallet'] = acc.external_wallet_id
                request.session['amount'] = amount
                request.session['overdraft'] = ov
                request.session['open_bal'] = bal
                if name:
                    request.session['group_name'] = name

            elif amount > bal and user_name is not None:
                messages.error(
                    request,
                    'You do not have enough balance to make to transfer TZS' + str(amount) + ' to ' + user_name + '.'
                )
            elif user_name is None:
                messages.error(request, 'This user is not registered with a POCHI account!')
        else:
            messages.error(request, 'This user is not registered with a POCHI account!')
    if name:
        context = {
            'group': name,
            'account': this_group,
        }
        return render_with_global_data(request, 'pochi/group_activity.html', context)
    else:
        context = {
            'account': acc
        }
    return render_with_global_data(request, 'pochi/pochi2pochi.html', context)


@login_required
def mobile(request):
    return render_with_global_data(request, 'pochi/mobile_withdraw.html', {})


@login_required
def withdraw(request):
    profile = request.user.profile
    identifier = profile.profile_id
    phone = request.user.username
    msisdn_3 = phone[:3]

    swift = None
    address = None
    display_buttons = False

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
        external_account = ExternalAccount.objects.get(profile_id=identifier)
    except ExternalAccount.DoesNotExist:
        external_account = None

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
            if request.POST['swift']:
                swift = request.POST['swift']
            if request.POST['swift']:
                address = request.POST['address']

        elif request.POST['type'] == u"bank":
            amount = float(request.POST['amount'])
            request.session['confirm'] = request.POST['type']

            try:
                ext_account = ExternalAccount.objects.get(profile_id=identifier)
                institution = ext_account.institution_name
                ext_account_no = ext_account.account_number
            except ExternalAccount.DoesNotExist:
                messages.error(request, 'You have not registered your bank account\r\n, '
                                        'To add an account go to Fund transfer -> Bank Account '
                                        'and follow instructions on how to open an account')
                return redirect(request.META['HTTP_REFERER'])

            try:

                _account = Account.objects.get(profile_id=identifier)
                pochi_id = _account.account
                bal = _account.balance
                ov = _account.allow_overdraft

                if amount <= bal:
                    _account.balance -= amount
                    _account.save()

                    request.session['institution'] = institution
                    request.session['ext_account'] = ext_account_no
                    request.session['identifier'] = identifier
                    request.session['pochi_id'] = pochi_id
                    request.session['phone'] = phone
                    request.session['bal'] = bal
                    request.session['amount'] = amount
                    request.session['overdraft'] = ov

                    messages.info(
                        request,
                        'You are about to withdraw TZS ' + str(amount) + ' to your ' + ext_account_no + ' '
                        + institution + ' account!'
                    )
                else:
                    messages.error(request, 'You have insufficient funds to withdraw money from your account!')

            except Account.DoesNotExist:
                pass
        elif request.POST['type'] == u"mobile":
            amount = float(request.POST['amount'])
            request.session['confirm'] = request.POST['type']

            try:
                _account = Account.objects.get(profile_id=identifier)
                pochi_id = _account.account
                bal = _account.balance
                ov = _account.allow_overdraft

                if amount <= bal:
                    _account.balance -= amount
                    _account.save()

                    request.session['institution'] = institution
                    request.session['identifier'] = identifier
                    request.session['pochi_id'] = pochi_id
                    request.session['phone'] = phone
                    request.session['bal'] = bal
                    request.session['amount'] = amount
                    request.session['overdraft'] = ov

                    messages.info(
                        request,
                        'You are about to withdraw TZS ' + str(amount) + ' to your ' + institution + ' account ' + phone
                    )
                else:
                    messages.error(request, 'You have insufficient funds to withdraw money from your account!')

            except Account.DoesNotExist:
                pass

            return render_with_global_data(request, 'pochi/mobile_withdraw.html', {})

    context = {
        'bank_account': external_account,
        'address': address,
        'swift': swift,
        'buttons': display_buttons,
        'bForm': BankAccountForm
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
                    dst_account = _account.account

                    fund_transfer(request, 'DEPOSIT', 'NA', 'NA', src_profile_id, 'NA', dst_account, bal, amount, phone)

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
                name = _group.name

                fund_transfer(request, 'DEPOSIT', 'NA', 'NA', name, 'NA', this_account, bal, amount, 'NA')

                _group.balance += amount
                _group.save()

                message = 'You have successfully deposited ' + str(amount) + ' to your group account'

            except Group.DoesNotExist:
                message = 'Sorry!, This account number does not belong to any group in the system!'
                pass
    return JsonResponse({'message': message})


def del_bank_acc(request):
    profile_id = request.user.profile.profile_id
    try:
        ExternalAccount.objects.get(profile_id=profile_id).delete()
    except ExternalAccount.DoesNotExist:
        messages.warning(request, 'You have not registered a bank account!')
    return redirect(withdraw)


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
        try:
            with transaction.atomic():
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
        except IntegrityError:
            messages.error(request, 'Sorry!, this group name is already in use, try a different name')
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


@receiver(user_logged_out)
def lock(request, **kwargs):
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
    statements = None
    try:
        this_group = Group.objects.get(name=name)
        grp_acc = this_group.group_account
        try:
            statements = Transaction.objects.filter(account=grp_acc).exists()
            group_transactions = Transaction.objects.filter(account=grp_acc, status='PENDING')\
                .values('full_timestamp', 'service', 'channel', 'mode', 'amount', 'charge')
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
        'statement': statements,
        'pendings': group_transactions
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


@login_required
def view_data(request, page=None, name=None):
    if name:
        try:
            group = Group.objects.get(name=name)
            profile_id = group.name
        except Group.DoesNotExist:
            profile_id = None
    else:
        profile_id = request.user.profile.profile_id
    if page == 'rates':
        try:
            all_rates = Rate.objects.all()
        except Rate.DoesNotExist:
            all_rates = None
        if all_rates:
            last_30_days = datetime.datetime.today() - datetime.timedelta(days=30)
            rates_30 = all_rates.filter(full_timestamp__gte=last_30_days).only('rate')
            rates_arr = []
            for rate in rates_30:
                rates_arr.append(rate.rate)
            decimal_array = [float(decimal_value) for decimal_value in rates_arr]
            rates_list = (", ".join(repr(e) for e in decimal_array))
            try:
                today_rate = all_rates.get(full_timestamp__date=datetime.date.today()).rate
            except Rate.DoesNotExist:
                today_rate = None
            if today_rate:
                context = {
                    'page': 'rates',
                    'rates': all_rates,
                    'month': rates_list,
                    'today': today_rate
                }
            else:
                context = {
                    'page': 'rates',
                    'rates': all_rates,
                    'month': rates_list,
                    'today': 'No rate today'
                }
            return render_with_global_data(request, 'pochi/earnings.html', context)
        else:
            messages.info(request, 'There are no pochi rates yet! Coming soon')
            return render_with_global_data(request, 'pochi/earnings.html', {'page': 'rates'})
    elif page == 'daily':
        try:
            all_daily = BalanceSnapshot.objects.filter(profile_id=profile_id)\
                .values('full_timestamp', 'bonus_closing_balance')
        except BalanceSnapshot.DoesNotExist:
            all_daily = None
        if all_daily:
            last_30_days = datetime.datetime.today() - datetime.timedelta(days=30)
            daily_30 = all_daily.filter(full_timestamp__gte=last_30_days)
            bonus_arr = []
            for bonus in daily_30:
                bonus_arr.append(bonus['bonus_closing_balance'])
            numeric_array = [float(numeric_value) for numeric_value in bonus_arr]
            bonus_list = (", ".join(repr(e) for e in numeric_array))
            try:
                today_bonus = all_daily.get(full_timestamp__date=datetime.date.today())['bonus_closing_balance']
            except BalanceSnapshot.DoesNotExist:
                today_bonus = None
            if today_bonus:
                context = {
                    'page': 'daily',
                    'bonuses': all_daily,
                    'month': bonus_list,
                    'today': today_bonus
                }
            else:
                context = {
                    'page': 'daily',
                    'bonuses': all_daily,
                    'month': bonus_list,
                    'today': 'Nil'
                }
            return render_with_global_data(request, 'pochi/earnings.html', context)
        else:
            messages.info(request, 'There are no daily rates yet! Coming soon')
            return render_with_global_data(request, 'pochi/earnings.html', {'page': 'daily'})
    elif page == 'monthly':
        try:
            all_monthly = BalanceSnapshot.objects.filter(profile_id=profile_id)\
                .annotate(month=TruncMonth('full_timestamp'))\
                .values('month')\
                .annotate(bonus=Sum('bonus_closing_balance'))\
                .values('month', 'bonus')
        except BalanceSnapshot.DoesNotExist:
            all_monthly = None
        if all_monthly:
            last_12 = all_monthly.reverse()[:12]
            bonus_arr = []
            for bonus in last_12:
                bonus_arr.append(bonus['bonus'])
            numeric_array = [float(numeric_value) for numeric_value in bonus_arr]
            bonus_list = (", ".join(repr(e) for e in numeric_array))
            monthly_bonus = all_monthly.reverse()[:1]
            context = {
                'page': 'monthly',
                'bonuses': all_monthly,
                'year': bonus_list,
                'month': monthly_bonus
            }
            return render_with_global_data(request, 'pochi/earnings.html', context)
        else:
            messages.info(request, 'There are no monthly rates yet! Coming soon')
            return render_with_global_data(request, 'pochi/earnings.html', {'page': 'monthly'})
    elif page == 'total':
        try:
            bs = BalanceSnapshot.objects.filter(profile_id=profile_id)
        except BalanceSnapshot.DoesNotExist:
            bs = None
        if bs:
            bs_arr = []
            cumulative = 0
            for individual in bs:
                cumulative += individual.bonus_closing_balance
                dto = CumulativeBonusDto(
                    individual.profile_id,
                    individual.bonus_closing_balance,
                    individual.full_timestamp,
                    cumulative
                )
                bs_arr.append(dto)
            total_bonuses = bs.aggregate(Sum('bonus_closing_balance'))
            cumulative_30 = bs_arr[-30:]
            context = {
                'page': 'total',
                'total': total_bonuses,
                'history': bs_arr,
                'month': cumulative_30
            }
            return render_with_global_data(request, 'pochi/earnings.html', context)
        else:
            messages.info(request, 'No earnings yet! Coming soon')
            return render_with_global_data(request, 'pochi/earnings.html', {'page': 'total'})
    else:
        return redirect(admin)


@login_required
def delete_account(request):
    profile_id = request.user.profile.profile_id
    balance = Account.objects.get(profile_id=profile_id).balance
    if balance != 0:
        messages.info(request, 'You have to transfer all your funds from POCHI to be able to delete your account!',
                      extra_tags='main')
    elif balance == 0:
        try:
            subscription = PaidUser.objects.get(profile_id=profile_id)
        except PaidUser.DoesNotExist:
            subscription = None
        if subscription:
            subscription.delete()
        try:
            membership = GroupMember.objects.filter(profile_id=profile_id)
        except GroupMember.DoesNotExist:
            membership = None
        if membership:
            membership.delete()
        request.user.is_active = False
        request.user.save()
        return redirect(index)
    return redirect(request.META['HTTP_REFERER'])
