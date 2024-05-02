from django.shortcuts import render

# Create your views here.
def langganan(request):
    return render(request, 'kelola_langganan.html')

def bayar(request):
    return render(request, 'bayar.html')