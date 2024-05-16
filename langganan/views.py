from django.shortcuts import render, redirect
from django.db import connection
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.http import HttpResponseBadRequest

# @login_required
def langganan(request):
    # Mendapatkan username dari pengguna yang sedang login
    username = request.COOKIES.get('username')

    # Mendapatkan informasi paket aktif
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.nama, p.harga, p.resolusi_layar, t.start_date_time, t.end_date_time, t.metode_pembayaran, t.timestamp_pembayaran
            FROM transaction t
            JOIN paket p ON t.nama_paket = p.nama
            WHERE t.username = %s AND t.end_date_time > CURRENT_DATE
            ORDER BY t.start_date_time DESC
            LIMIT 1
        """, [username])
        current_subscription = cursor.fetchone()

    # Mendapatkan daftar paket yang tersedia
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT nama, harga, resolusi_layar
            FROM paket
        """)
        packages = cursor.fetchall()

    context = {
        'current_subscription': current_subscription,
        'packages': packages,
    }

    return render(request, 'kelola_langganan.html', context)

# @login_required
def bayar(request):
    if request.method == "POST":
        username = request.COOKIES.get('username')
        package_name = request.POST.get('package_name')
        metode_pembayaran = request.POST.get('metode_pembayaran')
        
        # Validasi input
        if not package_name or not metode_pembayaran:
            return HttpResponseBadRequest("Nama paket dan metode pembayaran diperlukan.")

        # Menentukan tanggal mulai dan akhir untuk langganan baru
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=30)

        # Memasukkan transaksi baru atau memperbarui transaksi yang ada
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO transaction (username, start_date_time, end_date_time, nama_paket, metode_pembayaran, timestamp_pembayaran)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (username, start_date_time) DO UPDATE
                SET end_date_time = %s, nama_paket = %s, metode_pembayaran = %s, timestamp_pembayaran = %s
            """, [username, start_date, end_date, package_name, metode_pembayaran, datetime.now(), end_date, package_name, metode_pembayaran, datetime.now()])

        return redirect('langganan:langganan')
    else:
        package_name = request.GET.get('package', '')

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT nama, harga, resolusi_layar
                FROM paket
                WHERE nama = %s
            """, [package_name])
            package = cursor.fetchone()

        context = {
            'package': package,
        }

        return render(request, 'bayar.html', context)
