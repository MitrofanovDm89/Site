from datetime import timedelta, date
from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
from .models import Product, Category, Availability, Booking, Service, News


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


def news_list(request):
    """Список всех опубликованных новостей"""
    news = News.objects.filter(is_published=True).order_by('-published_at')
    
    # Получаем рекомендуемые новости отдельно
    featured_news = news.filter(featured=True)[:3]
    regular_news = news.filter(featured=False)[:6]
    
    context = {
        'featured_news': featured_news,
        'regular_news': regular_news,
        'all_news': news,
    }
    return render(request, 'catalog/news_list.html', context)


def news_detail(request, slug):
    """Детальная страница новости"""
    news = get_object_or_404(News, slug=slug, is_published=True)
    
    # Получаем похожие новости (по категории или тегу)
    related_news = News.objects.filter(
        is_published=True
    ).exclude(id=news.id).order_by('-published_at')[:3]
    
    context = {
        'news': news,
        'related_news': related_news,
    }
    return render(request, 'catalog/news_detail.html', context)


@staff_member_required
def booking_management(request):
    """Страница управления бронированиями с календарем"""
    
    # Получаем все товары для фильтрации с ценой
    products = Product.objects.filter(is_active=True).values('id', 'title', 'price')
    
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
            
            # Получаем продукт для расчета цены
            try:
                product = Product.objects.get(id=data['product_id'])
            except Product.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Продукт не найден'
                }, status=400)
            
            # Преобразуем строки дат в объекты date
            from datetime import datetime
            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
            
            # Проверяем, что end_date >= start_date
            if end_date < start_date:
                return JsonResponse({
                    'success': False,
                    'error': 'Дата окончания должна быть не раньше даты начала'
                }, status=400)
            
            # Рассчитываем количество дней и общую цену
            duration_days = (end_date - start_date).days + 1
            total_price = product.price * duration_days if product.price else 0
            
            # Создаем новое бронирование
            booking = Booking.objects.create(
                product_id=data['product_id'],
                customer_name=data['customer_name'],
                customer_email=data['customer_email'],
                customer_phone=data.get('customer_phone', ''),
                start_date=start_date,
                end_date=end_date,
                total_price=total_price,
                notes=data.get('notes', ''),
                status='pending'
            )
            
            return JsonResponse({
                'success': True,
                'booking_id': booking.id,
                'message': 'Buchung erfolgreich erstellt',
                'duration_days': duration_days,
                'total_price': float(total_price)
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
            date_changed = False
            if 'start_date' in data:
                new_start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
                if new_start_date != booking.start_date:
                    booking.start_date = new_start_date
                    date_changed = True
                    
            if 'end_date' in data:
                new_end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
                if new_end_date != booking.end_date:
                    booking.end_date = new_end_date
                    date_changed = True
            
            # Если даты изменились, пересчитываем цену
            if date_changed:
                if booking.end_date < booking.start_date:
                    return JsonResponse({
                        'success': False,
                        'error': 'Дата окончания должна быть не раньше даты начала'
                    }, status=400)
                
                # Рассчитываем новую цену
                duration_days = (booking.end_date - booking.start_date).days + 1
                booking.total_price = booking.product.price * duration_days if booking.product.price else 0
            
            if 'status' in data:
                booking.status = data['status']
            if 'notes' in data:
                booking.notes = data['notes']
            
            booking.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Buchung erfolgreich aktualisiert',
                'duration_days': booking.duration_days,
                'total_price': float(booking.total_price)
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

    # Всегда включаем два конкретных товара
    fixed_products = []
    
    # Gebläse Schalldämmung (ID 30)
    try:
        geblaese = Product.objects.get(id=30, is_active=True)
        if geblaese.id != product.id:  # Не показываем текущий товар
            fixed_products.append(geblaese)
    except Product.DoesNotExist:
        pass
    
    # Stromerzeuger (ID 35)
    try:
        stromerzeuger = Product.objects.get(id=35, is_active=True)
        if stromerzeuger.id != product.id:  # Не показываем текущий товар
            fixed_products.append(stromerzeuger)
    except Product.DoesNotExist:
        pass
    
    # Добавляем случайные товары из той же категории до общего количества 4
    remaining_slots = 4 - len(fixed_products)
    additional_products = []
    
    if remaining_slots > 0:
        # Исключаем текущий товар и уже добавленные фиксированные
        excluded_ids = [product.id] + [p.id for p in fixed_products]
        additional_products = Product.objects.filter(
            category=product.category, 
            is_active=True
        ).exclude(id__in=excluded_ids).order_by('?')[:remaining_slots]
        
        related_products = list(fixed_products) + list(additional_products)
    else:
        related_products = fixed_products[:4]  # Ограничиваем максимум 4 товарами

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
        'fixed_products': fixed_products,
        'additional_products': additional_products,
        'booked_dates': json.dumps(booked_dates),
        'bookings': bookings,
    }) 