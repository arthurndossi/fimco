from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.shortcuts import render, redirect

from .forms import RegisterForm, LoginForm


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
            client_id = form.cleaned_data['client_id']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone'].strip()
            image = form.cleaned_data['image']
            password = form.cleaned_data["password"]
            bot = form.cleaned_data['bot_cds']
            dse = form.cleaned_data['dse_cds']
            user = User.objects.create_user(phone, email, password, first_name=fName, last_name=lName)
            profile = user.profile
            profile.dob = dob
            profile.gender = gender
            profile.client_id = client_id
            profile.avatar = image
            profile.bot_cds = bot
            profile.dse_cds = dse
            profile.save()

            return redirect(index)
        else:
            return render(request, 'registration.html', {'rForm': form})

    return redirect(account)


@login_required
def log_out(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect(index)
