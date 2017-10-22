import os

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse

from django.shortcuts import render, redirect
from formtools.wizard.views import SessionWizardView

from .models import KYC, CorporateProfile, PROFILE_ROOT
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
    profile = user.profile
    profile.dob = dob
    profile.gender = gender
    profile.bot_cds = 'NA'
    profile.dse_cds = 'NA'
    profile.save()

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


def info(request):
    return render(request, 'pochi.html', {})


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
            username = request.POST["phone"]
            password = request.POST["password"]
            get_param = request.POST['next']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                if get_param == "":
                    return redirect(index)
                else:
                    return redirect(get_param)
            else:
                messages.add_message(request, messages.ERROR, 'Incorrect credentials!')
                return render(request, 'login.html', {'lForm': form})
        else:
            return render(request, 'login.html', {'lForm': form})
    else:
        return redirect(login_view)


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
            user = User.objects.create_user(phone, email, password, first_name=fName, last_name=lName)
            profile = user.profile
            profile.dob = dob
            profile.gender = gender
            profile.bot_cds = bot
            profile.dse_cds = dse
            profile.profile_type = 'C'
            profile.save()
            KYC.objects.create(profile_id=profile.profile_id, kyc_type=id_choice, id_number=client_id, document=scanned_id)

            return redirect(index)
        else:
            return render(request, 'registration.html', {'rForm': form})

    return redirect(account)


@login_required
def log_out(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect(index)
