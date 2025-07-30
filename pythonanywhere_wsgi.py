#!/usr/bin/env python
"""
WSGI config for PythonAnywhere deployment.
Замените 'yourusername' на ваше имя пользователя PythonAnywhere.
"""

import os
import sys

# Добавляем путь к проекту (замените 'yourusername' на ваше имя пользователя)
path = '/home/yourusername/playandjump'
if path not in sys.path:
    sys.path.append(path)

# Устанавливаем переменные окружения
os.environ['DJANGO_SETTINGS_MODULE'] = 'playandjump.settings_production'
os.environ['SECRET_KEY'] = 'your-secret-key-here'
os.environ['DEBUG'] = 'False'

# Импортируем приложение
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application() 