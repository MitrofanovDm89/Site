# Миграция сайта с одного Python Anywhere на другой

## 📋 Подготовка на ТВОЕМ аккаунте (исходный сервер)

### 1. Экспорт базы данных (если есть важные данные)

В консоли Python Anywhere (твой аккаунт):

```bash
cd /home/твое_имя_пользователя/playandjump
python manage.py dumpdata > backup_data.json
```

Или только определенные приложения:
```bash
python manage.py dumpdata catalog main auth > backup_data.json
```

### 2. Создание архива медиа файлов

```bash
cd /home/твое_имя_пользователя/playandjump
tar -czf media_backup.tar.gz media/
```

### 3. Проверка, что код в Git (уже сделано)

Код уже в репозитории: `https://github.com/MitrofanovDm89/Site.git`

---

## 🚀 Настройка на КЛИЕНТСКОМ аккаунте (новый сервер)

### ШАГ 1: Клонирование репозитория

В консоли Python Anywhere (клиентский аккаунт):

```bash
cd /home/имя_клиента/
git clone https://github.com/MitrofanovDm89/Site.git playandjump
cd playandjump
```

### ШАГ 2: Создание виртуального окружения

```bash
python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Или если нет requirements.txt:
```bash
pip install Django>=4.2,<5.0 django-ckeditor>=6.7.0 Pillow>=10.0.0 whitenoise>=6.5.0
```

### ШАГ 3: Настройка переменных окружения

Создай файл `.env` в корне проекта:

```bash
nano /home/имя_клиента/playandjump/.env
```

Или через Files в Python Anywhere создай файл `.env` со следующим содержимым:

```
SECRET_KEY=сгенерируй_новый_секретный_ключ
ALLOWED_HOSTS=имя_клиента.pythonanywhere.com,playandjump.de,www.playandjump.de
```

**Для генерации SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### ШАГ 4: Обновление settings для клиентского аккаунта

Обнови `playandjump/settings_pythonanywhere.py` или создай новый файл с правильным доменом:

В файле `settings_pythonanywhere.py` измени:
```python
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.pythonanywhere.com',
    'имя_клиента.pythonanywhere.com',  # ← НОВЫЙ ДОМЕН
    'playandjump.de',
    'www.playandjump.de',
]
```

### ШАГ 5: Настройка WSGI файла для веб-приложения

1. Зайди в раздел **Web** в Python Anywhere
2. Нажми **Add a new web app**
3. Выбери **Manual configuration**
4. Выбери Python версию (3.10)
5. Нажми **Next**

В разделе **Code** укажи:
- **Source code**: `/home/имя_клиента/playandjump`
- **Working directory**: `/home/имя_клиента/playandjump`

### ШАГ 6: Редактирование WSGI файла

Нажми **Edit** рядом с WSGI configuration file и замени содержимое:

```python
import os
import sys

# add your project directory to the sys.path
project_home = '/home/имя_клиента/playandjump'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# set environment variable to tell django where your settings.py is
os.environ['DJANGO_SETTINGS_MODULE'] = 'playandjump.settings_pythonanywhere'

# serve django via WSGI
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### ШАГ 7: Выполнение миграций

В консоли (с активированным venv):

```bash
cd /home/имя_клиента/playandjump
source venv/bin/activate
python manage.py migrate
```

### ШАГ 8: Импорт данных (если экспортировал)

Если нужно импортировать данные:

```bash
python manage.py loaddata backup_data.json
```

### ШАГ 9: Создание суперпользователя (если нужен новый)

```bash
python manage.py createsuperuser
```

### ШАГ 10: Копирование медиа файлов

**Вариант 1: Через веб-интерфейс Files**
- Загрузи `media_backup.tar.gz` через Files
- Распакуй в `/home/имя_клиента/playandjump/media/`

**Вариант 2: Через консоль (если есть доступ к старому серверу)**
```bash
# На старом сервере
cd /home/твое_имя/playandjump
tar -czf media_backup.tar.gz media/
# Скачай файл через Files

# На новом сервере
cd /home/имя_клиента/playandjump
# Загрузи media_backup.tar.gz через Files, затем:
tar -xzf media_backup.tar.gz
```

### ШАГ 11: Сбор статических файлов

```bash
python manage.py collectstatic --noinput
```

### ШАГ 12: Настройка статических файлов в Web разделе

В разделе **Web** → **Static files**:

Добавь:
- **URL**: `/static/` → **Directory**: `/home/имя_клиента/playandjump/staticfiles`
- **URL**: `/media/` → **Directory**: `/home/имя_клиента/playandjump/media`

### ШАГ 13: Настройка домена (если есть playandjump.de)

1. В разделе **Web** → **Static files** и **Domains**
2. Добавь домен: `playandjump.de` и `www.playandjump.de`
3. Настрой DNS записи у регистратора домена:
   - A-запись: IP адрес Python Anywhere (узнай в разделе Web)
   - CNAME для www → имя_клиента.pythonanywhere.com

### ШАГ 14: Перезагрузка веб-приложения

В разделе **Web** нажми кнопку **Reload** (зеленая кнопка)

---

## ✅ Проверка после миграции

1. Открой сайт: `https://имя_клиента.pythonanywhere.com`
2. Проверь админку: `https://имя_клиента.pythonanywhere.com/admin/`
3. Проверь медиа файлы (изображения товаров)
4. Проверь отправку email (тестовая форма)

---

## ⚠️ Важные моменты

1. **SECRET_KEY**: Обязательно смени на новый на клиентском аккаунте!
2. **Email пароли**: Если используешь Gmail, может понадобиться новый пароль приложения
3. **База данных**: Если на клиентском аккаунте уже есть данные, сначала сделай бэкап
4. **Домен**: После переноса обнови DNS записи, если используется свой домен

---

## 🔄 Быстрая команда для проверки

После всех настроек, выполни в консоли:

```bash
cd /home/имя_клиента/playandjump
source venv/bin/activate
python manage.py check --deploy
```

Эта команда проверит настройки для продакшена.

