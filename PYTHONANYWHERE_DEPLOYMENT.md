# 🐍 Деплой на PythonAnywhere

## 📋 Подготовка

### 1. Создайте аккаунт на PythonAnywhere
- Зайдите на [pythonanywhere.com](https://www.pythonanywhere.com)
- Зарегистрируйтесь (бесплатный план)
- Запомните ваше имя пользователя

### 2. Подготовьте проект локально
```bash
# Соберите статические файлы
python manage.py collectstatic --noinput

# Создайте папку для логов
mkdir logs

# Проверьте, что все файлы на месте
ls -la
```

## 🚀 Деплой на PythonAnywhere

### 1. Загрузите код
```bash
# В консоли PythonAnywhere
git clone https://github.com/yourusername/playandjump.git
cd playandjump
```

### 2. Создайте виртуальное окружение
```bash
# В консоли PythonAnywhere
mkvirtualenv --python=/usr/bin/python3.11 playandjump
pip install -r requirements_production.txt
```

### 3. Настройте WSGI файл
- Откройте `/var/www/yourusername_pythonanywhere_com_wsgi.py`
- Замените содержимое на код из `pythonanywhere_wsgi.py`
- **ВАЖНО**: Замените `yourusername` на ваше имя пользователя PythonAnywhere

### 4. Настройте переменные окружения
```bash
# В консоли PythonAnywhere
export SECRET_KEY="your-secret-key-here"
export DEBUG="False"
```

### 5. Выполните миграции
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Соберите статические файлы
```bash
python manage.py collectstatic --noinput
```

### 7. Перезапустите веб-приложение
- Зайдите в раздел "Web" на PythonAnywhere
- Нажмите "Reload yourusername.pythonanywhere.com"

## 🔧 Настройка домена

### 1. Настройте ALLOWED_HOSTS
В файле `playandjump/settings_pythonanywhere.py` замените:
```python
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.pythonanywhere.com',
    'yourusername.pythonanywhere.com',  # Замените на ваш домен
]
```

### 2. Настройте WSGI файл
В файле `pythonanywhere_wsgi.py` замените:
```python
path = '/home/yourusername/playandjump'  # Замените yourusername
```

## 📊 Проверка работы

### 1. Проверьте сайт
- Откройте `yourusername.pythonanywhere.com`
- Убедитесь, что главная страница загружается

### 2. Проверьте админ-панель
- Откройте `yourusername.pythonanywhere.com/admin/`
- Войдите с созданными учетными данными

### 3. Проверьте статические файлы
- Убедитесь, что CSS и изображения загружаются
- Проверьте логотип и фоновые изображения

## 🛠️ Устранение проблем

### Ошибка 500
```bash
# Проверьте логи
tail -f /var/log/yourusername.pythonanywhere.com.error.log

# Проверьте настройки
python manage.py check --deploy
```

### Статические файлы не загружаются
```bash
# Пересоберите статические файлы
python manage.py collectstatic --noinput --clear

# Проверьте права доступа
ls -la staticfiles/
```

### Ошибки миграций
```bash
# Проверьте миграции
python manage.py makemigrations --check

# Выполните миграции
python manage.py migrate
```

### Проблемы с базой данных
```bash
# Проверьте базу данных
python manage.py dbshell

# Создайте резервную копию
python manage.py dumpdata > backup.json
```

## 📈 Оптимизация

### 1. Сжатие изображений
```bash
# Установите Pillow для оптимизации
pip install Pillow

# Используйте Django для сжатия изображений
```

### 2. Кэширование
```bash
# Настройте кэш в settings
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
```

### 3. Логирование
```bash
# Проверьте логи
tail -f logs/django.log

# Настройте ротацию логов
```

## 🔒 Безопасность

### 1. Секретный ключ
```bash
# Сгенерируйте новый секретный ключ
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Установите его в переменных окружения
export SECRET_KEY="новый-секретный-ключ"
```

### 2. HTTPS
- PythonAnywhere автоматически предоставляет HTTPS
- Убедитесь, что DEBUG = False

### 3. Админ-панель
- Создайте сильного суперпользователя
- Используйте сложный пароль

## 📞 Поддержка

### Логи PythonAnywhere
- Error logs: `/var/log/yourusername.pythonanywhere.com.error.log`
- Access logs: `/var/log/yourusername.pythonanywhere.com.access.log`

### Полезные команды
```bash
# Перезапуск веб-приложения
touch /var/www/yourusername_pythonanywhere_com_wsgi.py

# Проверка статуса
python manage.py check --deploy

# Очистка кэша
python manage.py clearcache
```

## 🎉 Готово!

После выполнения всех шагов ваш сайт будет доступен по адресу:
`https://yourusername.pythonanywhere.com`

### Что дальше:
1. Настройте домен (если есть)
2. Добавьте SSL сертификат
3. Настройте резервное копирование
4. Добавьте мониторинг 