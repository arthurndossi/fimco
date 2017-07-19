from django.shortcuts import render


def index(request):
    return render(request, 'index.html', {})


def contact(request):
    return render(request, 'contact-us.html', {})


def services(request):
    return render(request, 'services.html', {})


def blog(request):
    return render(request, 'blog.html', {})


def clients(request):
    return render(request, 'clients.html', {})


def about(request):
    return render(request, 'about.html', {})


def register(request):
    return render(request, 'register_login.html', {})
