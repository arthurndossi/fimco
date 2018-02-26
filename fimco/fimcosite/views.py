import re
import uuid

from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.core.mail import EmailMessage, BadHeaderError
from django.db import transaction
from django.db.models import Max
from django.shortcuts import render, redirect, render_to_response
from formtools.wizard.views import SessionWizardView

# from .backend import CorporateBackend
from .forms import RegisterForm1, RegisterForm2, IndividualLoginForm, CorporateLoginForm, CorporateForm1, \
    CorporateForm2, CorporateForm3, CorporateForm4, BankAccountForm, UserCorporateForm, EnquiryForm
from .models import KYC, CorporateProfile, Account, Profile, MEDIA_ROOT, CorporateUser


class AnonymousRequired(object):
    def __init__(self, view_function, redirect_to):
        if redirect_to is None:
            redirect_to = '/'
        self.view_function = view_function
        self.redirect_to = redirect_to

    def __call__(self, request, *args, **kwargs):
        if request.user is not None and request.user.is_authenticated():
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(self.redirect_to)
        return self.view_function(request, *args, **kwargs)


def anonymous_required(view_function, redirect_to=None):
    return AnonymousRequired(view_function, redirect_to)


class RegistrationWizard(SessionWizardView):
    form_list = [RegisterForm1, RegisterForm2]
    file_storage = FileSystemStorage(location=MEDIA_ROOT)
    template_name = "registration.html"

    def done(self, form_list, **kwargs):
        form_data = register(form_list)
        if form_data:
            messages.info(
                self.request,
                'Your information is being verified and you will receive notification shortly!'
            )
            context = {
                'form_data': form_data
            }
            return render(self.request, 'registration.html', context)
        else:
            messages.error(
                self.request,
                'Fill in all required details of this form!'
            )
            return redirect('account')


class CorporateWizard(SessionWizardView):
    form_list = [CorporateForm1, CorporateForm2, CorporateForm3, CorporateForm4]
    file_storage = FileSystemStorage(location=MEDIA_ROOT)
    template_name = "corporate.html"

    tab = 'active'
    logged_in = False

    def get_context_data(self, form, **kwargs):
        context = super(CorporateWizard, self).get_context_data(form=form, **kwargs)
        if self.steps.current == self.steps.first:
            extra = {
                'lForm': CorporateLoginForm(),
                'adForm': UserCorporateForm(prefix='ad'),
                'first': self.tab,
                'logged_in': self.logged_in
            }
            context.update(extra)
        elif self.steps.index == 1:
            extra = {
                'first': self.tab,
                'disabled': 'disabled',
                'logged_in': self.logged_in
            }
            context.update(extra)
        elif self.steps.index == 2:
            extra = {
                'first': self.tab,
                'disabled': 'disabled',
                'logged_in': self.logged_in
            }
            context.update(extra)
        elif self.steps.index == 3:
            extra = {
                'first': self.tab,
                'disabled': 'disabled',
                'logged_in': self.logged_in
            }
            context.update(extra)
        return context

    def done(self, form_list, **kwargs):
        form_data = process_form_data(self.request, form_list)
        context = {
            'bForm': BankAccountForm,
            'done': True,
            'message': True,
            'form_data': form_data
        }
        return render_to_response('corporate.html', context)


def index(request):
    return render(request, 'index.html', {})


def blog_single_view(request, article):
    return render(request, 'blog-single-page.html', {'article': article})


def info(request, page):
    if page == 'pochi':
        return render(request, 'pochi.html', {})
    elif page == 'market':
        return render(request, 'market-information.html', {})
    else:
        return redirect(index)


def general_view(request, page):
    if page == 'contact':
        context = {'iForm': EnquiryForm}
    else:
        context = {}
    return render(request, page+'.html', context)


