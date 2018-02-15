# coding=utf-8
import re
import uuid
from calendar import monthrange
from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.auth import user_logged_out
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction, IntegrityError
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.dispatch import receiver
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from djmoney.money import Money
from easy_pdf.views import PDFTemplateView
from notifications.signals import notify
from notifications.views import AllNotificationsList

from core import demo_settings
from core.utils import render_with_global_data
from fimcosite.forms import EditProfileForm, BankAccountForm
from fimcosite.models import Account, Profile, KYC
from fimcosite.views import index
from .models import Transaction, Group, GroupMember, ExternalAccount, Ledger, Charge, CashOut, BalanceSnapshot, Rate, \
    PaidUser


class CumulativeBonusDto:
    def __init__(self, bonus, time, cumulative):
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
                grp_name = Group.objects.get(account=group.group_account).name
                group_members_obj.append(grp_name)
            except Group.DoesNotExist:
                pass

    except GroupMember.DoesNotExist:
        pass

    try:
        transactions = Transaction.objects.filter(profile_id=profile.profile_id, status='PENDING')
    except Transaction.DoesNotExist:
        transactions = None

    context = {
        'transactions': transactions,
        'account': balance_data,
        'groups': group_members_obj
    }
    return render_with_global_data(request, 'pochi/home.html', context)


def get_rates(start_date):
    try:
        this_year_rates = Rate.objects.filter(full_timestamp__range=[start_date, datetime.now()])\
            .order_by('full_timestamp').only('rate')
    except Rate.DoesNotExist:
        this_year_rates = None
    if this_year_rates:
        now = datetime.now()
        rates_arr = []
        for rate in this_year_rates:
            rates_arr.append(rate.rate)
        decimal_array = [float(decimal_value) for decimal_value in rates_arr]
        rates_list = (", ".join(repr(e) for e in decimal_array))
        try:
            month_rate = Rate.objects.get(full_timestamp__month=now.month).rate
        except Rate.DoesNotExist:
            month_rate = None
        if month_rate:
            context = {
                'year': rates_list,
                'today': month_rate
            }
        else:
            context = {
                'year': rates_list,
                'today': 'Nil'
            }
    else:
        context = {
            'year': [],
            'today': 'Nil'
        }
    return context


def daily_rates(request):
    now = datetime.now()
    profile_id = request.user.profile.profile_id
    end_date = now - relativedelta(days=1)
    start_date = end_date - relativedelta(months=1)

    try:
        last_month_earnings = BalanceSnapshot.objects\
            .filter(full_timestamp__range=[start_date, end_date], profile_id=profile_id) \
            .values('full_timestamp', 'bonus_closing_balance').order_by('full_timestamp')
    except BalanceSnapshot.DoesNotExist:
        last_month_earnings = None
    if last_month_earnings:
        bonus_arr = []
        for bonus in last_month_earnings:
            bonus_arr.append(bonus['bonus_closing_balance'])
        numeric_array = [float(numeric_value) for numeric_value in bonus_arr]
        bonus_list = (", ".join(repr(e) for e in numeric_array))
        try:
            today_bonus = last_month_earnings.get(full_timestamp__date=end_date)['bonus_closing_balance']
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
                'today': 0
            }
    else:
        context = {
            'month': [],
            'today': 0
        }
    return context


def get_monthly(request, prev_date, start_date, end_date):
    profile_id = request.user.profile.profile_id
    try:
        last_12 = BalanceSnapshot.objects\
            .filter(full_timestamp__range=[start_date, end_date], profile_id=profile_id) \
            .annotate(month=TruncMonth('full_timestamp')) \
            .values('month') \
            .annotate(bonus=Sum('bonus_closing_balance')) \
            .values('month', 'bonus').order_by('month')
    except BalanceSnapshot.DoesNotExist:
        last_12 = None
    if last_12:
        bonus_arr = []
        for bonus in last_12:
            bonus_arr.append(bonus['bonus'])
        numeric_array = [float(numeric_value) for numeric_value in bonus_arr]
        bonus_list = (", ".join(repr(e) for e in numeric_array))
        query_set = last_12.filter(full_timestamp__month=prev_date.month, full_timestamp__year=prev_date.year)
        month, bonus = '', 0
        for data in query_set:
            month = data['month']
            bonus = data['bonus']
        context = {
            'year': bonus_list,
            'month': month,
            'bonus': bonus
        }
    else:
        context = {
            'year': [],
            'month': '',
            'bonus': 0
        }
    return context


def get_total(request, start_date, end_date):
    profile_id = request.user.profile.profile_id
    try:
        bs = BalanceSnapshot.objects.filter(full_timestamp__range=[start_date, end_date], profile_id=profile_id) \
            .annotate(month=TruncMonth('full_timestamp')) \
            .values('month') \
            .annotate(bonus=Sum('bonus_closing_balance')) \
            .values('month', 'bonus').order_by('month')
    except BalanceSnapshot.DoesNotExist:
        bs = None
    if bs:
        bs_arr = []
        cumulative = 0
        for individual in bs:
            cumulative += individual['bonus']
            dto = CumulativeBonusDto(
                individual['bonus'],
                individual['month'],
                cumulative
            )
            bs_arr.append(dto.cumulative)
        total_bonuses = bs.aggregate(Sum('bonus'))
        numeric_array = [float(numeric_value) for numeric_value in bs_arr]
        cumulative_list = (", ".join(repr(e) for e in numeric_array))
        context = {
            'total': total_bonuses,
            'month': cumulative_list
        }
    else:
        context = {
            'month': [],
            'total': 0
        }
    return context


