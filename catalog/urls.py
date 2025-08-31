from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    # Новости (должны идти ПЕРЕД общими slug паттернами)
    path('neuigkeiten/', views.news_list, name='news_list'),
    path('neuigkeiten/<slug:slug>/', views.news_detail, name='news_detail'),
    
    # Управление бронированиями (только для администраторов)
    path('admin/bookings/', views.booking_management, name='booking_management'),
    path('admin/bookings/data/', views.get_bookings_data, name='get_bookings_data'),
    path('admin/bookings/create/', views.create_booking, name='create_booking'),
    path('admin/bookings/<int:booking_id>/', views.update_booking, name='update_booking'),
    
    # Общие паттерны (должны идти ПОСЛЕ специфичных)
    path('', views.catalog_index, name='catalog_index'),
    path('<slug:slug>/', views.category_detail, name='category_detail'),
    path('produkt/<slug:slug>/', views.product_detail, name='product_detail'),
] 