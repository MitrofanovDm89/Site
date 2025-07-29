# Site

Современный веб-сайт на Django с использованием лучших практик разработки.

## 🚀 Технологии

- **Django 4.2+** - веб-фреймворк
- **Django REST Framework** - API
- **PostgreSQL** - база данных
- **Redis** - кэширование
- **Celery** - фоновые задачи
- **Docker** - контейнеризация

## 📋 Требования

- Python 3.9+
- PostgreSQL 12+
- Redis 6+
- Node.js 16+ (для фронтенд инструментов)

## 🛠️ Установка

### 1. Клонирование репозитория
```bash
git clone https://github.com/MitrofanovDm89/Site.git
cd Site
```

### 2. Создание виртуального окружения
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения
```bash
cp .env.example .env
# Отредактируйте .env файл с вашими настройками
```

### 5. Настройка базы данных
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Сбор статических файлов
```bash
python manage.py collectstatic
```

### 7. Запуск сервера разработки
```bash
python manage.py runserver
```

## 🏗️ Структура проекта

```
Site/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── PROJECT_RULES.md
├── site/
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
│   └── users/
├── static/
├── media/
├── templates/
└── docs/
```

## 🔧 Настройки

### Переменные окружения (.env)
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=site_db
DB_USER=site_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
```

## 🧪 Тестирование

```bash
# Запуск всех тестов
python manage.py test

# Запуск с покрытием
coverage run --source='.' manage.py test
coverage report
coverage html
```

## 🚀 Деплой

### Подготовка к продакшену
1. Установите `DEBUG=False` в настройках
2. Настройте `ALLOWED_HOSTS`
3. Используйте PostgreSQL
4. Настройте Redis для кэширования
5. Соберите статические файлы
6. Настройте HTTPS

### Docker
```bash
# Сборка образа
docker build -t site .

# Запуск контейнеров
docker-compose up -d
```

## 📚 Документация

- [Правила работы над проектом](PROJECT_RULES.md)
- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
4. Отправьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект лицензирован под MIT License.

## 👥 Авторы

- **MitrofanovDm89** - [GitHub](https://github.com/MitrofanovDm89)

---

**Версия**: 1.0.0  
**Последнее обновление**: 2025 