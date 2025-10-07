from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.utils.encoding import force_str
import json
import logging
from catalog.models import Product
from datetime import datetime, date

logger = logging.getLogger(__name__)


def home(request):
    return render(request, 'index.html')


def cart(request):
    """Страница корзины для аренды по дням"""
    cart_items = request.session.get('cart', {})
    # По умолчанию всегда Selbstabholung, если не выбран другой способ
    delivery_option = request.session.get('delivery_option', 'pickup')
    
    # Если в сессии нет выбранного способа доставки, устанавливаем pickup по умолчанию
    if 'delivery_option' not in request.session:
        request.session['delivery_option'] = 'pickup'
        delivery_option = 'pickup'
    products = []
    total_price = 0.0
    
    for cart_key, cart_data in cart_items.items():
        try:
            logger.debug(f"Processing cart_key = {cart_key}, cart_data = {cart_data}")
            
            # Проверяем, является ли это новым форматом корзины с датами
            if isinstance(cart_data, dict):
                product_id = cart_data['product_id']
                start_date = cart_data.get('start_date')
                end_date = cart_data.get('end_date')
                price_per_day = cart_data.get('price_per_day', 0)
                logger.debug(f"New format - product_id = {product_id}, start_date = {start_date}, end_date = {end_date}, price_per_day = {price_per_day}")
            else:
                # Старый формат (только product_id и quantity) - конвертируем
                product_id = cart_key
                start_date = None
                end_date = None
                price_per_day = 0
                logger.debug(f"Old format - product_id = {product_id}")
            
            logger.debug(f"Trying to get product with id = {product_id}")
            product = Product.objects.get(id=product_id, is_active=True)
            logger.debug(f"Product found: {product.title}")
            
            # Рассчитываем цену и количество дней
            if start_date and end_date:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                duration_days = (end - start).days + 1
                # Для товаров с Price auf Anfrage используем 0 как цену
                if price_per_day and price_per_day > 0:
                    subtotal = float(price_per_day) * duration_days
                else:
                    subtotal = 0.0  # Price auf Anfrage
            else:
                # Если нет дат, устанавливаем сегодня + 1 день
                today = date.today()
                start_date = today.strftime('%Y-%m-%d')
                end_date = (today.replace(day=today.day + 1)).strftime('%Y-%m-%d')
                duration_days = 1
                # Для товаров с Price auf Anfrage используем 0 как цену
                if product.price and product.price > 0:
                    subtotal = float(product.price)
                    price_per_day = float(product.price)
                else:
                    subtotal = 0.0  # Price auf Anfrage
                    price_per_day = 0.0
                
                # Обновляем корзину с датами
                if cart_key in cart_items:
                    cart_items[cart_key] = {
                        'product_id': product_id,
                        'start_date': start_date,
                        'end_date': end_date,
                        'price_per_day': price_per_day
                    }
            
            products.append({
                'id': product.id,
                'title': product.title,
                'price': product.price,
                'subtotal': subtotal,
                'start_date': start_date,
                'end_date': end_date,
                'duration_days': duration_days,
                'cart_key': cart_key,
                'price_per_day': price_per_day,
                'image': product.image
            })
            
            total_price += float(subtotal)
            
        except Product.DoesNotExist:
            logger.debug(f"Product with id {product_id} does not exist or is not active")
            continue
        except Exception as e:
            logger.debug(f"Error processing cart item: {e}")
            continue
    
    # Очищаем корзину от несуществующих товаров
    invalid_keys = []
    for cart_key, cart_data in cart_items.items():
        if isinstance(cart_data, dict) and 'product_id' in cart_data:
            try:
                Product.objects.get(id=cart_data['product_id'], is_active=True)
            except Product.DoesNotExist:
                invalid_keys.append(cart_key)
        elif isinstance(cart_data, str):
            try:
                Product.objects.get(id=cart_key, is_active=True)
            except Product.DoesNotExist:
                invalid_keys.append(cart_key)
    
    # Удаляем несуществующие товары
    for key in invalid_keys:
        del cart_items[key]
        logger.debug(f"Removed invalid item with key: {key}")
    
    # Сохраняем обновленную корзину
    if cart_items:
        request.session['cart'] = cart_items
        request.session.modified = True
    
    # Рассчитываем стоимость доставки
    delivery_cost = 70.0 if delivery_option == 'delivery' else 0.0
    final_total = total_price + delivery_cost
    
    # Получаем данные доставки из сессии
    delivery_address = request.session.get('delivery_address', '')
    delivery_datetime = request.session.get('delivery_datetime', '')
    return_datetime = request.session.get('return_datetime', '')
    delivery_instructions = request.session.get('delivery_instructions', '')
    
    # Преобразуем строки дат в объекты datetime для правильного отображения
    try:
        if delivery_datetime:
            delivery_dt = datetime.strptime(delivery_datetime, '%Y-%m-%dT%H:%M')
            delivery_datetime = delivery_dt
        if return_datetime:
            return_dt = datetime.strptime(return_datetime, '%Y-%m-%dT%H:%M')
            return_datetime = return_dt
    except ValueError:
        # Если формат даты неправильный, оставляем как есть
        pass
    
    # Отладочная информация
    logger.debug(f"cart_items = {cart_items}")
    logger.debug(f"products = {products}")
    logger.debug(f"len(products) = {len(products)}")
    logger.debug(f"delivery_address = {delivery_address}")
    logger.debug(f"delivery_datetime = {delivery_datetime}")
    logger.debug(f"return_datetime = {return_datetime}")
    logger.debug(f"delivery_instructions = {delivery_instructions}")
    
    context = {
        'cart_items': products,
        'total_price': total_price,
        'delivery_option': delivery_option,
        'delivery_cost': delivery_cost,
        'final_total': final_total,
        'cart_count': len(products),
        'delivery_address': delivery_address,
        'delivery_datetime': delivery_datetime,
        'return_datetime': return_datetime,
        'delivery_instructions': delivery_instructions
    }
    
    return render(request, 'main/cart.html', context)