@login_required
def admin(request, name=None):
    NOW = datetime.now()
    yesterday = NOW - relativedelta(days=1)
    prev_date = NOW - relativedelta(months=1)
    last_day_in_prev_date = monthrange(prev_date.year, prev_date.month)[1]
    end_date = prev_date.replace(day=last_day_in_prev_date)
    start_date = end_date - relativedelta(years=1)

    if name:
        try:
            group = Group.objects.get(name=name)
            profile_id = group.name
        except Group.DoesNotExist:
            profile_id = None
    else:
        profile_id = request.user.profile.profile_id

    rates = get_rates(start_date)
    daily_earnings = daily_rates(request)
    monthly_earnings = get_monthly(request, prev_date, start_date, end_date)
    total = get_total(request, start_date, end_date)

    context = {
        'yesterday': yesterday,
        'rates': rates,
        'daily': daily_earnings,
        'monthly': monthly_earnings,
        'total': total
    }

    if profile_id:
        snap_obj = BalanceSnapshot.objects.filter(profile_id=profile_id)\
            .values('available_closing_balance', 'bonus_closing_balance', 'full_timestamp')
        bal_list = []
        bonus_list = []
        label_list = []
        for row in snap_obj:
            temp_label = row['full_timestamp']
            temp_bal = row['available_closing_balance']
            temp_bonus = row['bonus_closing_balance']
            label_list.append(temp_label.strftime('%d/%m/%Y'))
            bal_list.append(float(temp_bal))
            bonus_list.append(float(temp_bonus))

        if name:
            context.update({'labels': label_list, 'balance': bal_list, 'bonus': bonus_list, 'group': name})
        else:
            more = {'labels': label_list, 'balance': bal_list, 'bonus': bonus_list}
            context.update(more)

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
            start = datetime.strptime(start, '%m/%d/%Y').strftime('%Y-%m-%d')
            end = datetime.strptime(end, '%m/%d/%Y').strftime('%Y-%m-%d')
            try:
                trans = Ledger.objects.filter(profile_id=profile.profile_id, full_timestamp__range=[start, end])
            except Ledger.DoesNotExist:
                trans = trans
        elif request.GET.get('channel'):
            selected_account = request.GET.get('channel')
            try:
                trans = Ledger.objects.filter(profile_id=profile.profile_id, channel=selected_account)
            except Ledger.DoesNotExist:
                trans = trans
        elif request.GET.get('service'):
            selected_account = request.GET.get('service')
            try:
                trans = Ledger.objects.filter(profile_id=profile.profile_id, service=selected_account)
            except Ledger.DoesNotExist:
                trans = trans
    else:
        try:
            trans = Ledger.objects.filter(profile_id=profile.profile_id)
        except Ledger.DoesNotExist:
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
        account_num = request.POST['account']
        account_type = request.POST['type']
        ExternalAccount.objects.create(
            profile_id=user.profile_id,
            account_name=name,
            account_number=account_num,
            institution_name=institution,
            account_type=account_type
        )
        messages.success(
            request,
            'You have successfully added '+name+' account!'
        )
    return render_with_global_data(request, 'pochi/account.html', {})