@transaction.atomic
def process_form_data(request, form_list):
    form_data = [form.cleaned_data for form in form_list]

    name = form_data[0]['name']
    place = form_data[0]['place']
    street = form_data[0]['street']
    address = form_data[0]['address']
    location = form_data[0]['location']

    bot = form_data[1]['bot']
    dse = form_data[1]['dse']

    fName = form_data[2]['fName'].capitalize()
    lName = form_data[2]['lName'].capitalize()
    dob = form_data[2]['dob']
    gender = form_data[2]['gender']
    email = form_data[2]['email']
    phone = form_data[2]['phone'].strip().replace('+255', '0')
    password = form_data[2]["password"]

    id_type = form_data[3]['id_type']
    id_number = form_data[3]['id_number']
    license = form_data[3]['license']
    certificate = form_data[3]['certificate']
    user_id = form_data[3]['user_id']
    sms_notify = form_data[3]['notification']

    username = '%s-%s' % (phone, name)  # not sure about duplicates if they may arise here
    company_address = address + '\r' + place + '\r' + street + '\r' + location

    profile_id = "CP%s" % uuid.uuid4().hex[:6].upper()
    pin = uuid.uuid4().hex[:4].upper()
    account_no = create_account()

    with transaction.atomic():
        CorporateProfile.objects.create(
            company_name=name,
            address=company_address,
            account=account_no
        )

        CorporateUser.objects.create(
            profile_id=profile_id,
            account=account_no,
            admin=True
        )

        KYC.objects.create(
            account=account_no,
            kyc_type=id_type,
            id_number=id_number,
            document=user_id
        )

        user = User.objects.create_user(username=username, email=email, password=password, first_name=fName,
                                        last_name=lName, is_active=0)
        profile = Profile(user=user, profile_id=profile_id, dob=dob, msisdn=phone, gender=gender, bot_cds=bot,
                          dse_cds=dse, profile_type='C', pin=pin, sms_notification=sms_notify)
        profile.save()

        Account.objects.create(
            account=account_no,
            nickname=name
        )

        from_email = email
        message = ''
        recipient_list = ['arthur@selcom.net']
        subject = 'Company KYC details'
        try:
            mail = EmailMessage(subject, message, from_email, recipient_list)
            mail.attach(license.name, license.read(), license.content_type)
            mail.attach(certificate.name, certificate.read(), certificate.content_type)
            mail.send()
        except BadHeaderError:
            messages.error(request, 'Invalid header found.')

        return form_data


def add_user_corporate(request):
    tab = 'active'
    logged_in = False
    form = CorporateLoginForm

    if 'login' in request.POST:
        form = CorporateLoginForm(request.POST or None)
        if form.is_valid():
            pochi_id = form.cleaned_data["id"]
            request.session['company_id'] = pochi_id
            username = form.cleaned_data["corp_rep"]
            password = form.cleaned_data["password"]
            user = corporate_authentication(request, username, password, pochi_id, 'admin')
            if user:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                logged_in = True
                company = CorporateProfile.objects.get(account=pochi_id).company_name
                members = CorporateUser.objects.filter(account=pochi_id).values_list('profile_id', flat=True)
                corporate_users = []
                for member in members:
                    corporate_user = User.objects.select_related('profile').get(profile__profile_id=member)\
                        .get_full_name()
                    corporate_users.append(corporate_user)
                context = {
                    'second': tab,
                    'inactive': 'disabled',
                    'adForm': UserCorporateForm,
                    'company': company,
                    'users': corporate_users,
                    'logged_in': logged_in
                }
                return render(request, 'corporate.html', context)
            else:
                context = {
                    'second': tab,
                    'lForm': form,
                    'logged_in': logged_in
                }
                return render(request, 'login.html', context)
        else:
            return render(request, 'login.html', {'second': tab, 'lForm': form, 'logged_in': logged_in})
    elif 'addRep' in request.POST:
        form = UserCorporateForm(request.POST, request.FILES or None)
        if form.is_valid():
            fName = form.cleaned_data['fName'].capitalize()
            lName = form.cleaned_data['lName'].capitalize()
            dob = form.cleaned_data['dob']
            gender = form.cleaned_data['gender']
            email = form.cleaned_data['email']
            id_type = form.cleaned_data['id_type']
            id_number = form.cleaned_data['id_number']
            user_id = request.FILES['user_id']
            phone = form.cleaned_data['phone'].strip().replace('+255', '0')
            password = form.cleaned_data["password"]
            sms_notify = form.cleaned_data['notification']
            profile_id = "CP%s" % uuid.uuid4().hex[:6].upper()

            pochi_id = request.session['company_id']
            company = CorporateProfile.objects.get(account=pochi_id).company_name
            username = '%s-%s' % (phone, company)

            with transaction.atomic():
                user = User.objects.create_user(username=username, email=email, password=password, first_name=fName,
                                                last_name=lName, is_active=0)
                profile = Profile(user=user, dob=dob, gender=gender, msisdn=phone, profile_type='C',
                                  profile_id=profile_id, sms_notification=sms_notify)
                profile.save()

                CorporateUser.objects.create(
                    profile_id=profile_id,
                    account=pochi_id,
                    admin=False
                )

                KYC.objects.create(
                    account=pochi_id,
                    kyc_type=id_type,
                    id_number=id_number,
                    document=user_id
                )

                messages.success(request, 'You have been added successfully to ' + company + ' corporate account!')
            return redirect("corporate")
        else:
            pochi_id = request.session['company_id']
            company = CorporateProfile.objects.get(account=pochi_id).company_name
            members = CorporateUser.objects.filter(account=pochi_id).values_list('profile_id', flat=True)
            corporate_users = []
            for member in members:
                corporate_user = User.objects.select_related('profile').get(profile__profile_id=member).get_full_name()
                corporate_users.append(corporate_user)
            context = {
                'second': tab,
                'inactive': 'disabled',
                'adForm': form,
                'company': company,
                'users': corporate_users,
                'logged_in': True
            }
            return render(request, 'corporate.html', context)
    else:
        context = {
            'second': tab,
            'inactive': 'disabled',
            'lForm': form,
            'logged_in': logged_in
        }
        return render(request, 'corporate.html', context)


