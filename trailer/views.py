from django.http import Http404
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
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
                t.sinopsis AS sinopsis_trailer,
                t.url_video_trailer AS trailer_url,
                t.release_date_trailer,
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
                sinopsis_trailer,
                trailer_url,
                release_date_trailer,
                COUNT(*) AS view_count
            FROM
                tayangan_durasi
            WHERE
                durasi_nonton >= 0.7 * durasi_tayangan
            GROUP BY
                id_tayangan, judul, sinopsis_trailer, trailer_url, release_date_trailer
        )
        SELECT
            id_tayangan,
            judul,
            sinopsis_trailer,
            trailer_url,
            release_date_trailer,
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
                t.id,
                t.judul,
                t.sinopsis,
                t.asal_negara,
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
                t.id,
                t.judul,
                t.sinopsis,
                t.asal_negara,
                t.url_video_trailer AS trailer_url,
                t.release_date_trailer AS release_date
            FROM
                tayangan t
            INNER JOIN
                series s ON t.id = s.id_tayangan
        """)
        series_data = cursor.fetchall()
                
    # Mapping data ke dictionary untuk dikirim ke template
    top_10 = [{'peringkat': i+1, 'judul': row[1], 'sinopsis': row[2], 'trailer_url': row[3],
               'release_date': row[4], 'view_count': row[5]} for i, row in enumerate(top_10_data)]
    films = [{'id': row[0], 'judul': row[1], 'sinopsis': row[2], 'asal_negara':row[3], 'trailer_url': row[4], 'release_date': row[5]} for row in film_data]
    series = [{'id': row[0], 'judul': row[1], 'sinopsis': row[2], 'asal_negara':row[3], 'trailer_url': row[4], 'release_date': row[5]} for row in series_data]
    
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

@csrf_exempt
def film_detail(request, film_id):
    # Ambil data film dari database dengan menggabungkan tabel Tayangan dan Film
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                t.judul,
                t.sinopsis,
                f.durasi_film,
                t.url_video_trailer,
                t.release_date_trailer,
                t.asal_negara,
                COUNT(r.id_tayangan) AS total_views,
                COALESCE(AVG(u.rating), 0) AS average_rating
            FROM
                tayangan t
            LEFT JOIN
                film f ON t.id = f.id_tayangan
            LEFT JOIN
                riwayat_nonton r ON t.id = r.id_tayangan
            LEFT JOIN
                ulasan u ON t.id = u.id_tayangan
            WHERE
                t.id = %s
            GROUP BY
                t.id, f.id_tayangan;
        """, [film_id])
        film_data = cursor.fetchone()

        # Fetch reviews for the film
        cursor.execute("SELECT rating FROM ULASAN WHERE id_tayangan = %s", [film_id])
        reviews_data = cursor.fetchall()

        # Fetch genre data for the film
        cursor.execute("""
            SELECT genre FROM genre_tayangan WHERE id_tayangan = %s
        """, [film_id])
        genre_data = cursor.fetchall()

        # Fetch cast data for the film
        cursor.execute("""
            SELECT c.nama
            FROM contributors c
            INNER JOIN memainkan_tayangan mt ON c.id = mt.id_pemain
            WHERE mt.id_tayangan = %s
        """, [film_id])
        cast_data = cursor.fetchall()

        # Fetch writer data for the film
        cursor.execute("""
            SELECT c.nama
            FROM contributors c
            INNER JOIN menulis_skenario_tayangan ms ON c.id = ms.id_penulis_skenario
            WHERE ms.id_tayangan = %s
        """, [film_id])
        writer_data = cursor.fetchall()

        # Fetch director data for the film
        cursor.execute("""
            SELECT c.nama
            FROM contributors c
            INNER JOIN tayangan t ON c.id = t.id_sutradara
            WHERE t.id = %s
        """, [film_id])
        director_data = cursor.fetchall()

        # Calculate total_views (jumlah entri di tabel RIWAYAT_NONTON)
        cursor.execute("SELECT COUNT(*) FROM RIWAYAT_NONTON WHERE id_tayangan = %s", [film_id])
        total_views_data = cursor.fetchone()

    # Calculate total_views and average_rating
    total_views = total_views_data[0] if total_views_data else 0
    average_rating = sum(rating[0] for rating in reviews_data) / len(reviews_data) if reviews_data else 0

    # Ambil ulasan-ulasan dari database
    if request.method == 'POST':
        id_tayangan = request.POST.get('id_tayangan')
        username = request.POST.get('username')
        rating = request.POST.get('rating')
        deskripsi = request.POST.get('deskripsi')
        
        with connection.cursor() as cursor:
            try:
                cursor.execute("""
                    INSERT INTO ulasan (id_tayangan, username, rating, deskripsi)
                    VALUES (%s, %s, %s, %s)
                """, [id_tayangan, username, rating, deskripsi])
                # Jika berhasil, komit perubahan ke database
                cursor.connection.commit()
                messages.success(request, 'Ulasan berhasil ditambahkan.')
                return redirect('film_detail', film_id=film_id)
            except Exception as e:
                # Jika terjadi kesalahan, rollback perubahan dan tampilkan pesan error
                cursor.connection.rollback()
                messages.error(request, f'Gagal menambahkan ulasan: {e}')

    # Siapkan data film dalam bentuk dictionary
    film = {
        'judul': film_data[0],
        'sinopsis': film_data[1],
        'durasi_film': film_data[2],
        'url_video_trailer': film_data[3],
        'release_date': film_data[4],
        'asal_negara': film_data[5],
        'total_views': total_views,
        'average_rating': average_rating,
        'genre': [genre[0] for genre in genre_data],
        'pemain': [cast[0] for cast in cast_data],
        'penulis_skenario': [writer[0] for writer in writer_data],
        'sutradara': [director[0] for director in director_data],
        'reviews': [{'rating': review[0]} for review in reviews_data],
    }

    # Render template dengan data film dan form ulasan
    return render(request, 'film_detail.html', {'film': film})

