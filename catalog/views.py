from datetime import timedelta, date
from django.shortcuts import render, get_object_or_404
from .models import Product, Category, Availability, Booking
import json


def catalog_index(request):
    categories = Category.objects.all()
    return render(request, 'catalog/index.html', {'categories': categories})


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