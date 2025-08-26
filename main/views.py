from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
import json
from catalog.models import Product


def home(request):
    return render(request, 'main/home.html')


def cart(request):
    """Страница корзины"""
    cart_items = request.session.get('cart', {})
    products = []
    total_price = 0
    
    for product_id, quantity in cart_items.items():
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            products.append({
                'id': product.id,
                'title': product.title,
                'price': product.price,
                'quantity': quantity,
                'subtotal': product.price * quantity if product.price else 0
            })
            if product.price:
                total_price += product.price * quantity
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
            
            # Добавляем товар в корзину
            cart = request.session['cart']
            if str(product_id) in cart:
                cart[str(product_id)] += quantity
            else:
                cart[str(product_id)] = quantity
            
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
            product_id = data.get('product_id')
            
            if not product_id:
                return JsonResponse({'success': False, 'error': 'Product ID is required'})
            
            cart = request.session.get('cart', {})
            if str(product_id) in cart:
                del cart[str(product_id)]
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
            product_id = data.get('product_id')
            quantity = data.get('quantity', 1)
            
            if not product_id:
                return JsonResponse({'success': False, 'error': 'Product ID is required'})
            
            if quantity <= 0:
                # Если количество <= 0, удаляем товар
                return remove_from_cart(request)
            
            cart = request.session.get('cart', {})
            if str(product_id) in cart:
                cart[str(product_id)] = quantity
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
            total_price = 0
            
            for product_id, quantity in cart_items.items():
                try:
                    product = Product.objects.get(id=product_id, is_active=True)
                    subtotal = product.price * quantity if product.price else 0
                    products.append({
                        'title': product.title,
                        'price': product.price,
                        'quantity': quantity,
                        'subtotal': subtotal
                    })
                    if product.price:
                        total_price += subtotal
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