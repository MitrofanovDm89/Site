from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from django.conf import settings
from django.utils.encoding import force_str
import json
import logging
from catalog.models import Product
from datetime import datetime, date

def format_date_dmy(date_str):
    """Преобразует дату из формата YYYY-MM-DD в DD-MM-YYYY"""
    if not date_str:
        return date_str
    try:
        # Если это ISO datetime формат (2025-11-05T10:00), берем только дату
        if 'T' in date_str:
            date_part = date_str.split('T')[0]
        else:
            date_part = date_str
        
        date_obj = datetime.strptime(date_part, '%Y-%m-%d').date()
        return date_obj.strftime('%d-%m-%Y')
    except (ValueError, AttributeError):
        # Если формат не подходит, возвращаем как есть
        return date_str

def format_datetime_dmy(datetime_str):
    """Преобразует datetime из формата YYYY-MM-DDTHH:MM в DD-MM-YYYY HH:MM"""
    if not datetime_str:
        return datetime_str
    try:
        if 'T' in datetime_str:
            # ISO datetime формат (2025-11-05T10:00)
            dt = datetime.strptime(datetime_str.split('+')[0].split('.')[0], '%Y-%m-%dT%H:%M')
            return dt.strftime('%d-%m-%Y %H:%M')
        else:
            # Просто дата
            return format_date_dmy(datetime_str)
    except (ValueError, AttributeError):
        # Если формат не подходит, возвращаем как есть
        return datetime_str

