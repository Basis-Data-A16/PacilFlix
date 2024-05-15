from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.shortcuts import redirect, render

def trailer_list(request):
    # # Ambil data 10 tayangan terbaik pada minggu ini (default: global)
    # top_trailers = Trailer.objects.annotate(max_views=Max('total_views_last_7_days')).order_by('-max_views')[:10]

    # # Jika pengguna telah login dan negara pengguna tersedia, ambil data 10 tayangan terbaik sesuai dengan negara pengguna
    # if request.user.is_authenticated:
    #     user_country = request.user.profile.country # Misalnya, ambil negara pengguna dari profil pengguna
    #     if user_country:
    #         top_trailers = Trailer.objects.filter(country=user_country).annotate(max_views=Max('total_views_last_7_days')).order_by('-max_views')[:10]

    # # Ambil data film
    # films = Film.objects.all()

    # # Ambil data series
    # series = Series.objects.all()

    # context = {
    #     'trailers': top_trailers,
    #     'films': films,
    #     'series': series
    # }
    context = {}
    return render(request, 'daftar_tayangan.html', context)

def search_trailer(request):
    return render(request, 'search_tayangan.html')

def film_detail(request):
    return render(request, 'film_detail.html')

def series_detail(request):
    return render(request, 'series_detail.html')

def episode_detail(request):
    return render(request, 'episode_detail.html')