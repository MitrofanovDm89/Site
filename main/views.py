from django.shortcuts import render
from django.http import JsonResponse


def home(request):
    return render(request, 'index.html')


def kontakt(request):
    return render(request, 'main/kontakt.html')


def agb(request):
    return render(request, 'main/agb.html')


def impressum(request):
    return render(request, 'main/impressum.html')


def datenschutz(request):
    return render(request, 'main/datenschutz.html')


def vermietung(request):
    return render(request, 'main/vermietung.html')


def neuigkeiten(request):
    return render(request, 'main/neuigkeiten.html')


def cart(request):
    return render(request, 'main/cart.html')


def cart_count(request):
    return JsonResponse({'count': 0}) 