# 🎮 PlayAndJump - Сайт аренды игрового оборудования

Django-сайт для аренды игрового оборудования на немецком языке.

## 🚀 Быстрый деплой на PythonAnywhere

### 📋 Подготовка
1. Создайте аккаунт на [PythonAnywhere](https://www.pythonanywhere.com)
2. Загрузите все файлы проекта в папку `/home/ваше_имя_пользователя/playandjump/`
3. Создайте веб-приложение в разделе "Web"

### ⚡ Автоматический деплой
```bash
# В консоли PythonAnywhere
cd playandjump
chmod +x deploy_script.sh
./deploy_script.sh
```

### 📖 Подробные инструкции
См. файл [QUICK_DEPLOY.md](QUICK_DEPLOY.md) для пошаговых инструкций.

## 🛠️ Локальная разработка

### Установка зависимостей
```bash
# Активируйте виртуальное окружение
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Установите зависимости
pip install -r requirements.txt
```

### Запуск сервера разработки
```bash
# Выполните миграции
python manage.py migrate

# Создайте суперпользователя
python manage.py createsuperuser

# Запустите сервер
python manage.py runserver
```

Сайт будет доступен по адресу: http://127.0.0.1:8000/

## 📁 Структура проекта

```
playandjump/
├── catalog/          # Приложение каталога товаров
├── main/             # Основные страницы сайта
├── playandjump/      # Настройки Django
├── static/           # Статические файлы
├── templates/        # HTML шаблоны
├── media/           # Загружаемые файлы
└── logs/            # Логи приложения
```

## 🎯 Основной функционал

- **Каталог товаров** - категории и продукты
- **Система бронирования** - заказ оборудования
- **Корзина покупок** - управление заказами
- **Админ-панель** - управление контентом
- **Мультиязычность** - немецкий язык

## 🗄️ Модели данных

- `Category` - категории товаров
- `Product` - товары/оборудование
- `Availability` - доступность товаров
- `Booking` - бронирования
- `Service` - дополнительные услуги

## 🔧 Технологии

- **Django 4.2** - веб-фреймворк
- **SQLite** - база данных
- **WhiteNoise** - статические файлы
- **Pillow** - обработка изображений
- **Bootstrap** - CSS фреймворк

## 📊 Статус проекта

✅ **Готов к деплою**  
✅ **Локально работает**  
✅ **Все зависимости установлены**  
✅ **Миграции выполнены**  
✅ **Статические файлы собраны**  

## 🚀 Деплой

### PythonAnywhere (Рекомендуется)
- Бесплатный план
- Простая настройка
- Поддержка Django
- Автоматический SSL

### Другие платформы
- **Heroku** - см. `Procfile`
- **Railway** - см. `railway.json`
- **Docker** - см. `Dockerfile`

## 📞 Поддержка

- **PythonAnywhere Support**: support@pythonanywhere.com
- **Django Documentation**: https://docs.djangoproject.com/
- **Stack Overflow**: https://stackoverflow.com/questions/tagged/django

## 📝 Лицензия

MIT License

---

**🎉 Проект готов к продакшену!** 