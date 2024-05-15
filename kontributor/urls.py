from django.urls import path

from kontributor.views import kontributor_list

app_name = 'kontributor'

urlpatterns = [
    path('', kontributor_list, name='kontributor')
    # path('submit/', submit, name='submit'),
]