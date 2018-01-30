import re
import uuid
from random import randint

from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.core.mail import EmailMessage, BadHeaderError
from django.db import transaction
from django.shortcuts import render, redirect, render_to_response
from formtools.wizard.views import SessionWizardView

from .backend import CorporateBackend
from .forms import RegisterForm1, RegisterForm2, IndividualLoginForm, CorporateLoginForm, CorporateForm1, \
    CorporateForm2, CorporateForm3, CorporateForm4, BankAccountForm, UserCorporateForm, EnquiryForm
from .models import KYC, CorporateProfile, Account, Profile, MEDIA_ROOT


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

    # @anonymous_required
    # def get_context_data(self, form, **kwargs):
    #     context = super(RegistrationWizard, self).get_context_data(form=form, **kwargs)
    #     return context

    def done(self, form_list, **kwargs):
        form_data = register(self.request, form_list)
        context = {
            'form_data': form_data
        }
        return render_to_response('registration.html', context)


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
    phone = '%s-%s' % ('C', form_data[2]['phone'].strip().replace('+255', '0'))
    password = form_data[2]["password"]

    id_type = form_data[3]['id_type']
    id_number = form_data[3]['id_number']
    license = form_data[3]['license']
    certificate = form_data[3]['certificate']
    user_id = form_data[3]['user_id']

    company_address = address + '\r' + place + '\r' + street + '\r' + location

    profile_id = "CP%s" % uuid.uuid4().hex[:6].upper()
    pin = uuid.uuid4().hex[:4].upper()
    account_no = create_account(profile_id)

    with transaction.atomic():
        CorporateProfile.objects.create(
            company_name=name,
            address=company_address,
            account=account_no,
            admin=profile_id
        )

        KYC.objects.create(
            profile_id=profile_id,
            kyc_type=id_type,
            id_number=id_number,
            document=user_id
        )

        user = User(username=phone, email=email, password=password, first_name=fName, last_name=lName, is_active=0)
        user.save()
        profile = Profile(user=user, profile_id=profile_id, dob=dob, msisdn=phone, gender=gender, bot_cds=bot,
                          dse_cds=dse, profile_type='C', pin=pin)
        profile.save()

        Account.objects.create(
            profile_id=profile_id,
            account=account_no
        )

        from_email = email
        message = ''
        recipient_list = ['ivan@fimco.co.tz']
        subject = 'Company KYC details'
        # try:
        #     mail = EmailMessage(subject, message, from_email, recipient_list)
        #     mail.attach(license.name, license.read(), license.content_type)
        #     mail.attach(certificate.name, certificate.read(), certificate.content_type)
        #     mail.send()
        # except BadHeaderError:
        #     messages.error(request, 'Invalid header found.')

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
            if re.match(r"[^@]+@[^@]+\.[^@]+", username):
                try:
                    user = User.objects.get(email=username)
                    if user.check_password(password):
                        user = user
                    else:
                        user = None
                except User.DoesNotExist:
                    user = None
            elif re.match(r'^([+]?(\d{1,3}\s?)|[0])\s?\d+(\s?-?\d{2,4}){1,3}?$', username):
                user = CorporateBackend.authenticate(request, username, password, pochi_id, 'admin')
            else:
                raise forms.ValidationError("Not a valid email or phone number!")

            if user:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                logged_in = True
                company = CorporateProfile.objects.get(account=pochi_id).company_name
                profile_id = Account.objects.get(account=pochi_id).profile_id
                members = Profile.objects.filter(profile_id=profile_id).values_list('user__username', flat=True)
                corporate_users = []
                for member in members:
                    user_obj = User.objects.select_related('profile').get(username=member)
                    corporate_user = user_obj.get_full_name()
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
            phone = '%s-%s' % ('C', form.cleaned_data['phone'].strip().replace('+255', '0'))
            password = form.cleaned_data["password"]
            profile_id = "CP%s" % uuid.uuid4().hex[:6].upper()

            pochi_id = request.session['company_id']
            company = CorporateProfile.objects.get(account=pochi_id).company_name

            with transaction.atomic():
                user = User(username=phone, email=email, password=password, first_name=fName, last_name=lName,
                            is_active=0)
                user.save()
                profile = Profile(user=user, dob=dob, gender=gender, msisdn=phone, profile_type='C',
                                  profile_id=profile_id)
                profile.save()

                KYC.objects.create(
                    profile_id=profile_id,
                    kyc_type=id_type,
                    id_number=id_number,
                    document=user_id
                )

                messages.success(request, 'You have been added successfully to ' + company + ' corporate account!')
            return redirect("corporate")
        else:
            pochi_id = request.session['company_id']
            company = CorporateProfile.objects.get(account=pochi_id).company_name
            profile_id = Account.objects.get(account=pochi_id).profile_id
            members = Profile.objects.filter(profile_id=profile_id).values_list('user__username', flat=True)
            corporate_users = []
            for member in members:
                user_obj = User.objects.select_related('profile').get(username=member)
                corporate_user = user_obj.get_full_name()
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
def login_view(request):

    context = {
        'user': 'active',
        'lForm': IndividualLoginForm(),
        'cForm': CorporateLoginForm(prefix='corp'),
        'next': request.GET['next'] if request.GET and 'next' in request.GET else ''
    }
    return render(request, 'login.html', context)