@login_required
def view_profile(request):
    user = request.user
    kyc_details = KYC.objects.get(profile_id=user.profile.profile_id)
    form = EditProfileForm(request.POST or None, initial={
        'fName': user.first_name,
        'lName': user.last_name,
        'phone': user.username,
        'email': user.email,
        'dob': user.profile.dob,
        'gender': user.profile.gender,
        'id_choice': kyc_details.kyc_type,
        'client_id': kyc_details.id_number,
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
        'client_id': kyc_details.kyc_type+' '+kyc_details.id_number,
        'bot_cds': user.profile.bot_cds,
        'dse_cds': user.profile.dse_cds
    }
    # gp_obj = GroupMember.objects.filter(profile_id=user.profile.profile_id)
    # group_names = []
    # for one_obj in gp_obj:
    #     try:
    #         name = Group.objects.get(account=one_obj.group_account).name
    #         group_names.append(name)
    #     except Group.DoesNotExist:
    #         pass

    context = {
        'pForm': form,
        'data': form_data,
        'bForm': BankAccountForm
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
            user.profile.msisdn = request.POST['phone']
            user.profile.avatar = request.FILES['avatar']
            user.profile.client_id = request.POST['id_number']
            user.profile.bot_cds = request.POST['bot_account']
            user.profile.dse_cds = request.POST['dse_account']
            user.save()
            user.profile.save()

            notify.send(user, recipient=user, verb='you reached level 10')

            return redirect(view_profile)
    else:
        return redirect(edit_profile)


def confirm_transfer(request):
    user = request.user
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

        fund_transfer(request, 'WITHDRAW', 'MOBILE', institution, identifier, pochi_id, phone, bal, amount, phone, ov)

        notify.send(user, recipient=user, verb='You have successfully withdrawn TZS' + str(amount) + ' to your '
                                               + institution + ' account ' + phone)

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

        fund_transfer(request, 'WITHDRAW', 'BANK', institution, identifier, pochi_id, ext_account_no, bal, amount,
                      phone, ov)

        notify.send(user, recipient=user, verb='You have successfully withdrawn TZS' + str(amount) + ' to your '
                                               + institution + ' account ' + phone)

        messages.success(
            request,
            'You have successfully withdrawn TZS' + str(amount) + ' to your ' + institution + ' account ' + phone
        )
        return render_with_global_data(request, 'pochi/withdrawal.html', {'bank_account': ext_account})

    elif request.session['confirm'] == u'P2P':
        src_account = request.session['account_no']
        name = request.session['name']
        dst_account = request.session['dst_account']
        amount = request.session['amount']
        ov = request.session['overdraft']
        bal = request.session['open_bal']

        del request.session['confirm']
        del request.session['dst_account']
        del request.session['amount']
        del request.session['overdraft']
        del request.session['open_bal']
        del request.session['account_no']
        del request.session['name']

        amount = float(amount)
        bal = float(bal)
        phone = request.user.username
        profile = request.user.profile
        src_profile_id = profile.profile_id

        fund_transfer(request, 'P2P', 'POCHI', 'NA', src_profile_id, src_account, dst_account, bal, amount, phone, ov)

        if src_account and dst_account:
            notify.send(user, recipient=user, verb='TZS' + str(amount) + ' has been transferred from your account to '
                                                   + name + '.')
            messages.success(request, 'TZS' + str(amount) + ' has been transferred from your account to ' + name + '.')
        else:
            messages.error(request, 'An invalid account was selected.')

        return render_with_global_data(request, 'pochi/pochi2pochi.html', {})

    elif request.session['confirm'] == u'G2P':
        src_account_no = request.session['account_no']
        name = request.session['name']
        group_name = request.session['group_name']
        dst_account_no = request.session['dst_account']
        amount = request.session['amount']
        ov = request.session['overdraft']
        bal = request.session['open_bal']

        amount = float(amount)
        bal = float(bal)
        phone = 'NA'
        src_profile_id = name

        del request.session['confirm']
        del request.session['dst_account']
        del request.session['amount']
        del request.session['overdraft']
        del request.session['open_bal']
        del request.session['account_no']
        del request.session['name']
        del request.session['group_name']

        fund_transfer(request, 'P2P', 'POCHI', 'NA', src_profile_id, src_account_no, dst_account_no, bal, amount,
                      phone, ov)

        if src_account_no and dst_account_no:
            notify.send(user, recipient=user, verb='TZS' + str(amount) + ' has been transferred from ' + group_name
                                                   + ' account to ' + name + '.')
            messages.success(request, 'TZS' + str(amount) + ' has been transferred from ' + group_name + ' account to '
                             + name + '.')
        else:
            messages.error(request, 'An invalid account was selected.')

        return render_with_global_data(request, 'pochi/group_activity.html', {})


def make_trans_id(phone):
    last_4_digits = phone[-4:]
    str_padded = last_4_digits.zfill(9)
    return "P%s" % str_padded


def generate_ref(p_id):
    last_4_digits = p_id[-4:]
    ran = str(datetime.today().microsecond)
    pad = ran[:3]
    import random
    fill = str(random.randint(11, 99))
    return "5%s%s%s" % (fill, pad, last_4_digits)


@transaction.atomic
def fund_transfer(request, service, mode, channel, profile_id, src, dst, bal, amount, msisdn, overdraft=0):
    try:
        charges = Charge.objects.get(service=mode).charge
    except Charge.DoesNotExist:
        charges = 0
    trans_id = make_trans_id(msisdn)
    total = float(amount) + float(charges)
    if service == 'P2P':
        try:
            src_acc = Account.objects.get(account=src)

            src_avail_bal = src_acc.available_balance.__float__()
            src_cur_bal = src_acc.current_balance.__float__()
            src_avail_amount = src_avail_bal - total
            src_cur_amount = src_cur_bal - total
        except Account.DoesNotExist:
            src_acc = None

        try:
            dst_acc = Account.objects.get(account=dst)
            dst_profile_id = dst_acc.profile_id

            dst_avail_bal = dst_acc.available_balance.__float__()
            dst_cur_bal = dst_acc.current_balance.__float__()
            dst_avail_amount = dst_avail_bal + total
            dst_cur_amount = dst_cur_bal + total
        except Account.DoesNotExist:
            dst_acc, dst_profile_id = None, None

        src_ref = generate_ref(profile_id)
        dst_ref = generate_ref(dst_profile_id)

        if src_acc and dst_acc:
            if bal > total or overdraft:
                Transaction.objects.create(
                    profile_id=profile_id,
                    account=src,
                    msisdn=msisdn,
                    trans_id=trans_id,
                    reference=src_ref,
                    service=service,
                    mode=mode,
                    dst_account=dst,
                    amount=Money(amount, 'TZS'),
                    status='DONE'
                )
                Ledger.objects.create(
                    profile_id=profile_id,
                    account=src,
                    trans_type='DEBIT',
                    mode=mode,
                    trans_id=trans_id,
                    reference=src_ref,
                    amount=Money(amount, 'TZS'),
                    current_o_bal=Money(src_cur_bal, 'TZS'),
                    current_c_bal=Money(src_cur_amount, 'TZS'),
                    available_o_bal=Money(src_avail_bal, 'TZS'),
                    available_c_bal=Money(src_avail_amount, 'TZS')
                )
                Ledger.objects.create(
                    profile_id=dst_profile_id,
                    account=dst,
                    trans_type='CREDIT',
                    mode=mode,
                    trans_id=trans_id,
                    reference=dst_ref,
                    amount=Money(amount, 'TZS'),
                    current_o_bal=Money(dst_cur_bal, 'TZS'),
                    current_c_bal=Money(dst_cur_amount, 'TZS'),
                    available_o_bal=Money(dst_avail_bal, 'TZS'),
                    available_c_bal=Money(dst_avail_amount, 'TZS')
                )
                BalanceSnapshot.objects.create(
                    profile_id=profile_id,
                    account=src,
                    current_closing_balance=Money(src_cur_amount, 'TZS'),
                    available_closing_balance=Money(src_avail_amount, 'TZS')
                )
                BalanceSnapshot.objects.create(
                    profile_id=dst_profile_id,
                    account=dst,
                    current_closing_balance=Money(dst_cur_amount, 'TZS'),
                    available_closing_balance=Money(dst_avail_amount, 'TZS')
                )
                src_acc.available_balance = src_avail_amount
                src_acc.current_balance = src_cur_amount
                src_acc.ts_current_bal = datetime.now()
                src_acc.save()
                dst_acc.available_balance = dst_avail_amount
                dst_acc.current_balance = dst_cur_amount
                dst_acc.ts_current_bal = datetime.now()
                dst_acc.save()
    elif service == 'WITHDRAW':
        try:
            src_acc = Account.objects.get(account=src)

            src_cur_bal = src_acc.current_balance.__float__()
            src_cur_amount = src_cur_bal - total
        except Account.DoesNotExist:
            src_acc = None

        ref = generate_ref(profile_id)

        if total <= bal or overdraft and src_acc:
            Transaction.objects.create(
                profile_id=profile_id,
                account=src,
                msisdn=msisdn,
                trans_id=trans_id,
                reference=ref,
                service=service,
                mode=mode,
                dst_account=dst,
                amount=Money(amount, 'TZS'),
                charge=Money(charges, 'TZS')
            )
            Ledger.objects.create(
                profile_id=profile_id,
                account=src,
                trans_type='DEBIT',
                mode=mode,
                trans_id=trans_id,
                reference=ref,
                amount=Money(total, 'TZS'),
                current_o_bal=Money(src_cur_bal, 'TZS'),
                current_c_bal=Money(src_cur_amount, 'TZS')
            )
            CashOut.objects.create(
                ext_entity=channel,
                ext_acc_no=dst,
                ext_trans_id=trans_id,
                amount=Money(total, 'TZS')
            )
            BalanceSnapshot.objects.create(
                profile_id=profile_id,
                account=src,
                current_closing_balance=Money(src_cur_amount, 'TZS')
            )
            src_acc.current_balance = src_cur_amount
            src_acc.ts_current_bal = datetime.now()
            src_acc.save()
    elif service == 'DEPOSIT':
        try:
            dst_acc = Account.objects.get(account=dst)

            dst_cur_bal = dst_acc.current_balance.__float__()
            dst_cur_amount = dst_cur_bal + total
        except Account.DoesNotExist:
            dst_acc = None

        ref = generate_ref(profile_id)

        Transaction.objects.create(
            profile_id=profile_id,
            account=src,
            msisdn=msisdn,
            trans_id=trans_id,
            reference=ref,
            service=service,
            mode=mode,
            dst_account=dst,
            amount=Money(amount, 'TZS'),
            charge=Money(charges, 'TZS')
        )
        Ledger.objects.create(
            profile_id=profile_id,
            account=dst,
            trans_type='CREDIT',
            mode=mode,
            trans_id=trans_id,
            reference=ref,
            amount=Money(total, 'TZS'),
            current_o_bal=Money(dst_cur_bal, 'TZS'),
            current_c_bal=Money(dst_cur_amount, 'TZS')
        )
        BalanceSnapshot.objects.create(
            profile_id=profile_id,
            account=dst,
            current_closing_balance=Money(dst_cur_amount, 'TZS')
        )
        dst_acc.current_balance = dst_cur_amount
        dst_acc.ts_current_bal = datetime.now()
        dst_acc.save()


@login_required
def pochi2pochi(request, name=None):
    this_group = None
    acc = None
    if name:
        bal = ov = 0
        try:
            this_group = Group.objects.get(name=name)
            this_group_account = this_group.account
            try:
                acc = Account.objects.get(account=this_group_account)
                ov = acc.allow_overdraft
                bal = acc.available_balance
            except Account.DoesNotExist:
                acc = None
        except Group.DoesNotExist:
            pass

    else:
        profile = request.user.profile
        try:
            acc = Account.objects.get(profile_id=profile.profile_id)
            bal = acc.available_balance.__float__()
            ov = acc.allow_overdraft
        except Account.DoesNotExist:
            acc = None
            bal = ov = 0

    if request.method == "POST":
        user_name = dst_account = dst_profile_id = None
        if request.POST['dst_mobile']:
            phone = request.POST['dst_mobile']
            if phone == request.user.username:
                messages.error(request, 'Sorry!, you cannot transfer money to your own account!')
                return redirect(request.META['HTTP_REFERER'])
            try:
                user_obj = User.objects.select_related('profile').get(username=phone)
                dst_profile_id = user_obj.profile.profile_id
                user_name = user_obj.get_full_name()
            except User.DoesNotExist:
                user_name = None

            try:
                dst_account = Account.objects.get(profile_id=dst_profile_id).account
            except Account.DoesNotExist:
                dst_account = None

        elif request.POST['dst_account']:
            dst_account = request.POST['dst_account']
            if acc.account == dst_account:
                messages.error(request, 'Sorry!, you cannot transfer money to your own account!')
                return redirect(request.META['HTTP_REFERER'])

            try:
                dst_profile_id = Account.objects.get(account=dst_account).profile_id
            except Account.DoesNotExist:
                dst_profile_id = None

            if dst_profile_id == 'NA':
                try:
                    grp = Group.objects.get(account=dst_account)
                    grp_name = grp.name
                except Group.DoesNotExist:
                    grp_name = None
            elif dst_profile_id and dst_profile_id != 'NA':
                try:
                    user_obj = User.objects.get(profile__profile_id=dst_profile_id)
                    user_name = user_obj.get_full_name()
                except User.DoesNotExist:
                    user_name = None

        amount = request.POST['amount']
        request.session['confirm'] = request.POST['type']
        amount = amount

        if dst_account:
            if amount <= bal and user_name or grp_name:
                get_name = user_name if user_name else grp_name
                messages.info(
                    request,
                    'You are about to transfer TZS' + str(amount) + ' to ' + get_name +
                    '.\r Proceed with the transfer?'
                )

                request.session['dst_account'] = dst_account
                request.session['account_no'] = acc.account
                request.session['name'] = get_name
                request.session['amount'] = amount
                request.session['overdraft'] = ov
                request.session['open_bal'] = bal
                if name:
                    request.session['group_name'] = name

            elif amount > bal and user_name or grp_name:
                get_name = user_name if user_name else grp_name
                messages.error(
                    request,
                    'You do not have enough balance to make to transfer TZS' + str(amount) + ' to ' + get_name + '.'
                )
            elif user_name is None:
                messages.error(request, 'This user is not registered with a POCHI account!')
            elif grp_name is None:
                messages.error(request, 'This group is not registered with a POCHI account!')
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
            account_num = request.POST['account']
            account_type = request.POST['type']
            ExternalAccount.objects.create(
                profile_id=identifier,
                account_name=bank_name,
                account_number=account_num,
                institution_name=institution,
                account_type=account_type
            )
            messages.success(
                request,
                'You have successfully added ' + bank_name + ' account!'
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
                bal = _account.available_balance.__float__()
                ov = _account.allow_overdraft

                if amount <= bal:
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
                bal = _account.available_balance.__float__()
                ov = _account.allow_overdraft

                if amount <= bal:
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
    user = request.user
    message = None
    if request.method == "GET":
        amount = float(request.GET['amount'])
        dst_account = request.GET['account']
        phone = request.GET['msisdn']
        channel = request.GET['channel']
        mode = request.GET['source']

        try:
            _account = Account.objects.get(account=dst_account)
            dst_profile_id = _account.profile_id
            bal = _account.available_balance
            dst_account = _account.account

            if dst_profile_id == 'NA':
                name = _account.nickname
                fund_transfer(request, 'DEPOSIT', mode, channel, name, phone, dst_account, bal, amount, phone)
            else:
                fund_transfer(request, 'DEPOSIT', mode, channel, dst_profile_id, phone, dst_account, bal, amount, phone)

            notify.send(user, recipient=user, verb='TShs. ' + str(amount) + ' deposited to your account')

            message = 'You have successfully deposited ' + str(amount) + ' to your account'

        except Account.DoesNotExist:
            message = 'Sorry!, This account does not exist!'

    return JsonResponse({'message': message})


def del_bank_acc(request):
    user = request.user
    profile_id = request.user.profile.profile_id
    try:
        notify.send(user, recipient=user, verb='Register your bank account!')
        ExternalAccount.objects.get(profile_id=profile_id).delete()
    except ExternalAccount.DoesNotExist:
        messages.warning(request, 'You have not registered a bank account!')
    return redirect(withdraw)


def confirm_delete_bank_acc(request):
    messages.warning(request, 'You are about to delete your bank account in POCHI. Proceed?')
    return redirect(request.META['HTTP_REFERER'])


@login_required
def new_group(request):
    phone = request.user.username
    return render_with_global_data(request, 'pochi/create_group.html', {'phone': phone})


@login_required
def create_group(request):
    user = request.user
    import json
    if request.method == 'POST':
        groupName = request.POST['profileGroupName'].capitalize()
        member_list = request.POST['members']
        first_admin = user.username
        members = json.loads(member_list)
        grp_acc = uuid.uuid4().hex[:10].upper()
        try:
            with transaction.atomic():
                Group.objects.create(
                    account=grp_acc,
                    name=groupName,
                )
                Account.objects.create(
                    account=grp_acc,
                    nickname=groupName,
                )

                for member in members:
                    is_admin = 0
                    if member == first_admin:
                        is_admin = 1
                    try:
                        profile_id = Profile.objects.get(user__username=member).profile_id
                    except Profile.DoesNotExist:
                        profile_id = None
                    if profile_id is None:
                        continue
                    GroupMember.objects.create(
                        group_account=grp_acc,
                        profile_id=profile_id,
                        admin=is_admin
                    )
                    notify.send(user, recipient=user, verb='You created group '+groupName+' successfully!')
                    messages.success(request, "Group "+groupName+"created successfully!")
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
    return redirect(request.META['HTTP_REFERER'])


@login_required
def edit_group(request):
    return render_with_global_data(request, 'pochi/edit_group.html', {})


@receiver(user_logged_out)
def lock(request, **kwargs):
    return render_with_global_data(request, 'pochi/lock.html', {})


@login_required
def group_settings(request, name=None):
    count = 0
    members = []
    admins = []
    try:
        this_group = Group.objects.get(name=name)
        grp_acc = this_group.account
        count = GroupMember.objects.filter(group_account=grp_acc).count()

        members_profile_obj = GroupMember.objects.filter(group_account=grp_acc).values('profile_id', 'admin')
        for member_profile_obj in members_profile_obj:
            pid = member_profile_obj['profile_id']
            adm = member_profile_obj['admin']
            member = User.objects.select_related('profile').get(profile__profile_id=pid).get_full_name()
            if adm == 1:
                admins.append(member)
            members.append({'member': member, 'id': pid, 'admin': adm})
    except Account.DoesNotExist:
        pass
    context = {
        'group': name,
        'number': count,
        'members': members,
        'admins': admins,
    }
    return render_with_global_data(request, 'pochi/group_settings.html', context)


@login_required
def add_remove_member(request, name=None, action=None):
    if action == 'add':
        if request.POST:
            members = request.POST['members']
            evaluated_members = eval(members)
            count = len(evaluated_members)
            invalid = 0
            for member in evaluated_members:
                profile = Profile.objects.select_related('user').get(user__username=member)
                if profile:
                    try:
                        this_group = Group.objects.get(name=name)
                        grp_acc = this_group.account
                        GroupMember.objects.create(group_account=grp_acc, profile_id=profile.profile_id)
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
            JsonResponse({'status': 'success', 'url': request.META['HTTP_REFERER']})
        else:
            JsonResponse({'status': 'fail', 'url': request.META['HTTP_REFERER']})
    elif action == 'remove':
        if request.POST:
            names = request.POST['rejected']
            count = len(eval(names))
            for name in eval(names):
                first_name = name.split[0]
                rejected_profile_id = Profile.objects.get(user__first_name=first_name).profile_id
                try:
                    this_group = Group.objects.get(name=name)
                    grp_acc = this_group.account
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
        grp_acc = this_group.account
    except Group.DoesNotExist:
        grp_acc = None
    if grp_acc:
        if request.GET:
            if request.GET.get('range'):
                date_range = request.GET.get('range')
                start, end = date_range.split(' - ')
                start = datetime.strptime(start, '%m/%d/%Y').strftime('%Y-%m-%d')
                end = datetime.strptime(end, '%m/%d/%Y').strftime('%Y-%m-%d')
                group_transactions = Ledger.objects.filter(account=grp_acc, full_timestamp__range=[start, end])
            elif request.GET.get('channel'):
                selected_account = request.GET.get('channel')
                group_transactions = Ledger.objects.filter(account=grp_acc, channel=selected_account)
            elif request.GET.get('service'):
                selected_account = request.GET.get('service')
                group_transactions = Ledger.objects.filter(account=grp_acc, service=selected_account)
        else:
            try:
                group_transactions = Ledger.objects.filter(account=grp_acc)
            except Ledger.DoesNotExist:
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
        grp_acc = this_group.account
        try:
            statements = Transaction.objects.filter(account=grp_acc).exists()
            group_transactions = Transaction.objects.filter(account=grp_acc, status='PENDING')
        except Transaction.DoesNotExist:
            group_transactions = None
    except Group.DoesNotExist:
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
        'pending': group_transactions
    }
    return render_with_global_data(request, 'pochi/group_profile.html', context)


def delete_group(request, name=None):
    user = request.user
    profile = request.user.profile
    try:
        group = Group.objects.get(name=name)
        group_acc = group.account
    except Group.DoesNotExist:
        group_acc = None
    if group_acc:
        group_member_obj = GroupMember.objects.get(group_account=group_acc, profile_id=profile.profile_id)
        group_account = Account.objects.get(account=group_acc)
        is_admin = group_member_obj.admin
        grp_cur_bal = group_account.current_balance.__float__()
        if is_admin:
            if grp_cur_bal > 0:
                admin_id = group_member_obj.profile_id
                m_account = Account.objects.get(profile_id=admin_id)
                m_account_bal = m_account.available_balance.__float__()
                new_account_bal = m_account_bal + grp_cur_bal
                m_account.available_balance = new_account_bal
                m_account.save()
            GroupMember.objects.filter(group_account=group_acc).delete()
            Group.objects.get(name=name).delete()
            group_account.delete()
            notify.send(user, recipient=user, verb='You deleted group ' + name + ' successfully!')
    return redirect(home)


def exit_group(request, name=None):
    user = request.user
    profile = request.user.profile
    try:
        group = Group.objects.get(name=name)
        group_acc = group.account
    except Group.DoesNotExist:
        group_acc = None

    if group_acc:
        try:
            members_queryset = GroupMember.objects.filter(group_account=group_acc)
        except GroupMember.DoesNotExist:
            members_queryset = None

        try:
            grp_account = Account.objects.get(account=group_acc)
            grp_cur_bal = grp_account.current_balance.__float__()
        except Account.DoesNotExist:
            grp_account = None
            grp_cur_bal = 0

        members_count = members_queryset.count()

        if grp_account and members_count <= 2:
            if grp_cur_bal > 0:
                remaining_member_queryset = GroupMember.objects.exclude(profile_id=profile.profile_id)
                remaining_member_id = remaining_member_queryset.profile_id
                m_account = Account.objects.get(profile_id=remaining_member_id)
                m_account_bal = m_account.available_balance.__float__()
                new_account_bal = m_account_bal + grp_cur_bal
                m_account.available_balance = new_account_bal
                m_account.save()
            GroupMember.objects.get(group_account=group_acc, profile_id=profile.profile_id).delete()
            Group.objects.get(name=name).delete()
            grp_account.delete()
        else:
            GroupMember.objects.get(group_account=group_acc, profile_id=profile.profile_id).delete()

        notify.send(user, recipient=user, verb='You exited group ' + name + ' successfully!')

    return redirect(home)


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

    NOW = datetime.now()
    prev_date = NOW - relativedelta(months=1)
    last_day_in_prev_date = monthrange(prev_date.year, prev_date.month)[1]
    end_date = prev_date.replace(day=last_day_in_prev_date)
    start_date = end_date - relativedelta(years=1)

    if page == 'rates':
        end_date = NOW
        if request.POST:
            rates_range = request.POST['rates_range']
            start, end = rates_range.split(' - ')
            start_date = datetime.strptime(start, '%m/%d/%Y').strftime('%Y-%m-%d')
            end_date = datetime.strptime(end, '%m/%d/%Y').strftime('%Y-%m-%d')

        try:
            all_rates = Rate.objects.filter(full_timestamp__range=[start_date, end_date])
        except Rate.DoesNotExist:
            all_rates = None

        if all_rates:
            this_year_rates = all_rates.order_by('full_timestamp').only('rate')
            rates_arr = []
            for rate in this_year_rates:
                rates_arr.append(rate.rate)
            decimal_array = [float(decimal_value) for decimal_value in rates_arr]
            rates_list = (", ".join(repr(e) for e in decimal_array))
            try:
                today_rate = all_rates.get(full_timestamp__month=NOW.month, full_timestamp__year=NOW.year).rate
            except Rate.DoesNotExist:
                today_rate = None

            if today_rate:
                context = {
                    'page': 'rates',
                    'group': name,
                    'rates': all_rates,
                    'year': rates_list,
                    'start_date': start_date,
                    'end_date': end_date
                }
            else:
                context = {
                    'page': 'rates',
                    'group': name,
                    'rates': all_rates,
                    'year': rates_list,
                    'today': 'No rate today',
                    'start_date': start_date,
                    'end_date': end_date
                }
            return render_with_global_data(request, 'pochi/earnings.html', context)
        else:
            messages.info(request, 'There are no pochi rates yet! Coming soon')
            return render_with_global_data(request, 'pochi/earnings.html', {'page': 'rates', 'group': name})

    elif page == 'daily':
        end_date = NOW - relativedelta(days=1)
        start_date = end_date - relativedelta(months=1)
        if request.POST:
            daily_range = request.POST['daily_range']
            start, end = daily_range.split(' - ')
            start_date = datetime.strptime(start, '%m/%d/%Y').strftime('%Y-%m-%d')
            end_date = datetime.strptime(end, '%m/%d/%Y').strftime('%Y-%m-%d')

        try:
            all_daily = BalanceSnapshot.objects\
                .filter(full_timestamp__range=[start_date, end_date], profile_id=profile_id) \
                .values('full_timestamp', 'bonus_closing_balance')
        except BalanceSnapshot.DoesNotExist:
            all_daily = None

        if all_daily:
            daily_30 = all_daily.order_by('full_timestamp')
            bonus_arr = []
            for bonus in daily_30:
                bonus_arr.append(bonus['bonus_closing_balance'])
            numeric_array = [float(numeric_value) for numeric_value in bonus_arr]
            bonus_list = (", ".join(repr(e) for e in numeric_array))
            try:
                today_bonus = all_daily.get(full_timestamp__date=end_date)['bonus_closing_balance']
            except BalanceSnapshot.DoesNotExist:
                today_bonus = None

            if today_bonus:
                context = {
                    'page': 'daily',
                    'group': name,
                    'bonuses': all_daily,
                    'month': bonus_list,
                    'start_date': start_date,
                    'end_date': end_date
                }
            else:
                context = {
                    'page': 'daily',
                    'group': name,
                    'bonuses': all_daily,
                    'month': bonus_list,
                    'start_date': start_date,
                    'end_date': end_date
                }
            return render_with_global_data(request, 'pochi/earnings.html', context)
        else:
            messages.info(request, 'There are no daily rates yet! Coming soon')
            context = {
                'page': 'daily',
                'group': name,
            }
            return render_with_global_data(request, 'pochi/earnings.html', context)

    elif page == 'monthly':
        if request.POST:
            monthly_range = request.POST['monthly_range']
            start, end = monthly_range.split(' - ')
            start_date = datetime.strptime(start, '%m/%d/%Y').strftime('%Y-%m-%d')
            end_date = datetime.strptime(end, '%m/%d/%Y').strftime('%Y-%m-%d')

        try:
            all_monthly = BalanceSnapshot.objects\
                .filter(full_timestamp__range=[start_date, end_date], profile_id=profile_id) \
                .annotate(month=TruncMonth('full_timestamp')) \
                .values('month') \
                .annotate(bonus=Sum('bonus_closing_balance')) \
                .values('month', 'bonus').order_by('month')
        except BalanceSnapshot.DoesNotExist:
            all_monthly = None

        if all_monthly:
            prev_day = NOW - relativedelta(days=1)
            bonus_arr = []
            for bonus in all_monthly:
                bonus_arr.append(bonus['bonus'])
            numeric_array = [float(numeric_value) for numeric_value in bonus_arr]
            bonus_list = (", ".join(repr(e) for e in numeric_array))
            query_set = all_monthly.filter(full_timestamp__month=prev_date.month, full_timestamp__year=prev_date.year)
            month, bonus = '', 0
            for data in query_set:
                month = data['month']
                bonus = data['bonus']
            month_to_date_bonus = all_monthly.filter(full_timestamp__month=NOW.month, full_timestamp__year=NOW.year)\
                .aggregate(Sum('bonus'))
            context = {
                'page': 'monthly',
                'group': name,
                'bonuses': all_monthly,
                'year': bonus_list,
                'month': month,
                'bonus': bonus,
                'start_date': start_date,
                'end_date': end_date,
                'prev_day': prev_day,
                'month_to_date_bonus': month_to_date_bonus['bonus__sum']
            }
            return render_with_global_data(request, 'pochi/earnings.html', context)
        else:
            messages.info(request, 'There are no monthly rates yet! Coming soon')
            context = {'page': 'monthly', 'group': name}
            return render_with_global_data(request, 'pochi/earnings.html', context)

    elif page == 'total':
        if request.POST:
            total_range = request.POST['total_range']
            start, end = total_range.split(' - ')
            start_date = datetime.strptime(start, '%m/%d/%Y').strftime('%Y-%m-%d')
            end_date = datetime.strptime(end, '%m/%d/%Y').strftime('%Y-%m-%d')

        try:
            bs = BalanceSnapshot.objects\
                .filter(full_timestamp__range=[start_date, end_date], profile_id=profile_id) \
                .annotate(month=TruncMonth('full_timestamp')) \
                .values('month') \
                .annotate(bonus=Sum('bonus_closing_balance')) \
                .values('month', 'bonus').order_by('month')
        except BalanceSnapshot.DoesNotExist:
            bs = None

        if bs:
            bs_arr = []
            cumulative = 0
            for individual in bs:
                cumulative += individual['bonus']
                dto = CumulativeBonusDto(
                    individual['bonus'],
                    individual['month'],
                    cumulative
                )
                bs_arr.append(dto)
            total_bonuses = bs.aggregate(Sum('bonus'))
            cumulative_year_bonuses = bs_arr[-12:]
            context = {
                'page': 'total',
                'total': total_bonuses,
                'history': bs_arr,
                'month': cumulative_year_bonuses,
                'now': datetime.now(),
                'start_date': start_date,
                'end_date': end_date
            }
            return render_with_global_data(request, 'pochi/earnings.html', context)
        else:
            messages.info(request, 'No earnings yet! Coming soon')
            context = {
                'page': 'total',
                'group': name
            }
            return render_with_global_data(request, 'pochi/earnings.html', context)
    else:
        return redirect(admin)


@login_required
def delete_account(request):
    profile_id = request.user.profile.profile_id
    balance = Account.objects.get(profile_id=profile_id).current_balance
    if balance != 0:
        messages.info(request, 'You have to transfer all your funds from POCHI to be able to delete your account!',
                      extra_tags='main')
    elif balance == 0:
        try:
            Account.objects.get(profile_id=profile_id).delete()
        except Account.DoesNotExist:
            pass
        try:
            PaidUser.objects.get(profile_id=profile_id).delete()
        except PaidUser.DoesNotExist:
            pass
        try:
            GroupMember.objects.filter(profile_id=profile_id).delete()
        except GroupMember.DoesNotExist:
            pass
        request.user.is_active = False
        request.user.save()
        return redirect(index)
    return redirect(request.META['HTTP_REFERER'])


def validate_pochi_id(request):
    if request.is_ajax() and request.POST:
        username = request.POST['username']
        try:
            user_obj = User.objects.get(username=username)
            user = '%s %s' % (user_obj.first_name, user_obj.last_name)
        except User.DoesNotExist:
            user = None
        context = {'result': user}
    else:
        context = {'result': None}
    return JsonResponse(context)


def group_admin(request, name, identity, action):
    user = request.user
    if action == 'add':
        try:
            group = Group.objects.get(name=name)
            group_acc = group.account
        except Group.DoesNotExist:
            group_acc = None
            messages.error(request, "Sorry!, an error occurred, cannot complete this action.")

        if group_acc:
            try:
                member_qs = GroupMember.objects.get(profile_id=identity, group_account=group_acc)
                member_qs.admin = 1
                member_qs.save()
                notify.send(user, recipient=user, verb='XXXX is now an admin of ' + name + '!')
            except GroupMember.DoesNotExist:
                messages.error(request, "Sorry!, an error occurred, This member does not exist!")
    elif action == 'remove':
        try:
            group = Group.objects.get(name=name)
            group_acc = group.account
        except Group.DoesNotExist:
            group_acc = None
            messages.error(request, "Sorry!, an error occurred, cannot complete this action.")

        if group_acc:
            try:
                member_qs = GroupMember.objects.get(profile_id=identity, group_account=group_acc)
                member_qs.admin = 0
                member_qs.save()
            except GroupMember.DoesNotExist:
                messages.error(request, "Sorry!, an error occurred, This member does not exist!")
    if action == 'change':
        identity.replace('—', ' ')
        try:
            group = Group.objects.get(name=name)
            group.name = identity
            group.save()
            notify.send(user, recipient=user, verb='Group ' + name + ' was changed to ' + identity + '!')
        except Group.DoesNotExist:
            messages.error(request, "Sorry!, an error occurred, cannot complete this action.")

    return redirect(group_settings, name)


def confirm_action_group(request, name, action):
    if 'addAdmin' in action:
        action_array = action.split('-')
        tag = action_array[0]+' '+action_array[1]
        messages.info(request, "Add this member as an admin of "+name+" group. Continue?",
                      extra_tags=tag)
    elif 'removeAdmin' in action:
        action_array = action.split('-')
        tag = action_array[0] + ' ' + action_array[1]
        messages.warning(request, "This member will no longer be an admin of "+name+" group. Continue?",
                         extra_tags=tag)
    elif 'change' in action:
        if request.POST:
            new_name = request.POST['g_name']
            new_name = re.sub(' +', ' ', new_name.strip())
            new_name.replace(' ', '—')
            tag = action+' '+new_name
            messages.warning(request, "Are you sure you want to "+action+" "+name+" group name?", extra_tags=tag)
    else:
        messages.warning(request, "You are about to "+action+" "+name+" group. Do you wish to proceed?",
                         extra_tags=action)
    return redirect(request.META.get("HTTP_REFERER"))


class UserNotificationsList(AllNotificationsList):
    template_name = 'pochi/notifications.html'


@login_required
def mark_as_read(request, slug=None):
    from notifications.utils import slug2id
    id = slug2id(slug)

    from notifications.models import Notification
    notification = get_object_or_404(
        Notification, recipient=request.user, id=id)
    notification.mark_as_read()

    _next = request.GET.get('next')

    if _next:
        return redirect(_next)

    return redirect('unread')
