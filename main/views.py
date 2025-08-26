from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
import json
from catalog.models import Product


def home(request):
    return render(request, 'index.html')


def cart(request):
    """Страница корзины"""
    cart_items = request.session.get('cart', {})
    products = []
    total_price = 0.0
    
    for cart_key, cart_data in cart_items.items():
        try:
            # Проверяем, является ли это новым форматом корзины с датами
            if isinstance(cart_data, dict):
                product_id = cart_data['product_id']
                quantity = cart_data['quantity']
                start_date = cart_data.get('start_date')
                end_date = cart_data.get('end_date')
                price_per_day = cart_data.get('price_per_day', 0)
            else:
                # Старый формат (только product_id и quantity)
                product_id = cart_key
                quantity = cart_data
                start_date = None
                end_date = None
                price_per_day = 0
            
            product = Product.objects.get(id=product_id, is_active=True)
            
            # Рассчитываем цену
            if start_date and end_date and price_per_day:
                # Новый формат с датами
                from datetime import datetime
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                duration_days = (end - start).days + 1
                subtotal = float(price_per_day) * duration_days * quantity
            else:
                # Старый формат без дат
                duration_days = 1
                subtotal = float(product.price) * quantity if product.price else 0.0
            
            products.append({
                'id': product.id,
                'title': product.title,
                'price': product.price,
                'quantity': quantity,
                'subtotal': subtotal,
                'start_date': start_date,
                'end_date': end_date,
                'duration_days': duration_days,
                'cart_key': cart_key
            })
            
            total_price += float(subtotal)
            
        except Product.DoesNotExist:
            continue
    
    context = {
        'cart_items': products,
        'total_price': total_price,
        'cart_count': len(products)
    }
    
    return render(request, 'main/cart.html', context)


@csrf_exempt
def add_to_cart(request):
    """Добавление товара в корзину"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            quantity = data.get('quantity', 1)
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            
            if not product_id:
                return JsonResponse({'success': False, 'error': 'Product ID is required'})
            
            # Получаем товар
            try:
                product = Product.objects.get(id=product_id, is_active=True)
            except Product.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Product not found'})
            
            # Инициализируем корзину в сессии
            if 'cart' not in request.session:
                request.session['cart'] = {}
            
            # Создаем уникальный ключ для товара с датами
            cart_key = f"{product_id}_{start_date}_{end_date}" if start_date and end_date else str(product_id)
            
            # Добавляем товар в корзину с информацией о датах
            cart = request.session['cart']
            if cart_key in cart:
                cart[cart_key]['quantity'] += quantity
            else:
                cart[cart_key] = {
                    'product_id': product_id,
                    'quantity': quantity,
                    'start_date': start_date,
                    'end_date': end_date,
                    'price_per_day': float(product.price) if product.price else 0
                }
            
            request.session.modified = True
            
            return JsonResponse({
                'success': True,
                'message': f'{product.title} добавлен в корзину',
                'cart_count': len(cart)
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})


@csrf_exempt
def remove_from_cart(request):
    """Удаление товара из корзины"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cart_key = data.get('cart_key')
            
            if not cart_key:
                return JsonResponse({'success': False, 'error': 'Cart key is required'})
            
            cart = request.session.get('cart', {})
            if cart_key in cart:
                del cart[cart_key]
                request.session.modified = True
            
            return JsonResponse({
                'success': True,
                'message': 'Товар удален из корзины',
                'cart_count': len(cart)
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})


