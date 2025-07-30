"""
WSGI config for playandjump project.
"""

import os

from django.core.wsgi import get_wsgi_application

# Используем production настройки если DJANGO_SETTINGS_MODULE не установлен
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'playandjump.settings_production')

application = get_wsgi_application() 