from django.urls import path

from authentication.views import form_login, form_register, login_register

app_name = 'authentication'

urlpatterns = [
    path('login-register/', login_register, name='login-register'),
    path('form-register/', form_register, name='form-register'),
    path('form-login/', form_login, name='form-login'),
]