@csrf_exempt
def update_cart_quantity(request):
    """Обновление количества товара в корзине"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cart_key = data.get('cart_key')
            quantity = data.get('quantity', 1)
            
            if not cart_key:
                return JsonResponse({'success': False, 'error': 'Cart key is required'})
            
            if quantity <= 0:
                # Если количество <= 0, удаляем товар
                return remove_from_cart(request)
            
            cart = request.session.get('cart', {})
            if cart_key in cart:
                # Проверяем, является ли это новым форматом корзины
                if isinstance(cart[cart_key], dict):
                    cart[cart_key]['quantity'] = quantity
                else:
                    # Старый формат
                    cart[cart_key] = quantity
                
                request.session.modified = True
            
            return JsonResponse({
                'success': True,
                'message': 'Количество обновлено',
                'cart_count': len(cart)
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})


@csrf_exempt
def send_inquiry(request):
    """Отправка заявки на email"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Получаем данные формы
            customer_name = data.get('customer_name', '').strip()
            customer_email = data.get('customer_email', '').strip()
            customer_phone = data.get('customer_phone', '').strip()
            comment = data.get('comment', '').strip()
            
            # Валидация
            if not customer_email and not customer_phone:
                return JsonResponse({
                    'success': False, 
                    'error': 'Необходимо указать email или телефон'
                })
            
            # Получаем товары из корзины
            cart_items = request.session.get('cart', {})
            products = []
            total_price = 0.0
            
            for cart_key, cart_data in cart_items.items():
                try:
                    # Проверяем, является ли это новым форматом корзины с датами
                    if isinstance(cart_data, dict):
                        product_id = cart_data['product_id']
                        quantity = cart_data['quantity']
                        start_date = cart_data.get('start_date')
                        end_date = cart_data.get('end_date')
                        price_per_day = cart_data.get('price_per_day', 0)
                    else:
                        # Старый формат (только product_id и quantity)
                        product_id = cart_key
                        quantity = cart_data
                        start_date = None
                        end_date = None
                        price_per_day = 0
                    
                    product = Product.objects.get(id=product_id, is_active=True)
                    
                    # Рассчитываем цену
                    if start_date and end_date and price_per_day:
                        # Новый формат с датами
                        from datetime import datetime
                        start = datetime.strptime(start_date, '%Y-%m-%d').date()
                        end = datetime.strptime(end_date, '%Y-%m-%d').date()
                        duration_days = (end - start).days + 1
                        subtotal = float(price_per_day) * duration_days * quantity
                    else:
                        # Старый формат без дат
                        subtotal = float(product.price) * quantity if product.price else 0.0
                    
                    products.append({
                        'title': product.title,
                        'price': product.price,
                        'quantity': quantity,
                        'subtotal': subtotal,
                        'start_date': start_date,
                        'end_date': end_date,
                        'duration_days': duration_days if start_date and end_date else 1
                    })
                    
                    total_price += float(subtotal)
                    
                except Product.DoesNotExist:
                    continue
            
            if not products:
                return JsonResponse({
                    'success': False, 
                    'error': 'Корзина пуста'
                })
            
            # Формируем сообщение
            message = f"""
Новая заявка с сайта Play & Jump

Клиент: {customer_name or 'Не указано'}
Email: {customer_email or 'Не указано'}
Телефон: {customer_phone or 'Не указано'}
Комментарий: {comment or 'Не указано'}

Выбранные товары:
"""
            
            for product in products:
                if product.get('start_date') and product.get('end_date'):
                    message += f"- {product['title']} x{product['quantity']} ({product['start_date']} bis {product['end_date']}, {product['duration_days']} Tage) = {product['subtotal']}€\n"
                else:
                    message += f"- {product['title']} x{product['quantity']} = {product['subtotal']}€\n"
            
            message += f"\nОбщая стоимость: {total_price}€"
            
            # Отправляем email администратору
            try:
                send_mail(
                    subject='Новая заявка с сайта Play & Jump',
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=['dlktsprdct@gmail.com'],
                    fail_silently=False,
                )
                
                # Отправляем подтверждение клиенту (если указан email)
                if customer_email:
                    confirmation_message = f"""
Здравствуйте!

Спасибо за вашу заявку на сайте Play & Jump.

Мы получили ваш запрос и свяжемся с вами в ближайшее время.

Детали заявки:
"""
                    
                    for product in products:
                        if product.get('start_date') and product.get('end_date'):
                            confirmation_message += f"- {product['title']} x{product['quantity']} ({product['start_date']} bis {product['end_date']}, {product['duration_days']} Tage) = {product['subtotal']}€\n"
                        else:
                            confirmation_message += f"- {product['title']} x{product['quantity']} = {product['subtotal']}€\n"
                    
                    confirmation_message += f"\nОбщая стоимость: {total_price}€"
                    
                    send_mail(
                        subject='Ваша заявка получена - Play & Jump',
                        message=confirmation_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[customer_email],
                        fail_silently=True,
                    )
                
                # Очищаем корзину
                request.session['cart'] = {}
                request.session.modified = True
                
                return JsonResponse({
                    'success': True,
                    'message': 'Заявка успешно отправлена! Мы свяжемся с вами в ближайшее время.'
                })
                
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': f'Ошибка при отправке email: {str(e)}'
                })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Ошибка при обработке заявки: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})


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


def cart_count(request):
    return JsonResponse({'count': 0}) 