# Правила работы над проектом Django

## 🚨 КРИТИЧЕСКИЕ ПРАВИЛА РАБОТЫ

### Стиль взаимодействия
- **DO NOT GIVE ME HIGH LEVEL STUFF** - если прошу исправление или объяснение, давай конкретный код или объяснение
- **НЕ ДАВАЙ "Here's how you can blablabla"** - сразу давай решение
- **Будь casual** - если не указано иное
- **Будь краток** - без лишней воды
- **Предлагай решения, которые я не думал** - предугадывай мои потребности
- **Относись ко мне как к эксперту** - не объясняй очевидное
- **Будь точным и тщательным**
- **Давай ответ сразу** - детальные объяснения после
- **Цени хорошие аргументы** - источник не важен
- **Рассматривай новые технологии** - не только конвенциональную мудрость
- **Можешь спекулировать** - но помечай это
- **НЕ морализируй**
- **Безопасность только когда критично**
- **ПРИ ОБНОВЛЕНИИ КОДА БУДЬ НА 100% УВЕРЕН ЧТО НИЧЕГО НЕ СЛОМАЛ**
- **Я использую Windows**

## 🎯 Основные принципы

### Сопоставление меню с Site2
- **"Startseite" в Site2** = **"Über uns" в нашем сайте**
- При упоминании "Startseite" из Site2 всегда подразумевается "Über uns" в нашем проекте

### Цветовая схема при заимствовании
- **Обязательно соблюдать нашу цветовую палитру** при заимствовании блоков с Site1 или Site2
- **Бирюзовый** (`teal-600`) - основной цвет
- **Коралловый** (`coral-500`) - акцентный цвет
- **Всегда адаптировать** цвета под нашу схему, даже если оригинал использует другие цвета

