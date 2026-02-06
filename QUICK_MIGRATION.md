# ⚡ Быстрая миграция на клиентский Python Anywhere

## 📝 Краткая инструкция

### На ТВОЕМ аккаунте (экспорт данных)

**ВАЖНО:** Сохрани все данные (брони, товары, пользователи) перед переносом!

```bash
cd /home/твое_имя/playandjump
source venv/bin/activate  # если есть venv

# Экспорт ВСЕХ данных (брони, товары, пользователи)
python manage.py dumpdata catalog main auth > backup.json

# Создание архива медиа файлов (изображения товаров)
tar -czf media_backup.tar.gz media/

# Проверка размера файлов
ls -lh backup.json media_backup.tar.gz
```

**Скачай файлы через Files:**
1. Зайди в раздел **Files** на Python Anywhere
2. Найди файлы: `backup.json` и `media_backup.tar.gz`
3. Нажми на каждый файл → **Download**
4. Скачай файлы на компьютер

**Альтернатива:** Можно скопировать файл `db.sqlite3` напрямую (см. `BACKUP_AND_RESTORE.md`)

---

### На КЛИЕНТСКОМ аккаунте

#### 1. Клонирование и установка

```bash
cd /home/имя_клиента/
git clone https://github.com/MitrofanovDm89/Site.git playandjump
cd playandjump

python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements_pythonanywhere.txt
```

#### 2. Настройка переменных окружения

Создай `.env` файл в корне проекта:

```bash
echo "SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')" > .env
```

#### 3. Обновить ALLOWED_HOSTS

В `playandjump/settings_pythonanywhere.py` замени:
```python
'имя_клиента.pythonanywhere.com'  # вместо dlktsprdct.pythonanywhere.com
```

#### 4. Настроить веб-приложение

В разделе **Web**:
1. **Add a new web app** → Manual configuration → Python 3.10
2. **Source code**: `/home/имя_клиента/playandjump`
3. **Working directory**: `/home/имя_клиента/playandjump`

Отредактируй WSGI файл:
```python
import os
import sys

project_home = '/home/имя_клиента/playandjump'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ['DJANGO_SETTINGS_MODULE'] = 'playandjump.settings_pythonanywhere'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

#### 5. Загрузка бэкапа и импорт данных

**Через Files:**
1. Загрузи `backup.json` и `media_backup.tar.gz` через **Files**
2. Положи их в `/home/имя_клиента/playandjump/`

**В консоли:**

```bash
source venv/bin/activate
cd /home/имя_клиента/playandjump

# Сначала создай структуру базы
python manage.py migrate

# Импорт данных (брони, товары, пользователи)
python manage.py loaddata backup.json

# Распаковка медиа файлов
tar -xzf media_backup.tar.gz

# Сбор статических файлов
python manage.py collectstatic --noinput

# Создание суперпользователя (если нужен новый)
python manage.py createsuperuser
```

**Проверка:**
```bash
python manage.py shell
>>> from catalog.models import Booking, Product
>>> Booking.objects.count()  # Должно показать количество броней
>>> Product.objects.count()   # Должно показать количество товаров
>>> exit()
```

#### 6. Настроить статические файлы

В разделе **Web** → **Static files**:
- `/static/` → `/home/имя_клиента/playandjump/staticfiles`
- `/media/` → `/home/имя_клиента/playandjump/media`

#### 7. Перезагрузить

Нажми **Reload** в разделе Web.

---

## ✅ Готово!

Сайт должен быть доступен по адресу: `https://имя_клиента.pythonanywhere.com`