def format_price(price):
    """Форматирует цену, убирая .0 если это целое число"""
    try:
        price_float = float(price)
        if price_float.is_integer():
            return str(int(price_float))
        else:
            return str(price_float)
    except (ValueError, TypeError):
        return str(price)

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
            # Логируем сырой запрос для отладки
            logger.debug(f"add_to_cart request.body: {request.body}")
            
            data = json.loads(request.body)
            product_id = data.get('product_id')
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            
            logger.debug(f"add_to_cart: product_id={product_id}, start_date={start_date}, end_date={end_date}")
            
            if not product_id:
                return JsonResponse({'success': False, 'error': 'Product ID is required'})
                
            if not start_date or not end_date:
                return JsonResponse({'success': False, 'error': 'Start and end dates are required'})
            
            # Получаем товар
            try:
                product = Product.objects.get(id=product_id, is_active=True)
            except Product.DoesNotExist:
                logger.error(f"Product not found: id={product_id}")
                return JsonResponse({'success': False, 'error': 'Product not found'})
            
            # Проверяем даты
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError as e:
                logger.error(f"Date parsing error: {e}, start_date={start_date}, end_date={end_date}")
                return JsonResponse({'success': False, 'error': f'Invalid date format: {str(e)}'})
            
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
            try:
                price_per_day = float(product.price) if product.price else 0
            except (ValueError, TypeError) as e:
                logger.error(f"Price conversion error: {e}, product.price={product.price}")
                price_per_day = 0
            
            cart = request.session['cart']
            cart[cart_key] = {
                'product_id': product_id,
                'start_date': start_date,
                'end_date': end_date,
                'price_per_day': price_per_day
            }
                
            request.session.modified = True
            
            logger.debug(f"Product added to cart: {product.title}, cart_key={cart_key}")
            
            return JsonResponse({
                'success': True,
                'message': f'{product.title} wurde in den Warenkorb gelegt',
                'cart_count': len(cart)
            })
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}, request.body: {request.body}")
            return JsonResponse({'success': False, 'error': f'Invalid JSON: {str(e)}'})
        except Exception as e:
            logger.error(f"Unexpected error in add_to_cart: {str(e)}", exc_info=True)
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
                    start_date_formatted = format_date_dmy(product['start_date'])
                    end_date_formatted = format_date_dmy(product['end_date'])
                    subtotal_formatted = format_price(product['subtotal'])
                    message += f"- {product['title']} ({start_date_formatted} bis {end_date_formatted}, {product['duration_days']} Tage) = {subtotal_formatted}€\n"
                else:
                    subtotal_formatted = format_price(product['subtotal'])
                    message += f"- {product['title']} = {subtotal_formatted}€\n"
            
            # Добавляем информацию о доставке
            delivery_option = request.session.get('delivery_option', 'pickup')
            delivery_cost = 70.0 if delivery_option == 'delivery' else 0.0
            total_price = sum(product['subtotal'] for product in products)
            final_total = total_price + delivery_cost
            
            message += f"\nMietpreis: {format_price(total_price)}€"
            if delivery_option == 'delivery':
                message += f"\nLieferung + Aufbau/Abbau: {format_price(delivery_cost)}€"
                
                # Добавляем детали доставки
                delivery_address = request.session.get('delivery_address', '')
                delivery_datetime = request.session.get('delivery_datetime', '')
                return_datetime = request.session.get('return_datetime', '')
                delivery_instructions = request.session.get('delivery_instructions', '')
                
                if delivery_address:
                    message += f"\n\nLieferdetails:"
                    message += f"\nAdresse: {delivery_address}"
                    if delivery_datetime:
                        delivery_datetime_formatted = format_datetime_dmy(delivery_datetime)
                        message += f"\nLieferung: {delivery_datetime_formatted}"
                    if return_datetime:
                        return_datetime_formatted = format_datetime_dmy(return_datetime)
                        message += f"\nRückgabe: {return_datetime_formatted}"
                    if delivery_instructions:
                        message += f"\nAnweisungen: {delivery_instructions}"
                
            message += f"\nGesamt: {format_price(final_total)}€"
            
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
                
                # Автоответ клиенту (корпоративное письмо: plain + HTML)
                if customer_email:
                    from html import escape as html_escape
                    anrede = f"Guten Tag, {customer_name_safe}," if (customer_name_safe and customer_name_safe != 'Nicht angegeben') else "Guten Tag,"
                    # Строим строки по товарам и блок доставки один раз
                    product_lines_plain = []
                    product_lines_html = []
                    for product in products:
                        if product.get('start_date') and product.get('end_date'):
                            start_f = format_date_dmy(product['start_date'])
                            end_f = format_date_dmy(product['end_date'])
                            sub_f = format_price(product['subtotal'])
                            product_lines_plain.append(f"  • {product['title']} ({start_f} bis {end_f}, {product['duration_days']} Tag(e)) = {sub_f} €")
                            product_lines_html.append(f"<li>{html_escape(product['title'])} ({start_f} bis {end_f}, {product['duration_days']} Tag(e)) = {sub_f} €</li>")
                        else:
                            sub_f = format_price(product['subtotal'])
                            product_lines_plain.append(f"  • {product['title']} = {sub_f} €")
                            product_lines_html.append(f"<li>{html_escape(product['title'])} = {sub_f} €</li>")
                    delivery_plain = f"\nMietpreis: {format_price(total_price)} €"
                    delivery_html = f"<p><strong>Mietpreis:</strong> {format_price(total_price)} €</p>"
                    if delivery_option == 'delivery':
                        delivery_plain += f"\nLieferung + Auf- und Abbau: {format_price(delivery_cost)} €"
                        delivery_html += f"<p><strong>Lieferung + Auf- und Abbau:</strong> {format_price(delivery_cost)} €</p>"
                        addr = request.session.get('delivery_address', '')
                        dt_del = request.session.get('delivery_datetime', '')
                        dt_ret = request.session.get('return_datetime', '')
                        instr = request.session.get('delivery_instructions', '')
                        if addr:
                            delivery_plain += f"\n\nLieferdetails:\nAdresse: {addr}"
                            delivery_html += f"<p><strong>Lieferdetails:</strong><br>Adresse: {html_escape(addr)}"
                            if dt_del:
                                delivery_plain += f"\nLieferung: {format_datetime_dmy(dt_del)}"
                                delivery_html += f"<br>Lieferung: {format_datetime_dmy(dt_del)}"
                            if dt_ret:
                                delivery_plain += f"\nRückgabe: {format_datetime_dmy(dt_ret)}"
                                delivery_html += f"<br>Rückgabe: {format_datetime_dmy(dt_ret)}"
                            if instr:
                                delivery_plain += f"\nAnweisungen: {instr}"
                                delivery_html += f"<br>Anweisungen: {html_escape(instr)}"
                            delivery_html += "</p>"
                    delivery_plain += f"\nGesamt: {format_price(final_total)} €"
                    delivery_html += f"<p><strong>Gesamt: {format_price(final_total)} €</strong></p>"
                    # Plain
                    confirmation_message = f"""{anrede}

vielen Dank für Ihre Buchungsanfrage.

Wir haben Ihre Anfrage erhalten. Unser Team wird sich in Kürze bei Ihnen melden, um die Details zu bestätigen.

Zur Information – Ihre Anfrage im Überblick:

"""
                    confirmation_message += "\n".join(product_lines_plain) + delivery_plain + """

---
Mit freundlichen Grüßen

Ihr Play & Jump Team
www.playandjump.de
"""
                    # HTML
                    html_body = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0; padding:0; font-family: Arial, sans-serif; font-size: 15px; line-height: 1.5; color: #333;">