### Архитектура и структура
- **MVT (Model-View-Template)** - строгое следование паттерну Django
- **Модульность** - разделение на Django apps для переиспользования и разделения ответственности
- **DRY (Don't Repeat Yourself)** - избегать дублирования кода
- **SOLID принципы** - следование принципам объектно-ориентированного программирования

### Структура проекта
```
project_name/
├── manage.py
├── requirements.txt
├── .env
├── .gitignore
├── README.md
├── project_name/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── production.py
│   │   └── testing.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── __init__.py
│   ├── core/
│   ├── users/
│   └── [other_apps]/
├── static/
├── media/
├── templates/
│   ├── base.html
│   └── [app_templates]/
├── staticfiles/
└── docs/
```

## 📝 Стандарты кодирования

### Python/Django
- **PEP 8** - строгое соблюдение стиля кодирования Python
- **Django Coding Style** - следование рекомендациям Django
- **Именование**: 
  - Функции и переменные: `lowercase_with_underscores`
  - Классы: `PascalCase`
  - Константы: `UPPER_CASE`
  - Модели: `PascalCase` (единственное число)
  - URL паттерны: `kebab-case`

### Views
- **Function-Based Views (FBV)** для простой логики
- **Class-Based Views (CBV)** для сложной логики
- **Generic Views** для стандартных операций CRUD
- **API Views** с Django REST Framework для API endpoints

### Models
```python
# Пример правильной модели
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'
        ordering = ['-user__date_joined']
    
    def __str__(self):
        return f"Профиль {self.user.username}"
    
    def get_full_name(self):
        return f"{self.user.first_name} {self.user.last_name}".strip()
```

### Forms
```python
# Пример правильной формы
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'birth_date', 'avatar']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
    
    def clean_bio(self):
        bio = self.cleaned_data.get('bio')
        if bio and len(bio) < 10:
            raise forms.ValidationError('Биография должна содержать минимум 10 символов')
        return bio
```

## 🔒 Безопасность

### Обязательные меры
- **CSRF защита** - всегда включена
- **SQL Injection защита** - использование ORM, избегать raw SQL
- **XSS защита** - экранирование пользовательского ввода
- **Аутентификация** - использование Django User model
- **Авторизация** - декораторы `@login_required`, `@permission_required`
- **Валидация данных** - на уровне форм и моделей
- **HTTPS** - обязательно в продакшене

### Middleware
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

## 🚀 Производительность

### Оптимизация запросов
- **select_related()** для ForeignKey
- **prefetch_related()** для ManyToMany и reverse ForeignKey
- **only()** и **defer()** для выбора полей
- **Database indexes** для часто используемых полей

### Кэширование
```python
# Настройки кэширования
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# Использование в коде
from django.core.cache import cache

def get_user_data(user_id):
    cache_key = f'user_data_{user_id}'
    user_data = cache.get(cache_key)
    if user_data is None:
        user_data = User.objects.get(id=user_id)
        cache.set(cache_key, user_data, 3600)  # 1 час
    return user_data
```

## 🧪 Тестирование

### Структура тестов
```python
# tests.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class UserProfileTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_profile_creation(self):
        """Тест создания профиля пользователя"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
    
    def test_profile_update(self):
        """Тест обновления профиля"""
        self.client.login(username='testuser', password='testpass123')
        data = {'bio': 'Новая биография'}
        response = self.client.post(reverse('profile_update'), data)
        self.assertEqual(response.status_code, 302)
```

### Покрытие тестами
- **Модели**: 100% покрытие
- **Views**: минимум 80% покрытие
- **Forms**: 100% покрытие
- **URLs**: тестирование всех endpoints

## 📦 Зависимости

### Основные пакеты
```
Django>=4.2,<5.0
djangorestframework>=3.14.0
celery>=5.3.0
redis>=4.5.0
psycopg2-binary>=2.9.0
Pillow>=10.0.0
python-decouple>=3.8
whitenoise>=6.5.0
gunicorn>=21.2.0
```

### Разработка
```
pytest>=7.4.0
pytest-django>=4.5.0
coverage>=7.3.0
black>=23.0.0
flake8>=6.0.0
isort>=5.12.0
```

## 🔧 Настройки окружения

### settings/base.py
```python
import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party apps
    'rest_framework',
    # Local apps
    'apps.core',
    'apps.users',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project_name.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'project_name.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'users.User'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
```

## 📋 Чек-лист перед коммитом

### Код
- [ ] Код соответствует PEP 8
- [ ] Все импорты отсортированы (isort)
- [ ] Код отформатирован (black)
- [ ] Нет неиспользуемых импортов
- [ ] Все функции и классы имеют docstrings
- [ ] Переменные имеют понятные имена

### Django
- [ ] Модели имеют `__str__` метод
- [ ] Формы имеют валидацию
- [ ] Views обрабатывают ошибки
- [ ] URLs следуют RESTful принципам
- [ ] Используются правильные HTTP методы

### Безопасность
- [ ] Нет хардкода секретных ключей
- [ ] Пользовательский ввод валидируется
- [ ] Используются CSRF токены
- [ ] Нет SQL injection уязвимостей

### Тестирование
- [ ] Все новые функции покрыты тестами
- [ ] Тесты проходят успешно
- [ ] Покрытие кода не уменьшилось

## 🚀 Деплой

### Подготовка к продакшену
- [ ] DEBUG = False
- [ ] Настроены ALLOWED_HOSTS
- [ ] Используется PostgreSQL
- [ ] Настроено кэширование (Redis)
- [ ] Статические файлы собраны
- [ ] Настроен HTTPS
- [ ] Настроено логирование

### Переменные окружения (.env)
```env
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
```

## 📚 Документация

### Обязательная документация
- [ ] README.md с описанием проекта
- [ ] requirements.txt с зависимостями
- [ ] .env.example с примером переменных окружения
- [ ] Документация API (если есть)
- [ ] Инструкции по установке и запуску

### Комментарии в коде
```python
def complex_business_logic(user, data):
    """
    Выполняет сложную бизнес-логику для пользователя.
    
    Args:
        user: Объект пользователя Django
        data: Словарь с данными для обработки
    
    Returns:
        dict: Результат обработки данных
    
    Raises:
        ValidationError: Если данные некорректны
    """
    # Логика здесь
    pass
```

## 🔄 Git Workflow

### Ветки
- `main` - основная ветка, только стабильный код
- `develop` - ветка разработки
- `feature/feature-name` - новые функции
- `bugfix/bug-description` - исправления багов
- `hotfix/critical-fix` - критические исправления

### Коммиты
- Использовать conventional commits
- Примеры: `feat: add user profile`, `fix: resolve login issue`, `docs: update README`

## 📊 Мониторинг

### Логирование
```python
import logging

logger = logging.getLogger(__name__)

def some_view(request):
    logger.info(f"User {request.user} accessed the view")
    try:
        # Логика
        pass
    except Exception as e:
        logger.error(f"Error in view: {e}")
        raise
```

### Метрики
- Время ответа сервера
- Количество ошибок
- Использование памяти и CPU
- Количество активных пользователей

---

**Последнее обновление**: $(date)
**Версия**: 1.0.0 