@anonymous_required
def login_view(request, tab='user'):

    context = {
        tab: 'active',
        'lForm': IndividualLoginForm(),
        'cForm': CorporateLoginForm(prefix='corp'),
        'next': request.GET['next'] if request.GET and 'next' in request.GET else ''
    }
    return render(request, 'login.html', context)


def validate_credentials(request, form, username, password, _next, category, pochi=None, new_user=False):
    if re.match(r"[^@]+@[^@]+\.[^@]+", username):
        if category == 'user':
            username = User.objects.get(email=username).username
            user = authenticate(username=username, password=password)
        else:
            user = corporate_authentication(request, username, password, pochi, 'admin')
    elif re.match(r'^([+]?(\d{1,3}\s?)|[0])\s?\d+(\s?-?\d{2,4}){1,3}?$', username):
        username = User.objects.select_related('profile').get(profile__msisdn__exact=username).username
        user = authenticate(username=username, password=password)
    else:
        raise forms.ValidationError("Not a valid email or phone number!")

    if user:
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        current_url = request.resolver_match.url_name
        if _next == "/" or "pochi" not in current_url:
            if new_user:
                company = CorporateProfile.objects.get(account=pochi).company_name
                members = CorporateUser.objects.get(account=pochi).values_list('profile_id', flat=True)
                corporate_users = []
                for member in members:
                    corporate_user = User.objects.select_related('profile').get(profile__profile_id__exact=member)\
                        .get_full_name()
                    corporate_users.append(corporate_user)
                context = {
                    'second': 'active',
                    'inactive': 'disabled',
                    'adForm': UserCorporateForm,
                    'company': company,
                    'users': corporate_users,
                    'logged_in': True
                }
                return render(request, 'corporate.html', context)
            else:
                from pochi.views import home
                return redirect(home)
        else:
            return redirect(_next)
    else:
        if category == 'user':
            context = {
                'user': 'active',
                'lForm': form,
                'cForm': CorporateLoginForm(prefix='corp'),
                'next': request.GET['next'] if request.GET and 'next' in request.GET else ''
            }
        else:
            messages.error(request, "Wrong username or password!")
            context = {
                'corporate': 'active',
                'lForm': IndividualLoginForm(),
                'cForm': form,
                'next': request.GET['next'] if request.GET and 'next' in request.GET else ''
            }
        return render(request, 'login.html', context)


def validate(request):
    if request.method == 'POST':
        tab = 'active'
        if 'user' in request.POST:
            form = IndividualLoginForm(request.POST or None)
            if form.is_valid():
                username = form.cleaned_data["username"]
                password = form.cleaned_data["password"]
                get_param = request.POST['next']
                return validate_credentials(request, form, username, password, get_param, 'user')
            else:
                return render(request, 'login.html', {'lForm': form, 'user': tab})
        elif 'corporate' in request.POST:
            form = CorporateLoginForm(request.POST or None, prefix='corp')
            if form.is_valid():
                pochi_id = form.cleaned_data["id"]
                rep = form.cleaned_data["corp_rep"]
                password = form.cleaned_data["password"]
                get_param = request.POST['next']
                if request.is_ajax():
                    return validate_credentials(request, form, rep, password, get_param, 'corporate', pochi_id, True)
                else:
                    return validate_credentials(request, form, rep, password, get_param, 'corporate', pochi_id)
            else:
                return redirect(login_view, tab='corporate')
        else:
            return redirect(login_view)
    else:
        return redirect(login_view)


def make_random_number(f):
    def random_number(n):
        l = (n >> 16) & 65535
        r = n & 65535
        for _ in (1, 2, 3):
            l, r = r, l ^ f(r)
        return ((r & 65535) << 16) + l
    return random_number