def add_to_cart(request):
    """Добавление товара в корзину для аренды"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            
            if not product_id:
                return JsonResponse({'success': False, 'error': 'Product ID is required'})
                
            if not start_date or not end_date:
                return JsonResponse({'success': False, 'error': 'Start and end dates are required'})
            
            # Получаем товар
            try:
                product = Product.objects.get(id=product_id, is_active=True)
            except Product.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Product not found'})
            
            # Проверяем даты
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            if end < start:
                return JsonResponse({'success': False, 'error': 'End date must be after start date'})
                
            # Инициализируем корзину в сессии
            if 'cart' not in request.session:
                request.session['cart'] = {}
            
            # Устанавливаем pickup по умолчанию при первом добавлении товара
            if 'delivery_option' not in request.session:
                request.session['delivery_option'] = 'pickup'
            
            # Создаем уникальный ключ для товара с датами
            cart_key = f"{product_id}_{start_date}_{end_date}"
            
            # Добавляем товар в корзину
            cart = request.session['cart']
            cart[cart_key] = {
                'product_id': product_id,
                'start_date': start_date,
                'end_date': end_date,
                'price_per_day': float(product.price) if product.price else 0
            }
                
            request.session.modified = True
            
            return JsonResponse({
                'success': True,
                'message': f'{product.title} wurde in den Warenkorb gelegt',
                'cart_count': len(cart)
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})


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
                
                # Если корзина пуста, сбрасываем способ доставки на pickup
                # Детали доставки очищаем только при полной очистке корзины
                if not cart:
                    request.session['delivery_option'] = 'pickup'
                    # Очищаем детали доставки только если корзина полностью пуста
                    if 'delivery_address' in request.session:
                        del request.session['delivery_address']
                    if 'delivery_datetime' in request.session:
                        del request.session['delivery_datetime']
                    if 'return_datetime' in request.session:
                        del request.session['return_datetime']
                    if 'delivery_instructions' in request.session:
                        del request.session['delivery_instructions']
                request.session.modified = True
                
                return JsonResponse({
                    'success': True,
                    'message': 'Товар удален из корзины',
                    'cart_count': len(cart)
                })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})


def update_cart_dates(request):
    """Обновление дат товара в корзине"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cart_key = data.get('cart_key')
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            
            if not cart_key or not start_date or not end_date:
                return JsonResponse({'success': False, 'error': 'Cart key and dates are required'})
            
            # Проверяем даты
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            if end < start:
                return JsonResponse({'success': False, 'error': 'End date must be after start date'})
                
            cart = request.session.get('cart', {})
            if cart_key in cart:
                # Обновляем даты
                cart[cart_key]['start_date'] = start_date
                cart[cart_key]['end_date'] = end_date
                request.session.modified = True
                        
                # Пересчитываем цену
                duration_days = (end - start).days + 1
                price_per_day = cart[cart_key]['price_per_day']
                new_subtotal = price_per_day * duration_days
            
                return JsonResponse({
                    'success': True,
                    'message': 'Даты обновлены',
                    'new_subtotal': new_subtotal,
                    'duration_days': duration_days
                })
            else:
                return JsonResponse({'success': False, 'error': 'Cart item not found'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})


