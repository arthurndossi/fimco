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
from django.shortcuts import render, redirect

from .forms import RegisterForm, LoginForm, CorporateForm1, CorporateForm2, CorporateForm3, CorporateForm4
from .models import KYC, CorporateProfile, Account, Profile


@transaction.atomic
def process_form_data(request):
    options = CorporateProfile.objects.values_list('company_name', flat=True)
    first_tab = 'active'
    second_tab = ''
    if request.POST:
        if request.POST['new_rep']:
            form_1 = CorporateForm1(request.POST or None)
            form_2 = CorporateForm2(request.POST, request.FILES or None)
            form_3 = CorporateForm3(request.POST or None)
            form_4 = CorporateForm4(request.POST, request.FILES or None)

            form_list = [form_1, form_2, form_3, form_4]

            if form_1.is_valid() and form_2.is_valid() and form_3.is_valid() and form_4.is_valid():
                form_data = [form.cleaned_data for form in form_list]

                name = form_data[0]['name']
                contact = form_data[0]['contact']
                address = form_data[0]['address']
                license = request.FILES[1]['license']
                certificate = request.FILES[1]['certificate']
                bot = form_data[2]['bot']
                dse = form_data[2]['dse']
                fName = form_data[3]['fName'].capitalize()
                lName = form_data[3]['lName'].capitalize()
                dob = form_data[3]['dob']
                gender = form_data[3]['gender']
                email = form_data[3]['email']
                id_type = form_data[3]['id_type']
                id_number = form_data[3]['id_number']
                user_id = request.FILES[3]['user_id']
                phone = form_data[3]['phone'].strip()
                password = form_data[3]["password"]
                profile_id = "POC%s" % uuid.uuid4().hex[:6].upper()
                pin = uuid.uuid4().hex[:4].upper()
                with transaction.atomic():
                    CorporateProfile.objects.create(
                        company_name=name,
                        address=address,
                        phone_number=contact,
                        profile_id=profile_id
                    )
                    KYC.objects.create(
                        profile_id=profile_id,
                        kyc_type=id_type,
                        id_number=id_number,
                        document=user_id
                    )
                    user = User.objects.create_user(phone, email, password, first_name=fName, last_name=lName)
                    Profile.objects.create(
                        user=user,
                        dob=dob,
                        gender=gender,
                        bot_cds=bot,
                        dse_cds=dse,
                        profile_id=profile_id,
                        profile_type='C',
                        pin=pin
                    )

                    from_email = email
                    message = ''
                    recipient_list = ['admin@fimco.co.tz']
                    subject = 'Company KYC details'
                    try:
                        mail = EmailMessage(subject, message, from_email, recipient_list)
                        mail.attach(license.name, license.read(), license.content_type)
                        mail.attach(certificate.name, certificate.read(), certificate.content_type)
                        mail.send()
                    except BadHeaderError:
                        messages.error(request, 'Invalid header found.')

                    messages.success(request, 'Your corporate account has been created successfully!')
                    return redirect(request.META['HTTP_REFERER'])
            else:
                messages.error(request, 'One or more fields was not filled. Make sure all fields are filled')
                context = {
                    'cForm': form_1,
                    'kForm': form_2,
                    'aForm': form_3,
                    'uForm': form_4,
                    'first': first_tab,
                    'second': second_tab,
                    'options': options
                }
                return render(request, 'corporate.html', context)
        elif request.POST['add_rep']:
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
                user_id = request.FILES[3]['user_id']
                phone = form.cleaned_data['phone'].strip()
                password = form.cleaned_data["password"]

                profile_id = None
                while profile_id is None:
                    try:
                        profile_id = CorporateProfile.objects.get(company_name=name).profile_id
                    except Error:
                        pass
                with transaction.atomic():
                    user = User.objects.create_user(phone, email, password, first_name=fName, last_name=lName)
                    Profile.objects.create(
                        user=user,
                        dob=dob,
                        gender=gender,
                        profile_id=profile_id,
                        profile_type='C',
                    )
                    KYC.objects.create(
                        profile_id=profile_id,
                        kyc_type=id_type,
                        id_number=id_number,
                        document=user_id
                    )
                    messages.success(request, 'You have been added successfully to '+name+' corporate account!')

            else:
                messages.error(request, 'One or more fields was not filled. Make sure all fields are filled')
                first_tab = ''
                second_tab = 'active'
                return render(request, 'corporate.html', {'adForm': form, 'first': first_tab, 'second': second_tab})

            return redirect(request.META['HTTP_REFERER'])
    context = {
        'cForm': CorporateForm1(),
        'kForm': CorporateForm2(),
        'aForm': CorporateForm3(),
        'uForm': CorporateForm4(),
        'adForm': CorporateForm4(),
        'first': first_tab,
        'second': second_tab,
        'options': options
    }
    return render(request, 'corporate.html', context)


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
        'rForm': RegisterForm()
    }
    return render(request, 'registration.html', context)


@anonymous_required
def login_view(request):
    from .forms import LoginForm
    context = {
        'lForm': LoginForm(),
        'next': request.GET['next'] if request.GET and 'next' in request.GET else ''
    }
    return render(request, 'login.html', context)


def validate(request):
    if request.method == 'POST':
        form = LoginForm(request.POST or None)
        if form.is_valid():
            username = request.POST["username"]
            password = request.POST["password"]
            get_param = request.POST['next']
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
                user = authenticate(username=username, password=password)
            else:
                raise forms.ValidationError("Not a valid email or phone number!")
            if user:
                login(request, user)
                if get_param == "/":
                    from pochi.views import home
                    return redirect(home)
                else:
                    return redirect(get_param)
            else:
                messages.add_message(request, messages.ERROR, 'Incorrect credentials!')
                return render(request, 'login.html', {'lForm': form})
        else:
            return render(request, 'login.html', {'lForm': form})
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
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            fName = form.cleaned_data['fName'].capitalize()
            lName = form.cleaned_data['lName'].capitalize()
            dob = form.cleaned_data['dob']
            gender = form.cleaned_data['gender']
            id_choice = form.cleaned_data['id_choice']
            client_id = form.cleaned_data['client_id']
            scanned_id = form.cleaned_data['scanned_id']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone'].strip()
            password = form.cleaned_data["password"]
            bot = form.cleaned_data['bot_cds']
            dse = form.cleaned_data['dse_cds']
            profile_id = "POC%s" % uuid.uuid4().hex[:6].upper()
            pin = uuid.uuid4().hex[:4].upper()
            user = User.objects.create_user(phone, email, password, first_name=fName, last_name=lName)
            profile = Profile.objects.create(
                user=user,
                dob=dob,
                gender=gender,
                bot_cds=bot,
                dse_cds=dse,
                profile_id=profile_id,
                pin=pin
            )
            account_no = create_account(profile.profile_id)
            KYC.objects.create(
                profile_id=profile.profile_id,
                kyc_type=id_choice,
                id_number=client_id,
                document=scanned_id
            )
            Account.objects.create(
                profile_id=profile.profile_id,
                account=account_no
            )
            messages.info(
                request,
                'Your information is being verified and you will receive notification shortly!'
            )
            return redirect(request.META['HTTP_REFERER'])
        else:
            messages.error(
                request,
                'Something is not right... Please try again!'
            )
            return render(request, 'registration.html', {'rForm': form})

    return redirect(account)


@login_required
def log_out(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect(index)
