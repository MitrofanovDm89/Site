from datetime import timedelta, date
from django.shortcuts import render, get_object_or_404
from .models import Product, Category, Availability, Booking
import json


def catalog_index(request):
    # Получаем все активные товары
    products = Product.objects.filter(is_active=True).select_related('category')
    
    # Получаем все категории для фильтра
    categories = Category.objects.all()
    
    # Фильтрация по категории (если выбрана)
    selected_category = request.GET.get('category')
    if selected_category:
        products = products.filter(category__slug=selected_category)
    
    # Поиск по названию (если указан)
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(title__icontains=search_query)
    
    # Сортировка
    sort_by = request.GET.get('sort', 'title')
    if sort_by == 'price':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    else:
        products = products.order_by('title')
    
    context = {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'search_query': search_query,
        'sort_by': sort_by,
    }
    
    return render(request, 'catalog/all_products.html', context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, is_active=True)
    return render(request, 'catalog/category_detail.html', {
        'category': category,
        'products': products
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)

    # Get related products from same category
    related_products = Product.objects.filter(
        category=product.category, 
        is_active=True
    ).exclude(id=product.id)[:4]

    # Get booked dates for the next 3 months
    today = date.today()
    end_date = today + timedelta(days=90)
    
    # Get confirmed and pending bookings
    bookings = Booking.objects.filter(
        product=product,
        start_date__gte=today,
        end_date__lte=end_date,
        status__in=['confirmed', 'pending']
    ).order_by('start_date')
    
    # Create list of booked dates for JavaScript
    booked_dates = []
    for booking in bookings:
        current_date = booking.start_date
        while current_date <= booking.end_date:
            booked_dates.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)

    return render(request, 'catalog/product_detail.html', {
        'product': product,
        'related_products': related_products,
        'booked_dates': json.dumps(booked_dates),
        'bookings': bookings,
    }) 