def update_delivery_option(request):
    """Обновление способа доставки"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            delivery_option = data.get('delivery_option')
            
            if delivery_option not in ['pickup', 'delivery']:
                return JsonResponse({'success': False, 'error': 'Invalid delivery option'})
            
            # Сохраняем выбор в сессии
            request.session['delivery_option'] = delivery_option
            request.session.modified = True
            
            # Если выбран pickup, НЕ очищаем данные доставки
            # Пользователь может сохранить детали и использовать их позже
            # Детали будут очищены только при очистке корзины или отправке заявки
            
            # Рассчитываем новую стоимость
            cart_items = request.session.get('cart', {})
            total_price = 0.0
            
            for cart_key, cart_data in cart_items.items():
                if isinstance(cart_data, dict):
                    start_date = cart_data.get('start_date')
                    end_date = cart_data.get('end_date')
                    price_per_day = cart_data.get('price_per_day', 0)
                    
                    if start_date and end_date and price_per_day:
                        start = datetime.strptime(start_date, '%Y-%m-%d').date()
                        end = datetime.strptime(end_date, '%Y-%m-%d').date()
                        duration_days = (end - start).days + 1
                        subtotal = float(price_per_day) * duration_days
                        total_price += subtotal
            
            delivery_cost = 70.0 if delivery_option == 'delivery' else 0.0
            final_total = total_price + delivery_cost
            
            return JsonResponse({
                'success': True,
                'message': 'Способ доставки обновлен',
                'delivery_cost': delivery_cost,
                'final_total': final_total
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})


def update_delivery_details(request):
    """Обновление деталей доставки (адрес, даты, время)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
                
            # Проверяем, что выбран способ доставки
            if request.session.get('delivery_option') != 'delivery':
                return JsonResponse({'success': False, 'error': 'Lieferung muss ausgewählt werden'})
            
            # Получаем данные доставки
            delivery_address = data.get('delivery_address', '').strip()
            delivery_datetime = data.get('delivery_datetime', '').strip()
            return_datetime = data.get('return_datetime', '').strip()
            delivery_instructions = data.get('delivery_instructions', '').strip()
            
            # Валидация обязательных полей
            if not delivery_address:
                return JsonResponse({'success': False, 'error': 'Lieferadresse ist erforderlich'})
            if not delivery_datetime:
                return JsonResponse({'success': False, 'error': 'Lieferdatum und -zeit sind erforderlich'})
            if not return_datetime:
                return JsonResponse({'success': False, 'error': 'Rückgabedatum und -zeit sind erforderlich'})
            
            # Проверяем, что время возврата после времени доставки
            try:
                delivery_dt = datetime.strptime(delivery_datetime, '%Y-%m-%dT%H:%M')
                return_dt = datetime.strptime(return_datetime, '%Y-%m-%dT%H:%M')
                
                if return_dt <= delivery_dt:
                    return JsonResponse({'success': False, 'error': 'Rückgabezeit muss nach der Lieferzeit liegen'})
                    
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Ungültiges Datums- oder Zeitformat'})
            
            # Сохраняем в сессии
            request.session['delivery_address'] = delivery_address
            request.session['delivery_datetime'] = delivery_datetime
            request.session['return_datetime'] = return_datetime
            request.session['delivery_instructions'] = delivery_instructions
            request.session.modified = True
            
            return JsonResponse({
                'success': True,
                'message': 'Lieferdetails erfolgreich gespeichert'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})


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
            privacy_consent = data.get('privacy_consent', False)
            
            # Валидация
            if not customer_email and not customer_phone:
                return JsonResponse({
                    'success': False, 
                    'error': 'Необходимо указать email или телефон'
                })
            
            # Проверка согласия на обработку персональных данных
            if not privacy_consent:
                return JsonResponse({
                    'success': False, 
                    'error': 'Bitte stimmen Sie der Verarbeitung Ihrer personenbezogenen Daten zu.'
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
                        start_date = cart_data.get('start_date')
                        end_date = cart_data.get('end_date')
                        price_per_day = cart_data.get('price_per_day', 0)
                    else:
                        # Старый формат (только product_id и quantity)
                        product_id = cart_key
                        start_date = None
                        end_date = None
                        price_per_day = 0
                    
                    product = Product.objects.get(id=product_id, is_active=True)
                    
                    # Рассчитываем цену
                    if start_date and end_date and price_per_day:
                        # Новый формат с датами
                        start = datetime.strptime(start_date, '%Y-%m-%d').date()
                        end = datetime.strptime(end_date, '%Y-%m-%d').date()
                        duration_days = (end - start).days + 1
                        subtotal = float(price_per_day) * duration_days
                    else:
                        # Старый формат без дат
                        subtotal = float(product.price) if product.price else 0.0
                    
                    products.append({
                        'title': product.title,
                        'price': product.price,
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
            
            # Формируем сообщение с безопасным кодированием
            def safe_encode(text):
                if text:
                    try:
                        return text.encode('utf-8').decode('utf-8')
                    except:
                        return str(text)
                return 'Nicht angegeben'
            
            customer_name_safe = safe_encode(customer_name)
            customer_email_safe = safe_encode(customer_email)
            customer_phone_safe = safe_encode(customer_phone)
            comment_safe = safe_encode(comment)
            
            message = f"""
Neue Anfrage von der Play & Jump Website

Kunde: {customer_name_safe}
Email: {customer_email_safe}
Telefon: {customer_phone_safe}
Kommentar: {comment_safe}

Lieferoption: {'Lieferung + Aufbau/Abbau' if request.session.get('delivery_option') == 'delivery' else 'Selbstabholung'}

Ausgewählte Produkte:
"""
            
            for product in products:
                if product.get('start_date') and product.get('end_date'):
                    message += f"- {product['title']} ({product['start_date']} bis {product['end_date']}, {product['duration_days']} Tage) = {product['subtotal']}€\n"
                else:
                    message += f"- {product['title']} = {product['subtotal']}€\n"
            
            # Добавляем информацию о доставке
            delivery_option = request.session.get('delivery_option', 'pickup')
            delivery_cost = 70.0 if delivery_option == 'delivery' else 0.0
            total_price = sum(product['subtotal'] for product in products)
            final_total = total_price + delivery_cost
            
            message += f"\nMietpreis: {total_price}€"
            if delivery_option == 'delivery':
                message += f"\nLieferung + Aufbau/Abbau: {delivery_cost}€"
                
                # Добавляем детали доставки
                delivery_address = request.session.get('delivery_address', '')
                delivery_datetime = request.session.get('delivery_datetime', '')
                return_datetime = request.session.get('return_datetime', '')
                delivery_instructions = request.session.get('delivery_instructions', '')
                
                if delivery_address:
                    message += f"\n\nLieferdetails:"
                    message += f"\nAdresse: {delivery_address}"
                    if delivery_datetime:
                        message += f"\nLieferung: {delivery_datetime}"
                    if return_datetime:
                        message += f"\nRückgabe: {return_datetime}"
                    if delivery_instructions:
                        message += f"\nAnweisungen: {delivery_instructions}"
                
            message += f"\nGesamt: {final_total}€"
            
            # Отправляем email администратору
            try:
                email = EmailMessage(
                    subject='Neue Anfrage von der Play & Jump Website',
                    body=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=['playandjump.de@gmail.com'],
                )
                email.content_subtype = 'plain'
                email.encoding = 'utf-8'
                email.send(fail_silently=False)
                
                # Отправляем подтверждение клиенту (если указан email)
                if customer_email:
                    confirmation_message = f"""
Hallo!

Vielen Dank für Ihre Anfrage auf der Play & Jump Website.

Wir haben Ihre Anfrage erhalten und werden uns in Kürze bei Ihnen melden.

Anfrage-Details:
"""
                    
                    for product in products:
                        if product.get('start_date') and product.get('end_date'):
                            confirmation_message += f"- {product['title']} ({product['start_date']} bis {product['end_date']}, {product['duration_days']} Tage) = {product['subtotal']}€\n"
                        else:
                            confirmation_message += f"- {product['title']} = {product['subtotal']}€\n"
                    
                    confirmation_message += f"\nMietpreis: {total_price}€"
                    if delivery_option == 'delivery':
                        confirmation_message += f"\nLieferung + Aufbau/Abbau: {delivery_cost}€"
                        
                        # Добавляем детали доставки
                        delivery_address = request.session.get('delivery_address', '')
                        delivery_datetime = request.session.get('delivery_datetime', '')
                        return_datetime = request.session.get('return_datetime', '')
                        delivery_instructions = request.session.get('delivery_instructions', '')
                        
                        if delivery_address:
                            confirmation_message += f"\n\nLieferdetails:"
                            confirmation_message += f"\nAdresse: {delivery_address}"
                            if delivery_datetime:
                                confirmation_message += f"\nLieferung: {delivery_datetime}"
                            if return_datetime:
                                confirmation_message += f"\nRückgabe: {return_datetime}"
                            if delivery_instructions:
                                confirmation_message += f"\nAnweisungen: {delivery_instructions}"
                        
                    confirmation_message += f"\nGesamt: {final_total}€"
                    
                    confirmation_email = EmailMessage(
                        subject='Ihre Anfrage wurde erhalten - Play & Jump',
                        body=confirmation_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[customer_email],
                    )
                    confirmation_email.content_subtype = 'plain'
                    confirmation_email.encoding = 'utf-8'
                    confirmation_email.send(fail_silently=True)
                
                # Очищаем корзину и данные доставки только при успешной отправке заявки
                request.session['cart'] = {}
                # Сбрасываем на pickup по умолчанию
                request.session['delivery_option'] = 'pickup'
                # Очищаем детали доставки
                if 'delivery_address' in request.session:
                    del request.session['delivery_address']
                if 'delivery_datetime' in request.session:
                    del request.session['delivery_datetime']
                if 'return_datetime' in request.session:
                    del request.session['return_datetime']
                if 'delivery_instructions' in request.session:
                    del request.session['delivery_instructions']
                request.session.modified = True
            
                return JsonResponse({
                    'success': True,
                    'message': 'Anfrage erfolgreich gesendet! Wir werden uns in Kürze bei Ihnen melden.'
                })
                
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': f'Fehler beim Senden der E-Mail: {str(e)}'
                })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Fehler bei der Verarbeitung der Anfrage: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'})


def cart_count(request):
    """Получение количества товаров в корзине"""
    cart_items = request.session.get('cart', {})
    
    # Подсчитываем только валидные товары (с product_id)
    valid_count = 0
    invalid_keys = []
    
    for cart_key, cart_data in cart_items.items():
        if isinstance(cart_data, dict) and 'product_id' in cart_data:
            try:
                # Проверяем, существует ли товар
                product = Product.objects.get(id=cart_data['product_id'], is_active=True)
                valid_count += 1
            except Product.DoesNotExist:
                invalid_keys.append(cart_key)
        elif isinstance(cart_data, str):  # Старый формат
            try:
                product = Product.objects.get(id=cart_key, is_active=True)
                valid_count += 1
            except Product.DoesNotExist:
                invalid_keys.append(cart_key)
    
    # Удаляем несуществующие товары из корзины
    if invalid_keys:
        for key in invalid_keys:
            del cart_items[key]
        request.session['cart'] = cart_items
        request.session.modified = True
        logger.debug(f"Removed invalid items: {invalid_keys}")
    
    # Отладочная информация
    logger.debug(f"cart_items = {cart_items}")
    logger.debug(f"valid_count = {valid_count}")
    
    return JsonResponse({'count': valid_count})


def kontakt(request):
    return render(request, 'main/kontakt.html')


def agb(request):
    return render(request, 'main/agb.html')


def impressum(request):
    return render(request, 'main/impressum.html')


def datenschutz(request):
    """Datenschutz page view"""
    return render(request, 'main/datenschutz.html')


def vermietung(request):
    return render(request, 'main/vermietung.html')


def neuigkeiten(request):
    """Страница новостей - перенаправляет на новую систему"""
    return redirect('catalog:news_list')


def cookie_richtlinie(request):
    """Cookie-Richtlinie (EU) page view"""
    return render(request, 'main/cookie_richtlinie.html')