@csrf_exempt
def series_detail(request, series_id):
    # Fetch series data from the database
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                t.judul,
                t.sinopsis,
                t.asal_negara,
                COUNT(r.id_tayangan) AS total_views,
                COALESCE(AVG(u.rating), 0) AS average_rating
            FROM
                tayangan t
            LEFT JOIN
                series s ON t.id = s.id_tayangan
            LEFT JOIN
                riwayat_nonton r ON t.id = r.id_tayangan
            LEFT JOIN
                ulasan u ON t.id = u.id_tayangan
            WHERE
                t.id = %s
            GROUP BY
                t.id, s.id_tayangan;
        """, [series_id])
        series_data = cursor.fetchone()

        cursor.execute("SELECT sub_judul FROM episode WHERE id_series = %s", [str(series_id)])
        episodes_data = cursor.fetchall()

        # Fetch reviews for the series
        cursor.execute("SELECT rating FROM ULASAN WHERE id_tayangan = %s", [str(series_id)])
        reviews_data = cursor.fetchall()

        # Fetch genre data for the series
        cursor.execute("""
            SELECT genre FROM genre_tayangan WHERE id_tayangan = %s
        """, [series_id])
        genre_data = cursor.fetchall()

        # Fetch cast data for the series
        cursor.execute("""
            SELECT c.nama
            FROM contributors c
            INNER JOIN memainkan_tayangan mt ON c.id = mt.id_pemain
            WHERE mt.id_tayangan = %s
        """, [series_id])
        cast_data = cursor.fetchall()

        # Fetch writer data for the series
        cursor.execute("""
            SELECT c.nama
            FROM contributors c
            INNER JOIN menulis_skenario_tayangan ms ON c.id = ms.id_penulis_skenario
            WHERE ms.id_tayangan = %s
        """, [series_id])
        writer_data = cursor.fetchall()

        # Fetch director data for the series
        cursor.execute("""
            SELECT c.nama
            FROM contributors c
            INNER JOIN tayangan t ON c.id = t.id_sutradara
            WHERE t.id = %s
        """, [series_id])
        director_data = cursor.fetchall()

        # Calculate total_views (jumlah entri di tabel RIWAYAT_NONTON)
        cursor.execute("SELECT COUNT(*) FROM RIWAYAT_NONTON WHERE id_tayangan = %s", [str(series_id)])
        total_views_data = cursor.fetchone()


    # Calculate total_views and average_rating
    total_views = total_views_data[0] if total_views_data else 0
    average_rating = sum(rating[0] for rating in reviews_data) / len(reviews_data) if reviews_data else 0

    # Ambil ulasan-ulasan dari database
    if request.method == 'POST':
        id_tayangan = request.POST.get('id_tayangan')
        username = request.POST.get('username')
        rating = request.POST.get('rating')
        deskripsi = request.POST.get('deskripsi')
        
        with connection.cursor() as cursor:
            try:
                cursor.execute("""
                    INSERT INTO ulasan (id_tayangan, username, rating, deskripsi)
                    VALUES (%s, %s, %s, %s)
                """, [id_tayangan, username, rating, deskripsi])
                # Jika berhasil, komit perubahan ke database
                cursor.connection.commit()
                messages.success(request, 'Ulasan berhasil ditambahkan.')
                return redirect('film_detail', series_id=series_id)
            except Exception as e:
                # Jika terjadi kesalahan, rollback perubahan dan tampilkan pesan error
                cursor.connection.rollback()
                messages.error(request, f'Gagal menambahkan ulasan: {e}')

    # Siapkan data series dalam bentuk dictionary
    series = {
        'judul': series_data[0],
        'sinopsis': series_data[1],
        'asal_negara': series_data[2],
        'total_views': total_views,
        'average_rating': average_rating,
        'genre': [genre[0] for genre in genre_data],
        'pemain': [cast[0] for cast in cast_data],
        'penulis_skenario': [writer[0] for writer in writer_data],
        'sutradara': [director[0] for director in director_data],
        'episodes': [{'id': index, 'title': episode[0]} for index, episode in enumerate(episodes_data, start=1)],
    }

    # Render template dengan data series dan form ulasan
    return render(request, 'series_detail.html', {'series': series})

def episode_detail(request, episode_id):
    # Mengambil data episode dari database
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT e.sub_judul, e.sinopsis, e.durasi, e.release_date, s.judul AS series_judul
            FROM episode e
            INNER JOIN series s ON e.id_series = s.id
            WHERE e.id = %s
        """, [str(episode_id)])
        episode_data = cursor.fetchone()

    # Check if episode data exists
    if episode_data is None:
        raise Http404("Episode not found")

    # Prepare episode object
    episode = {
        'title': episode_data[0],
        'sinopsis': episode_data[1],
        'duration': episode_data[2],
        'release_date': episode_data[3],
        'series_title': episode_data[4],
    }

    # Mengambil daftar episode lainnya
    cursor.execute("""
        SELECT e.id, e.sub_judul
        FROM episode e
        INNER JOIN series s ON e.id_series = s.id
        WHERE e.id != %s AND s.id = (SELECT id_series FROM episode WHERE id = %s)
    """, [episode_id, episode_id])
    other_episodes_data = cursor.fetchall()

    other_episodes = [{'id': data[0], 'title': data[1]} for data in other_episodes_data]

    return render(request, 'episode_detail.html', {'episode': episode, 'other_episodes': other_episodes})

