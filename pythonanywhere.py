#!/usr/bin/env python
"""
WSGI config for PythonAnywhere deployment.
"""

import os
import sys

# Добавляем путь к проекту
path = '/home/yourusername/playandjump'
if path not in sys.path:
    sys.path.append(path)

# Устанавливаем переменные окружения
os.environ['DJANGO_SETTINGS_MODULE'] = 'playandjump.settings_production'

# Импортируем приложение
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application() 