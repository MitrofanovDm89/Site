from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.catalog_index, name='catalog_index'),
    path('<slug:slug>/', views.category_detail, name='category_detail'),
    path('produkt/<slug:slug>/', views.product_detail, name='product_detail'),
] 