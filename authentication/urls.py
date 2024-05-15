from django.urls import path

from authentication.views import (form_register, login, login_register, logout,
                                  register, test)

app_name = 'authentication'

urlpatterns = [
    path('test/', test, name='test'),
    path('', login_register, name='login-register'),
    path('form-register/', form_register, name='form-register'),
    path('form-login/', login, name='form-login'),
    path('logout', logout, name='logout'),
    path('register', register, name='register')
]