def sample_f(x):
    return int((((1366 * x + 150889) % 718925) * 32767) // 718925)


def create_account():
    max_agg = Account.objects.aggregate(Max('id'))
    max_id = 0 if max_agg['id__max'] is None else max_agg['id__max']
    random_number = make_random_number(sample_f)
    account_no = 'P%011d' % luhn_sign(random_number(max_id))
    return account_no


def register(form_list):
    if form_list:
        form_data = [form.cleaned_data for form in form_list]

        fName = form_data[0]['fName'].capitalize()
        lName = form_data[0]['lName'].capitalize()
        dob = form_data[0]['dob']
        gender = form_data[0]['gender']
        email = form_data[0]['email']
        phone = form_data[0]['phone'].strip().replace('+255', '0')
        username = '%s-%s' % (fName, phone)
        password = form_data[0]["password"]

        id_choice = form_data[1]['id_choice']
        client_id = form_data[1]['client_id']
        scanned_id = form_data[1]['scanned_id']
        bot = form_data[1]['bot_cds']
        dse = form_data[1]['dse_cds']
        sms_notify = form_data[1]['notification']

        profile_id = "POC%s" % uuid.uuid4().hex[:6].upper()
        pin = uuid.uuid4().hex[:4].upper()
        account_no = create_account()

        with transaction.atomic():
            user = User.objects.create_user(username=username, email=email, password=password, first_name=fName,
                                            last_name=lName, is_active=0)
            profile = Profile(user=user, profile_id=profile_id, dob=dob, gender=gender, msisdn=phone, bot_cds=bot,
                              dse_cds=dse, profile_type='I', pin=pin, sms_notification=sms_notify)
            profile.save()

            KYC.objects.create(
                account=account_no,
                kyc_type=id_choice,
                id_number=client_id,
                document=scanned_id
            )

            Account.objects.create(
                profile_id=profile_id,
                nickname=fName,
                account=account_no
            )

            return form_data
    else:
        return None


@login_required
def log_out(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect(index)


def inquiry(request):
    if request.POST:
        form = EnquiryForm(request.POST or None)
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            phone = form.cleaned_data["phone"]
            subject = form.cleaned_data["subject"]
            message = form.cleaned_data["message"]
            attachment = form.cleaned_data["attachment"]

            from_email = email
            msg = name+'\r\n'+phone+'\r\n'+message
            recipient_list = ['arthur@selcom.net']  # ivan@fimco.co.tz
            try:
                mail = EmailMessage(subject, msg, from_email, recipient_list)
                mail.attach(attachment.name, attachment.read(), attachment.content_type)
                mail.send()
            except BadHeaderError:
                messages.error(request, 'Invalid header found.')

            messages.success(request, "Your message is sent successfully!")

    return redirect(request.META['HTTP_REFERER'])


def luhn_checksum(n):
    digits = digits_of(n)
    checksum = (sum(digits[-2::-2]) + sum(sum2digits(d << 1) for d in digits[-1::-2])) % 10
    return checksum and 10 - checksum or 0


def luhn_sign(n):
    return luhn_checksum(n) + (n << 3) + (n << 1)


def is_luhn_valid(n):
    digits = digits_of(n)
    checksum = sum(digits[-1::-2]) + sum(sum2digits(d << 1) for d in digits[-2::-2])
    return checksum % 10 == 0


def digits_of(n):
    return [int(d) for d in str(n)]


def sum2digits(d):
    return (d // 10) + (d % 10)


def corporate_authentication(request, username=None, password=None, pochi=None, access='normal'):
    if is_luhn_valid(int(pochi[1:])):
        try:
            company = CorporateProfile.objects.get(account=pochi)
            try:
                username = User.objects.get(email__exact=username).username
                user = authenticate(username=username, password=password)
                if user:
                    try:
                        profile_id = Profile.objects.get(user__username=username).profile_id
                        corp_user_obj = CorporateUser.objects.get(profile_id=profile_id)
                        if access == 'normal':
                            if corp_user_obj:
                                return user
                            else:
                                messages.error(request, 'Sorry, you are not a corporate user in '
                                               + company.company_name + '.\r\n' +
                                               'Please contact your corporate admin to add you as a user.')
                                return None
                        else:
                            if corp_user_obj.admin:
                                return user
                            else:
                                messages.error(request, 'You need admin rights to add a new user.\r\n'
                                                        'Please contact your corporate admin to add another user.')
                                return None
                    except Profile.DoesNotExist or CorporateUser.DoesNotExist:
                        return None
                else:
                    messages.error(request, 'Wrong username or password!')
                    return None
            except User.DoesNotExist:
                messages.error(request, 'Wrong username or password!')
                return None
        except CorporateProfile.DoesNotExist:
            return None
    else:
        messages.error(request, "Invalid account number!")
