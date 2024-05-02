from django.shortcuts import render

# Create your views here.

def kontributor(request):
    return render(request, 'kontributor.html')