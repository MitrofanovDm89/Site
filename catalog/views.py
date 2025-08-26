from datetime import timedelta, date
from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
from .models import Product, Category, Availability, Booking, Service


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


@staff_member_required
def booking_management(request):
    """Страница управления бронированиями с календарем"""
    
    # Получаем все товары для фильтрации
    products = Product.objects.filter(is_active=True)
    
    # Получаем все бронирования
    bookings = Booking.objects.select_related('product').all()
    
    # Получаем выбранный товар (если указан)
    selected_product = request.GET.get('product')
    if selected_product:
        bookings = bookings.filter(product_id=selected_product)
    
    # Получаем выбранный месяц (если указан)
    selected_month = request.GET.get('month')
    
    context = {
        'products': products,
        'bookings': bookings,
        'selected_product': selected_product,
        'selected_month': selected_month,
    }
    
    return render(request, 'catalog/booking_management.html', context)


@staff_member_required
@csrf_exempt
def get_bookings_data(request):
    """API для получения данных бронирований для календаря"""
    
    # Получаем параметры
    product_id = request.GET.get('product')
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    
    # Фильтруем бронирования
    bookings = Booking.objects.select_related('product')
    
    if product_id and product_id != '':
        try:
            product_id = int(product_id)
            bookings = bookings.filter(product_id=product_id)
        except ValueError:
            pass
    
    if start_date and end_date:
        try:
            from datetime import datetime
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            bookings = bookings.filter(
                start_date__gte=start_date_obj,
                end_date__lte=end_date_obj
            )
        except ValueError:
            pass
    
    # Формируем данные для календаря
    events = []
    for booking in bookings:
        # Определяем цвет в зависимости от статуса
        color_map = {
            'pending': '#ffc107',      # Желтый
            'confirmed': '#28a745',    # Зеленый
            'cancelled': '#dc3545',    # Красный
            'completed': '#6c757d',    # Серый
        }
        
        events.append({
            'id': booking.id,
            'title': f"{booking.customer_name} - {booking.product.title}",
            'start': booking.start_date.isoformat(),
            'end': (booking.end_date + timedelta(days=1)).isoformat(),  # +1 день для корректного отображения
            'backgroundColor': color_map.get(booking.status, '#007bff'),
            'borderColor': color_map.get(booking.status, '#007bff'),
            'extendedProps': {
                'customer_name': booking.customer_name,
                'customer_email': booking.customer_email,
                'customer_phone': booking.customer_phone,
                'product_id': booking.product.id,
                'product_title': booking.product.title,
                'total_price': str(booking.total_price),
                'status': booking.status,
                'notes': booking.notes,
                'duration_days': booking.duration_days,
            }
        })
    
    return JsonResponse(events, safe=False)


@staff_member_required
@csrf_exempt
def create_booking(request):
    """API для создания нового бронирования"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Преобразуем строки дат в объекты date
            from datetime import datetime
            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
            
            # Создаем новое бронирование
            booking = Booking.objects.create(
                product_id=data['product_id'],
                customer_name=data['customer_name'],
                customer_email=data['customer_email'],
                customer_phone=data.get('customer_phone', ''),
                start_date=start_date,
                end_date=end_date,
                total_price=data['total_price'],
                notes=data.get('notes', ''),
                status='pending'
            )
            
            return JsonResponse({
                'success': True,
                'booking_id': booking.id,
                'message': 'Buchung erfolgreich erstellt'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@staff_member_required
@csrf_exempt
def update_booking(request, booking_id):
    """API для обновления бронирования"""
    try:
        booking = get_object_or_404(Booking, id=booking_id)
        
        if request.method == 'PUT':
            data = json.loads(request.body)
            
            # Преобразуем строки дат в объекты date
            from datetime import datetime
            if 'start_date' in data:
                booking.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            if 'end_date' in data:
                booking.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
            if 'status' in data:
                booking.status = data['status']
            if 'notes' in data:
                booking.notes = data['notes']
            
            booking.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Buchung erfolgreich aktualisiert'
            })
            
        elif request.method == 'DELETE':
            booking.delete()
            return JsonResponse({
                'success': True,
                'message': 'Buchung erfolgreich gelöscht'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


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