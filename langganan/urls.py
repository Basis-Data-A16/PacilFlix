from django.urls import path

from langganan.views import langganan, bayar


urlpatterns = [
    path('', langganan, name='langganan'),
    path('bayar/', bayar, name='bayar'),
    # path('submit/', submit, name='submit'),
]