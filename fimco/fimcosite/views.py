import re
import uuid
from random import randint

from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import EmailMessage, BadHeaderError
from django.db import transaction, Error
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.shortcuts import render, redirect

from .backend import CorporateBackend
from .forms import RegisterForm1, RegisterForm2, IndividualLoginForm, CorporateLoginForm, CorporateForm1, \
    CorporateForm2, CorporateForm3, CorporateForm4, BankAccountForm, UserCorporateForm
from .models import KYC, CorporateProfile, Account, Profile


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


@receiver(pre_save, sender=Profile)
def user_handler(sender, instance, **kwargs):
    print instance.user
    if instance.profile_type == 'C':
        profile = Profile.objects.filter(user__username=instance.user.username, profile_type='C').exists()
    else:
        profile = Profile.objects.filter(user__username=instance.user.username, profile_type='I').exists()
    if profile:
        raise ValueError('Cannot create this Profile, you already have one registered in the system!')


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
    return render(request, page+'.html', {})


@anonymous_required
def account(request):
    context = {
        'rForm1': RegisterForm1()
    }
    return render(request, 'registration.html', context)


@transaction.atomic
def process_form_data(request):
    options = CorporateProfile.objects.values_list('company_name', flat=True)
    tab = 'active'
    step = 'active'
    logged_in = False
    if request.POST:
        if 'login' in request.POST:
            form = CorporateLoginForm(request.POST or None)
            if form.is_valid():
                pochi_id = form.cleaned_data["id"]
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
                    user = CorporateBackend.authenticate(username, password, pochi_id)
                else:
                    raise forms.ValidationError("Not a valid email or phone number!")

                if user:
                    login(request, user)
                    logged_in = True
                    company = CorporateProfile.objects.get(profile_id=pochi_id).company_name
                    members = Profile.objects.filter(profile_id=pochi_id).values_list('user__username', flat=True)
                    corporate_users = []
                    for member in members:
                        user_obj = User.objects.select_related('profile').get(username=member)
                        corporate_user = user_obj.get_full_name()
                        corporate_users.append(corporate_user)
                    context = {
                        'second': tab,
                        'cForm': form,
                        'company': company,
                        'users': corporate_users,
                        'logged_in': logged_in
                    }
                    return render(request, 'corporate.html', context)
                else:
                    messages.add_message(request, messages.ERROR, 'Incorrect credentials!')
                    return render(request, 'login.html', {'second': tab, 'cForm': form, 'logged_in': logged_in})
            else:
                return render(request, 'login.html', {'second': tab, 'cForm': form, 'logged_in': logged_in})
        if 'name' in request.POST:
            form = CorporateForm1(request.POST or None)
            if form.is_valid():
                name = form.cleaned_data['name']
                place = form.cleaned_data['place']
                street = form.cleaned_data['street']
                address = form.cleaned_data['address']
                location = form.cleaned_data['location']

                request.session['name'] = name
                request.session['place'] = place
                request.session['street'] = street
                request.session['location'] = location
                request.session['address'] = address
                context = {
                    'aForm': CorporateForm2(),
                    'first': tab,
                    'step2': step,
                    'logged_in': logged_in
                }
                return render(request, 'corporate.html', context)
            else:
                context = {
                    'cForm': form,
                    'first': tab,
                    'step1': step,
                    'logged_in': logged_in
                }
                return render(request, 'corporate.html', context)
        elif 'bot' in request.POST:
            form = CorporateForm2(request.POST or None)
            if form.is_valid():
                bot = form.cleaned_data['bot']
                dse = form.cleaned_data['dse']

                request.session['bot'] = bot
                request.session['dse'] = dse
                context = {
                    'uForm': CorporateForm3(),
                    'first': tab,
                    'step3': step,
                    'logged_in': logged_in
                }
                return render(request, 'corporate.html', context)
            else:
                context = {
                    'aForm': form,
                    'first': tab,
                    'step2': step,
                    'logged_in': logged_in
                }
                return render(request, 'corporate.html', context)
        elif 'new' in request.POST:
            form = CorporateForm3(request.POST or None)
            if form.is_valid():
                fName = form.cleaned_data['fName'].capitalize()
                lName = form.cleaned_data['lName'].capitalize()
                dob = form.cleaned_data['dob']
                gender = form.cleaned_data['gender']
                email = form.cleaned_data['email']
                phone = form.cleaned_data['phone'].strip()
                password = form.cleaned_data["password"]

                request.session['fName'] = fName
                request.session['lName'] = lName
                request.session['dob'] = dob.isoformat()
                request.session['gender'] = gender
                request.session['email'] = email
                request.session['phone'] = phone
                request.session['password'] = password
                context = {
                    'kForm': CorporateForm4(),
                    'first': tab,
                    'step4': step,
                    'logged_in': logged_in
                }
                return render(request, 'corporate.html', context)
            else:
                context = {
                    'uForm': form,
                    'first': tab,
                    'step3': step,
                    'logged_in': logged_in
                }
                return render(request, 'corporate.html', context)
        elif 'id_type' in request.POST:
            form = CorporateForm4(request.POST, request.FILES or None)
            if form.is_valid():
                id_type = form.cleaned_data['id_type']
                id_number = form.cleaned_data['id_number']
                license = request.FILES['license']
                certificate = request.FILES['certificate']
                user_id = request.FILES['user_id']

                name = request.session['name']
                place = request.session['place']
                street = request.session['street']
                location = request.session['location']
                address = request.session['address']
                bot = request.session['bot']
                dse = request.session['dse']
                fName = request.session['fName']
                lName = request.session['lName']
                dob = request.session['dob']
                gender = request.session['gender']
                email = request.session['email']
                phone = request.session['phone']
                password = request.session['password']

                company_address = address + '\r' + place + '\r' + street + '\r' + location

                profile_id = "CP%s" % uuid.uuid4().hex[:6].upper()
                pin = uuid.uuid4().hex[:4].upper()
                account_no = create_account(profile_id)

                with transaction.atomic():
                    CorporateProfile.objects.create(
                        company_name=name,
                        address=company_address,
                        profile_id=profile_id
                    )

                    KYC.objects.create(
                        profile_id=profile_id,
                        kyc_type=id_type,
                        id_number=id_number,
                        document=user_id
                    )

                    user = User(phone, email, password, first_name=fName, last_name=lName, is_active=0)
                    profile = Profile(user=user, profile_id=profile_id, dob=dob, gender=gender, bot_cds=bot,
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

                    messages.success(request, 'Your corporate account has been created successfully!')
                    context = {
                        'bForm': BankAccountForm,
                        'first': tab,
                        'step5': step,
                        'logged_in': logged_in
                    }
                    return render(request, 'corporate.html', context)
            else:
                context = {
                    'kForm': form,
                    'first': tab,
                    'step4': step,
                    'logged_in': logged_in
                }
                return render(request, 'corporate.html', context)
        elif 'add_rep' in request.POST:
            form = CorporateForm4(request.POST, request.FILES or None)
            if form.is_valid():
                name = request.POST['company']
                fName = form.cleaned_data['fName'].capitalize()
                lName = form.cleaned_data['lName'].capitalize()
                dob = form.cleaned_data['dob']
                gender = form.cleaned_data['gender']
                email = form.cleaned_data['email']
                id_type = form.cleaned_data['id_type']
                id_number = form.cleaned_data['id_number']
                user_id = request.FILES['user_id']
                phone = form.cleaned_data['phone'].strip()
                password = form.cleaned_data["password"]

                profile_id = None
                while profile_id is None:
                    try:
                        profile_id = CorporateProfile.objects.get(company_name=name).profile_id
                    except Error:
                        pass

                with transaction.atomic():
                    user = User(phone, email, password, first_name=fName, last_name=lName, is_active=0)
                    profile = Profile(user=user, dob=dob, gender=gender, profile_type='C', profile_id=profile_id)
                    profile.save()

                    KYC.objects.create(
                        profile_id=profile_id,
                        kyc_type=id_type,
                        id_number=id_number,
                        document=user_id
                    )

                    messages.success(request, 'You have been added successfully to '+name+' corporate account!')

            return render(request, 'corporate.html', {'adForm': form, 'second': tab})
    context = {
        'cForm': CorporateForm1(),
        'aForm': CorporateForm2(),
        'uForm': CorporateForm3(),
        'kForm': CorporateForm4(),
        'lForm': CorporateLoginForm(),
        'adForm': UserCorporateForm(prefix='ad'),
        'first': tab,
        'step1': step,
        'logged_in': logged_in
    }
    return render(request, 'corporate.html', context)


@anonymous_required
def login_view(request):

    context = {
        'user': 'active',
        'lForm': IndividualLoginForm(),
        'cForm': CorporateLoginForm(),
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
            user = CorporateBackend.authenticate(username, password, pochi)
    else:
        raise forms.ValidationError("Not a valid email or phone number!")

    if user:
        login(request, user)
        current_url = request.resolver_match.url_name
        if _next == "/" or "pochi" not in current_url:
            from pochi.views import home
            return redirect(home)
        else:
            return redirect(_next)
    else:
        messages.add_message(request, messages.ERROR, 'Incorrect credentials!')
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


def register(request):
    if request.method == 'POST':
        if 'one' in request.POST:
            form = RegisterForm1(request.POST or None)
            if form.is_valid():
                fName = form.cleaned_data['fName'].capitalize()
                lName = form.cleaned_data['lName'].capitalize()
                dob = form.cleaned_data['dob']
                gender = form.cleaned_data['gender']
                email = form.cleaned_data['email']
                phone = form.cleaned_data['phone'].strip()
                password = form.cleaned_data["password"]

                request.session['fName'] = fName
                request.session['lName'] = lName
                request.session['dob'] = dob.isoformat()
                request.session['gender'] = gender
                request.session['email'] = email
                request.session['phone'] = phone
                request.session['password'] = password
                return render(request, 'registration.html', {'rForm2': RegisterForm2()})
            else:
                return render(request, 'registration.html', {'rForm1': form})
        elif 'two' in request.POST:
            form = RegisterForm2(request.POST, request.FILES or None)
            if form.is_valid():
                id_choice = form.cleaned_data['id_choice']
                client_id = form.cleaned_data['client_id']
                scanned_id = form.cleaned_data['scanned_id']
                bot = form.cleaned_data['bot_cds']
                dse = form.cleaned_data['dse_cds']
            else:
                return render(request, 'registration.html', {'rForm2': form})

            fName = request.session['fName']
            lName = request.session['lName']
            dob = request.session['dob']
            gender = request.session['gender']
            email = request.session['email']
            phone = request.session['phone']
            password = request.session['password']

            del request.session['fName']
            del request.session['lName']
            del request.session['dob']
            del request.session['gender']
            del request.session['email']
            del request.session['phone']
            del request.session['password']

            profile_id = "POC%s" % uuid.uuid4().hex[:6].upper()
            pin = uuid.uuid4().hex[:4].upper()
            account_no = create_account(profile_id)

            with transaction.atomic():
                user = User.objects.create_user(phone, email, password, first_name=fName, last_name=lName, is_active=0)
                profile = Profile(user=user, profile_id=profile_id, dob=dob, gender=gender, bot_cds=bot,
                                  dse_cds=dse, profile_type='I', pin=pin)
                profile.save()
                user.save()

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
                return redirect(request.META['HTTP_REFERER'])

    return redirect(account)


@login_required
def log_out(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect(index)
