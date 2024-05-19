from django.urls import path
from . import views

app_name = 'trailer'

urlpatterns = [
    path('', views.trailer_list, name='trailer_list'),
    path('search/', views.search_trailer, name='search_trailer'),
    path('film/<str:film_id>', views.film_detail, name='film_detail'),
    path('series/<str:series_id>', views.series_detail, name='series_detail'),
    path('episode/<str:id>/<str:sub_judul>', views.episode_detail, name='episode_detail'),
]
