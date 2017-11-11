import os
import re
import uuid
from random import randint

from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse

from django.shortcuts import render, redirect
from formtools.wizard.views import SessionWizardView

from .models import KYC, CorporateProfile, PROFILE_ROOT, Account, Profile
from .forms import RegisterForm, LoginForm


def process_form_data(form_list):
    form_data = [form.cleaned_data for form in form_list]
    name = form_data[0]['name']
    contact = form_data[0]['contact']
    address = form_data[0]['address']
    website = form_data[0]['website']
    id_type = form_data[1]['id_type']
    id_number = form_data[1]['id_number']
    scanned_id = form_data[1]['scanned_id']
    fName = form_data[2]['fName'].capitalize()
    lName = form_data[2]['lName'].capitalize()
    dob = form_data[2]['dob']
    gender = form_data[2]['gender']
    email = form_data[2]['email']
    phone = form_data[2]['phone'].strip()
    password = form_data[2]["password"]
    profile_id = "POC%s" % uuid.uuid4().hex[:6].upper()
    pin = uuid.uuid4().hex[:4].upper()
    CorporateProfile.objects.create(
        company_name=name,
        address=address,
        phone_number=contact,
        website=website
    )
    KYC.objects.create(
        profile_id=CorporateProfile.profile_id,
        kyc_type=id_type,
        id_number=id_number,
        document=scanned_id
    )
    user = User.objects.create_user(phone, email, password, first_name=fName, last_name=lName)
    Profile.objects.create(
        user=user,
        dob=dob,
        gender=gender,
        bot_cds='NA',
        dse_cds='NA',
        profile_id=profile_id,
        pin=pin
    )

    pass


class CorporateWizard(SessionWizardView):
    template_name = 'corporate.html'
    file_storage = FileSystemStorage(location=os.path.join(PROFILE_ROOT, 'companies'))
    
    def done(self, form_list, **kwargs):
        process_form_data(form_list)
        resp = {
            'status': 'success',
            'msg': 'Your corporate account has been created successfully!'
        }
        return JsonResponse(resp)


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


def about(request):
    return render(request, 'about.html', {})


def blog_view(request):
    return render(request, 'blog.html', {})


def blog_single_view(request, article):
    return render(request, 'blog-single-page.html', {'article': article})


def info(request, page):
    if page == 'pochi':
        return render(request, 'pochi.html', {})
    elif page == 'market':
        return render(request, 'market-information.html', {})
    else:
        return redirect(index)


def fund(request):
    return render(request, 'fund.html', {})


def brokerage(request):
    return render(request, 'brokerage.html', {})


def terms(request):
    return render(request, "terms_conditions.html", {})


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
                if get_param == "":
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

            return redirect(index)
        else:
            return render(request, 'registration.html', {'rForm': form})

    return redirect(account)


@login_required
def log_out(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect(index)
