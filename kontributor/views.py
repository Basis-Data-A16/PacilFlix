from django.shortcuts import render
from django.core.paginator import Paginator
from django.db import connection

def kontributor_list(request):
    search_query = request.GET.get('search', '')

    base_query = """
        SELECT nama, jenis_kelamin, kewarganegaraan, 
               STRING_AGG(tipe, ', ') AS tipe
        FROM (
            SELECT nama, jenis_kelamin, kewarganegaraan, 'Pemain' AS tipe
            FROM contributors
            JOIN pemain ON contributors.id = pemain.id
            UNION ALL
            SELECT nama, jenis_kelamin, kewarganegaraan, 'Penulis Skenario' AS tipe
            FROM contributors
            JOIN penulis_skenario ON contributors.id = penulis_skenario.id
            UNION ALL
            SELECT nama, jenis_kelamin, kewarganegaraan, 'Sutradara' AS tipe
            FROM contributors
            JOIN sutradara ON contributors.id = sutradara.id
        ) AS subquery
    """

    if search_query:
        query = f"{base_query} WHERE tipe ILIKE %s GROUP BY nama, jenis_kelamin, kewarganegaraan"
        params = [f'%{search_query}%']
    else:
        query = f"{base_query} GROUP BY nama, jenis_kelamin, kewarganegaraan"
        params = []

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        contributors = cursor.fetchall()

    contributors_list = [
        {
            'nama': row[0],
            'jenis_kelamin': 'Laki-laki' if row[1] == 0 else 'Perempuan',
            'kewarganegaraan': row[2],
            'tipe': row[3]
        } for row in contributors
    ]

    paginator = Paginator(contributors_list, 10)  # Show 10 contributors per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query
    }

    return render(request, 'kontributor.html', context)
