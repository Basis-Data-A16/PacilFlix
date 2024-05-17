from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.http import Http404
from django.shortcuts import redirect, render
from django.db import connection

def trailer_list(request):   
    top_10_selection = 'global'

    # ambil data negara pengguna jika pengguna sudah login
    if request.session.get('is_authenticated'):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    negara_asal
                FROM
                    pengguna
                WHERE
                    username = %s
            """, [request.session.get('username')])
            user_country = cursor.fetchone()[0]

    if request.method == 'POST' and request.session.get('is_authenticated'):
        top_10_selection = request.POST.get('top_10_selection', 'global')

    base_query = """
        WITH tayangan_durasi AS (
            SELECT
                t.id AS id_tayangan,
                t.judul,
                CASE
                    WHEN f.id_tayangan IS NOT NULL THEN f.durasi_film
                    WHEN e.id_series IS NOT NULL THEN e.durasi
                    ELSE 0
                END AS durasi_tayangan,
                EXTRACT(EPOCH FROM (r.end_date_time - r.start_date_time)) / 60 AS durasi_nonton
            FROM
                tayangan t
            LEFT JOIN
                film f ON t.id = f.id_tayangan
            LEFT JOIN
                episode e ON t.id = e.id_series
            LEFT JOIN
                riwayat_nonton r ON t.id = r.id_tayangan
            WHERE
                r.start_date_time >= CURRENT_DATE - INTERVAL '7 days'
    """

    if top_10_selection == 'asal_negara' and request.session.get('is_authenticated'):
        where_clause = f"AND t.asal_negara = '{user_country}'"
    else:
        where_clause = ""

    final_query = base_query + where_clause + """
        ),
        view_count AS (
            SELECT
                id_tayangan,
                judul,
                COUNT(*) AS view_count
            FROM
                tayangan_durasi
            WHERE
                durasi_nonton >= 0.7 * durasi_tayangan
            GROUP BY
                id_tayangan, judul
        )
        SELECT
            id_tayangan,
            judul,
            view_count
        FROM
            view_count
        ORDER BY
            view_count DESC
        LIMIT 10;
    """

    with connection.cursor() as cursor:
        cursor.execute(final_query)
        top_10_data = cursor.fetchall()
    
    # Fetch film data from database
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                t.judul,
                t.sinopsis,
                t.url_video_trailer AS trailer_url,
                t.release_date_trailer AS release_date
            FROM
                tayangan t
            INNER JOIN
                film f ON t.id = f.id_tayangan
        """)
        film_data = cursor.fetchall()

    # Fetch series data from database
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                t.judul,
                t.sinopsis,
                t.url_video_trailer AS trailer_url,
                t.release_date_trailer AS release_date
            FROM
                tayangan t
            INNER JOIN
                series s ON t.id = s.id_tayangan
        """)
        series_data = cursor.fetchall()
                
    # Mapping data ke dictionary untuk dikirim ke template
    top_10 = [{'peringkat': i+1, 'judul': row[1], 'view_count': row[2]} for i, row in enumerate(top_10_data)]
    films = [{'judul': row[0], 'sinopsis': row[1], 'trailer_url': row[2], 'release_date': row[3]} for row in film_data]
    series = [{'judul': row[0], 'sinopsis': row[1], 'trailer_url': row[2], 'release_date': row[3]} for row in series_data]
    
    context = {
        'top_10': top_10,
        'films': films,
        'series': series,
        'top_10_selection': top_10_selection
    }
    
    return render(request, 'daftar_tayangan.html', context)


def search_trailer(request):
    search_query = request.GET.get('search', '')

    # Jika tidak ada query pencarian, kembalikan template dengan pesan bahwa tidak ada hasil
    if not search_query:
        return render(request, 'search_tayangan.html', {'error': 'Masukkan judul tayangan untuk mencari.'})

    # Pencarian dalam database untuk film dan series berdasarkan judul
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                t.id,
                t.judul,
                t.sinopsis,
                t.url_video_trailer AS trailer_url,
                t.release_date_trailer AS release_date
            FROM
                tayangan t
            WHERE
                t.judul ILIKE %s
        """, [f'%{search_query}%'])
        search_results = cursor.fetchall()

    # Menentukan tipe tayangan (film atau series) dari hasil pencarian
    results = []
    for row in search_results:
        # Ambil ID tayangan dari hasil pencarian
        tayangan_id = row[0]
        
        # Periksa apakah tayangan tersebut adalah film atau series
        with connection.cursor() as inner_cursor:
            inner_cursor.execute("""
                SELECT
                    CASE
                        WHEN f.id_tayangan IS NOT NULL THEN 'Film'
                        WHEN s.id_tayangan IS NOT NULL THEN 'Series'
                        ELSE 'Unknown'
                    END AS tipe_tayangan
                FROM
                    tayangan t
                LEFT JOIN
                    film f ON t.id = f.id_tayangan
                LEFT JOIN
                    series s ON t.id = s.id_tayangan
                WHERE
                    t.id = %s
            """, [tayangan_id])
            tipe_tayangan = inner_cursor.fetchone()[0]
        
        # Tambahkan hasil pencarian beserta tipe tayangannya ke dalam list results
        results.append({
            'judul': row[1],
            'sinopsis': row[2],
            'trailer_url': row[3],
            'release_date': row[4],
            'tipe_tayangan': tipe_tayangan
        })

    context = {
        'search_query': search_query,
        'results': results,
    }

    return render(request, 'search_tayangan.html', context)


