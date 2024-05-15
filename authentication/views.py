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

            request = HttpResponseRedirect(reverse('trailer:search_trailer'))
            request.set_cookie('username', username)
            request.set_cookie('negara_asal', negara_asal)
            request.set_cookie('is_authenticated', True)

            return request

        else:
            return render(request, 'form_login.html', {'login_failed': True})
    else:
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
    return render(request, 'login_register.html')

def form_register(request):
    return render(request, 'form_register.html')

def test(request):
    return render(request, "test.html")

def logout(request):
    request = HttpResponseRedirect(reverse('authentication:form-login'))
    request.delete_cookie('username')
    request.delete_cookie('negara_asal')
    request.delete_cookie('is_authenticated')
    return request
