from django.urls import path
from .views import langganan, bayar

app_name = 'langganan'

urlpatterns = [
    path('', langganan, name='langganan'),
    path('bayar/', bayar, name='bayar'),
]
