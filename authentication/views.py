import pycountry
from django.db import connection
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        with connection.cursor() as cursor:
            cursor.execute((f"SELECT username, negara_asal FROM PENGGUNA WHERE username = '{username}' AND password = '{password}'"))
            data = cursor.fetchall()
        if len(data) != 0:
            username = data[0][0]
            negara_asal = data[0][1]

            request.session['username'] = username
            request.session['negara_asal'] = negara_asal
            request.session['is_authenticated'] = True

            return HttpResponseRedirect(reverse('trailer:trailer_list'))
        else:
            return render(request, 'form_login.html', {'login_failed': True})
    else:
        if request.session.get('is_authenticated'):
            return HttpResponseRedirect(reverse('trailer:trailer_list'))
        return render(request, 'form_login.html')

@csrf_exempt
def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        country = request.POST.get('country')
        error_message = None
        error = False
        try:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO PENGGUNA (username, password, negara_asal) VALUES (%s, %s, %s)", [username, password, country])
        except Exception as e:
            error_message = str(e)
            error = True
            print(error_message)
        if error_message:
            return render(request, 'form_register.html', {'error':error, 'error_message': error_message})
        else:
            return render(request, 'form_login.html')
    else:
        return render(request, 'form_register.html')

def login_register(request):
    if request.session.get('is_authenticated'):
        return HttpResponseRedirect(reverse('trailer:trailer_list'))
    return render(request, 'login_register.html')

def form_register(request):
    if request.session.get('is_authenticated'):
        return HttpResponseRedirect(reverse('trailer:trailer_list'))
    return render(request, 'form_register.html')

def test(request):
    return render(request, "test.html")

def logout(request):
    request.session.flush()
    return HttpResponseRedirect(reverse('authentication:form-login'))
