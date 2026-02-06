"""
Production settings for playandjump project.
"""

import os
from pathlib import Path
from .settings import *

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-playandjump-secret-key-2024')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.pythonanywhere.com',
    '.railway.app',
    '.herokuapp.com',
    'playandjump.de',
    'www.playandjump.de',
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'whitenoise.runserver_nostatic',  # Для статических файлов
    'ckeditor',
    'catalog',
    'main',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Для статических файлов
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Database - используем SQLite для PythonAnywhere (бесплатный план)
# Включаем WAL mode для поддержки параллельных чтений и записей
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 20,  # Увеличиваем timeout до 20 секунд
            # WAL mode будет включен автоматически при первом подключении через init_command
        },
    }
}

# Включаем WAL mode для SQLite при первом подключении
# Это позволяет параллельные чтения и записи
from django.db.backends.signals import connection_created
import threading

_wal_mode_activated = threading.Lock()

def activate_sqlite_wal_mode(sender, connection, **kwargs):
    """Включает WAL mode для SQLite, чтобы разрешить параллельные операции"""
    if connection.vendor == 'sqlite':
        # Используем lock, чтобы избежать одновременных попыток включить WAL
        if _wal_mode_activated.acquire(blocking=False):
            try:
                # Проверяем, включен ли уже WAL mode
                with connection.cursor() as cursor:
                    cursor.execute("PRAGMA journal_mode;")
                    current_mode = cursor.fetchone()[0].upper()
                    
                    if current_mode != 'WAL':
                        # Пытаемся включить WAL mode только если он не включен
                        cursor.execute("PRAGMA journal_mode=WAL;")
                        cursor.execute("PRAGMA synchronous=NORMAL;")
                        cursor.execute("PRAGMA busy_timeout=20000;")
            except Exception:
                # Если не удалось включить WAL (база заблокирована), просто пропускаем
                pass
            finally:
                _wal_mode_activated.release()

connection_created.connect(activate_sqlite_wal_mode)

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise для статических файлов
# Используем версию без манифеста для совместимости
STATICFILES_STORAGE = 'whitenoise.storage.WhiteNoiseStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Sessions - используем файловое хранилище вместо базы данных
# Это решает проблему блокировки SQLite при одновременных запросах
SESSION_ENGINE = 'django.contrib.sessions.backends.file'
# Путь для хранения файлов сессий
SESSION_FILE_PATH = str(BASE_DIR / 'sessions')
# Создаем папку для сессий, если её нет (безопасный способ)
os.makedirs(SESSION_FILE_PATH, exist_ok=True)

# Email settings (настройте под ваш хостинг)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'playandjump.de@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'kfuowvtoqsmxffng')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@playandjump.de')

# CKEditor Configuration
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent'],
            ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink'],
            ['RemoveFormat', 'Source'],
        ],
        'height': 300,
        'width': '100%',
        'removePlugins': 'stylesheetparser',
        'allowedContent': True,
    },
    'product_description': {
        'toolbar': 'Simple',
        'toolbar_Simple': [
            ['Bold', 'Italic'],
            ['NumberedList', 'BulletedList'],
            ['Link', 'Unlink'],
        ],
        'height': 200,
        'width': '100%',
        'removePlugins': 'stylesheetparser',
        'allowedContent': True,
    }
}

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField' 