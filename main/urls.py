from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.home, name='home'),
    path('kontakt/', views.kontakt, name='kontakt'),
    path('agb/', views.agb, name='agb'),
    path('impressum/', views.impressum, name='impressum'),
    path('datenschutz/', views.datenschutz, name='datenschutz'),
    path('vermietung/', views.vermietung, name='vermietung'),
    path('neuigkeiten/', views.neuigkeiten, name='neuigkeiten'),
    path('cart/', views.cart, name='cart'),
    path('cart/count/', views.cart_count, name='cart_count'),
] 