def film_detail(request, film_id):
    # Fetch film data from the database
    with connection.cursor() as cursor:
        cursor.execute("SELECT url_video_film, release_date_film, durasi_film FROM FILM WHERE id_tayangan = %s", [str(film_id)])

        film_data = cursor.fetchone()

        # Fetch reviews for the film
        cursor.execute("SELECT rating FROM ULASAN WHERE id_tayangan = %s", [str(film_id)])
        reviews_data = cursor.fetchall()

        # Calculate total_views (jumlah entri di tabel RIWAYAT_NONTON)
        cursor.execute("SELECT COUNT(*) FROM RIWAYAT_NONTON WHERE id_tayangan = %s", [str(film_id)])
        total_views_data = cursor.fetchone()

    # Check if film data exists
    if film_data is None:
        raise Http404("Film not found")

    # Calculate total_views and average_rating
    total_views = total_views_data[0] if total_views_data else 0
    average_rating = sum(rating[0] for rating in reviews_data) / len(reviews_data) if reviews_data else 0

    # Prepare film object
    film = {
        'url_video_film': film_data[0],
        'release_date_film': film_data[1],
        'durasi_film': film_data[2],
        'total_views': total_views,
        'average_rating': average_rating,
        'reviews': [{'rating': review[0]} for review in reviews_data]
    }

    return render(request, 'film_detail.html', {'film': film})

def series_detail(request, series_id):
    # Fetch series data from the database
    with connection.cursor() as cursor:
        cursor.execute("SELECT judul, sinopsis, release_date FROM tayangan WHERE id = %s", [str(series_id)])
        series_data = cursor.fetchone()

        cursor.execute("SELECT sub_judul FROM episode WHERE id_series = %s", [str(series_id)])
        episodes_data = cursor.fetchall()

    # Check if series data exists
    if series_data is None:
        raise Http404("Series not found")

    # Prepare series object
    series = {
        'judul': series_data[0],
        'sinopsis': series_data[1],
        'release_date': series_data[2],
        'episodes': [episode[0] for episode in episodes_data]
    }

    return render(request, 'series_detail.html', {'series': series})


def episode_detail(request, episode_id):
    # Fetch episode data from the database
    with connection.cursor() as cursor:
        cursor.execute("SELECT sub_judul, sinopsis, durasi, release_date FROM episode WHERE id = %s", [str(episode_id)])
        episode_data = cursor.fetchone()

        # Fetch reviews for the episode
        cursor.execute("SELECT deskripsi, rating FROM ulasan WHERE id_episode = %s", [str(episode_id)])
        reviews_data = cursor.fetchall()

    # Check if episode data exists
    if episode_data is None:
        raise Http404("Episode not found")

    # Prepare episode object
    episode = {
        'title': episode_data[0],
        'sinopsis': episode_data[1],
        'duration': episode_data[2],
        'release_date': episode_data[3],
        'reviews': [{'content': review[0], 'rating': review[1]} for review in reviews_data]
    }

    return render(request, 'episode_detail.html', {'episode': episode})