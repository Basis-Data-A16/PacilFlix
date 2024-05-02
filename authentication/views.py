import pycountry
from django.shortcuts import render


def form_register(request):
    countries = [{"code": country.alpha_2, "name": country.name} for country in pycountry.countries]
    return render(request, "form_register.html", {"countries": countries})

def login_register(request):
    return render(request, 'login_register.html')

def form_register(request):
    return render(request, 'form_register.html')

def form_login(request):
    return render(request, 'form_login.html')

