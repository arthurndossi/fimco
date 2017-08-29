from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from .forms import RegisterForm, EditProfileForm


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


@anonymous_required
def account(request):
    context = {
        'rForm': RegisterForm()
    }
    return render(request, 'invest.html', context)


def login(request):
    from .forms import LoginForm
    context = {
        'lForm': LoginForm()
    }
    return render(request, 'login.html', context)


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            fName = form.cleaned_data['fName'].capitalize()
            lName = form.cleaned_data['lName'].capitalize()
            dob = form.cleaned_data['dob']
            gender = form.cleaned_data['gender']
            client_id = form.cleaned_data['client_id']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone'].strip()
            image = form.cleaned_data['image']
            scanned_id = form.cleaned_data['scanned_id']
            id_choice = form.cleaned_data['id_choice']
            bot = form.cleaned_data['bot_cds']
            dse = form.cleaned_data['dse_cds']
            user = User.objects.create_user(None, email, None, first_name=fName, last_name=lName)
            profile = user.profile
            profile.birth_date = dob
            profile.gender = gender
            profile.identity = client_id
            profile.phone = phone
            profile.image = image
            profile.scanned_id = scanned_id
            profile.identity_type = id_choice
            profile.bot_account = bot
            profile.dse_account = dse
            profile.save()
            user.save()

            return redirect(index(request))
        else:
            return redirect(account)

    return redirect(index(request))


def log_out(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect(index(request))


@login_required
def edit_profile(request):
    user = request.user
    form = EditProfileForm(request.POST or None, request.FILES, initial={
        'fName': user.first_name,
        'mName': user.profile.middle_name,
        'lName': user.last_name,
        'dob': user.profile.birth_date,
        'gender': user.profile.gender,
        'id': user.profile.identity,
        'email': user.email,
        'phone': user.profile.phone,
        'bot_account': user.profile.bot_account,
        'dse_account': user.profile.dse_account,
        'image': user.profile.image
    })
    context = {
        'pForm': form
    }

    return render(request, "profile.html", context)