<div style="max-width: 600px; margin: 0 auto; padding: 24px;">
  <p style="margin: 0 0 16px;">{html_escape(anrede)}</p>
  <p style="margin: 0 0 16px;">vielen Dank für Ihre Buchungsanfrage.</p>
  <p style="margin: 0 0 20px;">Wir haben Ihre Anfrage erhalten. Unser Team wird sich in Kürze bei Ihnen melden, um die Details zu bestätigen.</p>
  <p style="margin: 0 0 8px;"><strong>Zur Information – Ihre Anfrage im Überblick:</strong></p>
  <ul style="margin: 0 0 16px; padding-left: 20px;">{''.join(product_lines_html)}</ul>
  {delivery_html}
  <p style="margin-top: 24px; padding-top: 16px; border-top: 1px solid #ddd; color: #555;">
    Mit freundlichen Grüßen<br><br>
    <strong>Ihr Play & Jump Team</strong><br>
    <a href="https://www.playandjump.de" style="color: #0d9488;">www.playandjump.de</a>
  </p>
</div>
</body>
</html>"""
                    confirmation_email = EmailMultiAlternatives(
                        subject='Ihre Buchungsanfrage bei Play & Jump – wir haben sie erhalten',
                        body=confirmation_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[customer_email],
                    )
                    confirmation_email.attach_alternative(html_body, 'text/html')
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


def send_contact(request):
    """Отправка сообщения через контактную форму"""
    if request.method == 'POST':
        try:
            # Получаем данные из JSON
            data = json.loads(request.body)
            first_name = data.get('first_name', '').strip()
            last_name = data.get('last_name', '').strip()
            email = data.get('email', '').strip()
            phone = data.get('phone', '').strip()
            message = data.get('message', '').strip()
            
            # Сохраняем оригинальные данные с немецкими символами
            # Заменяем символы только в email тексте для Windows консоли
            
            # Валидация
            if not email:
                return JsonResponse({
                    'success': False,
                    'message': 'E-Mail-Adresse ist erforderlich'
                })
            
            if not message:
                return JsonResponse({
                    'success': False,
                    'message': 'Nachricht ist erforderlich'
                })
            
            # Формируем имя
            full_name = f"{first_name} {last_name}".strip()
            if not full_name:
                full_name = "Unbekannt"
            
            # Функция для замены символов только для Windows консоли
            def console_safe(text):
                if text:
                    replacements = {
                        'ü': 'ue', 'Ü': 'Ue',
                        'ö': 'oe', 'Ö': 'Oe', 
                        'ä': 'ae', 'Ä': 'Ae',
                        'ß': 'ss'
                    }
                    for old, new in replacements.items():
                        text = text.replace(old, new)
                return text
            
            # Формируем текст письма с оригинальными символами
            email_subject = f"Neue Kontaktanfrage von {full_name}"
            email_body = f"""
Neue Kontaktanfrage über die Website:

Name: {full_name}
E-Mail: {email}
Telefon: {phone or 'Nicht angegeben'}

Nachricht:
{message}

---
Diese Nachricht wurde über das Kontaktformular auf playandjump.de gesendet.
"""
            
            # Отправляем email на правильный адрес
            try:
                send_mail(
                    subject=email_subject,
                    message=email_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=['playandjump.de@gmail.com'],
                    fail_silently=False,
                )
            except UnicodeEncodeError:
                # Если ошибка кодировки, используем безопасную версию для консоли
                logger.warning("Unicode encoding error, using console-safe version")
                send_mail(
                    subject=console_safe(email_subject),
                    message=console_safe(email_body),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=['playandjump.de@gmail.com'],
                    fail_silently=False,
                )
            
            return JsonResponse({
                'success': True,
                'message': 'Ihre Nachricht wurde erfolgreich gesendet!'
            })
            
        except Exception as e:
            logger.error(f"Error sending contact form: {e}")
            return JsonResponse({
                'success': False,
                'message': 'Ein Fehler ist aufgetreten. Bitte versuchen Sie es erneut.'
            })
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'})