def validate_credentials(request, form, username, password, _next, category, pochi=None):
    if re.match(r"[^@]+@[^@]+\.[^@]+", username):
        try:
            user = User.objects.get(email=username)
            if user.check_password(password):
                user = user
            else:
                user = None
        except User.DoesNotExist:
            user = None
    elif re.match(r'^([+]?(\d{1,3}\s?)|[0])\s?\d+(\s?-?\d{2,4}){1,3}?$', username):
        if category == 'user':
            user = authenticate(username=username, password=password)
        else:
            user = CorporateBackend.authenticate(request, username, password, pochi)
    else:
        raise forms.ValidationError("Not a valid email or phone number!")

    if user:
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        current_url = request.resolver_match.url_name
        if _next == "/" or "pochi" not in current_url:
            from pochi.views import home
            return redirect(home)
        else:
            return redirect(_next)
    else:
        if category == 'user':
            context = {'lForm': form, 'user': 'active'}
        else:
            context = {'cForm': form, 'corporate': 'active'}
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
            form = CorporateLoginForm(request.POST or None)
            if form.is_valid():
                pochi_id = form.cleaned_data["id"]
                rep = form.cleaned_data["corp_rep"]
                password = form.cleaned_data["password"]
                get_param = request.POST['next']
                return validate_credentials(request, form, rep, password, get_param, 'corporate', pochi_id)
            else:
                return render(request, 'login.html', {'cForm': form, 'corporate': tab})
        else:
            redirect(login_view)
    else:
        return redirect(login_view)


def create_account(profile_id):
    max_count = len(profile_id) - 1
    no1 = randint(0, max_count)
    no2 = randint(0, max_count)
    letter_one = profile_id[no1]
    letter_two = profile_id[no2]
    from datetime import datetime
    now = datetime.now()
    number_one_str = str(now.hour)
    number_two_str = str(now.microsecond)
    if len(number_one_str) != 2:
        str_one = '0'+number_one_str
    else:
        str_one = number_one_str
    if len(number_two_str) != 6:
        pads = 6 - len(number_two_str)
        pad_string = '0'
        for i in range(1, pads):
            pad_string += pad_string
        str_two = pad_string + number_two_str
    else:
        str_two = number_two_str
    account_no = str_one+letter_one+str_two+letter_two

    return account_no


def register(request, form_list):
    form_data = [form.cleaned_data for form in form_list]

    fName = form_data[0]['fName'].capitalize()
    lName = form_data[0]['lName'].capitalize()
    dob = form_data[0]['dob']
    gender = form_data[0]['gender']
    email = form_data[0]['email']
    phone = form_data[0]['phone'].strip().replace('+255', '0')
    password = form_data[0]["password"]

    id_choice = form_data[1]['id_choice']
    client_id = form_data[1]['client_id']
    scanned_id = form_data[1]['scanned_id']
    bot = form_data[1]['bot_cds']
    dse = form_data[1]['dse_cds']

    profile_id = "POC%s" % uuid.uuid4().hex[:6].upper()
    pin = uuid.uuid4().hex[:4].upper()
    account_no = create_account(profile_id)

    with transaction.atomic():
        user = User(username=phone, email=email, password=password, first_name=fName, last_name=lName, is_active=0)
        user.save()
        profile = Profile(user=user, profile_id=profile_id, dob=dob, gender=gender, msisdn=phone, bot_cds=bot,
                          dse_cds=dse, profile_type='I', pin=pin)
        profile.save()

        KYC.objects.create(
            profile_id=profile_id,
            kyc_type=id_choice,
            id_number=client_id,
            document=scanned_id
        )

        Account.objects.create(
            profile_id=profile_id,
            account=account_no
        )

        messages.info(
            request,
            'Your information is being verified and you will receive notification shortly!'
        )
        return form_data


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
