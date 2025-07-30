# 🚀 Деплой проекта Play & Jump

## Подготовка к деплою

### 1. Локальная подготовка

```bash
# Запустите скрипт подготовки
python deploy_prepare.py

# Или выполните команды вручную:
python manage.py collectstatic --noinput
python manage.py makemigrations --check
mkdir logs
```

### 2. Переменные окружения

Создайте файл `.env` на основе `env_production.example`:

```bash
# Скопируйте пример
cp env_production.example .env

# Отредактируйте .env файл
```

## Деплой на разные хостинги

### 🐍 PythonAnywhere

1. **Создайте аккаунт** на [pythonanywhere.com](https://www.pythonanywhere.com)

2. **Загрузите код**:
   ```bash
   git clone https://github.com/yourusername/playandjump.git
   ```

3. **Настройте виртуальное окружение**:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.11 playandjump
   pip install -r requirements_production.txt
   ```

4. **Настройте WSGI файл**:
   - Откройте `/var/www/yourusername_pythonanywhere_com_wsgi.py`
   - Замените содержимое на код из `pythonanywhere.py`
   - Измените путь на ваш: `/home/yourusername/playandjump`

5. **Настройте переменные окружения**:
   ```bash
   # В консоли PythonAnywhere
   export SECRET_KEY="your-secret-key"
   export DEBUG="False"
   ```

6. **Выполните миграции**:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

### ☁️ Heroku

1. **Установите Heroku CLI**:
   ```bash
   # Windows
   winget install --id=Heroku.HerokuCLI
   
   # macOS
   brew tap heroku/brew && brew install heroku
   ```

2. **Создайте приложение**:
   ```bash
   heroku create playandjump-app
   ```

3. **Настройте переменные окружения**:
   ```bash
   heroku config:set SECRET_KEY="your-secret-key"
   heroku config:set DEBUG="False"
   heroku config:set DATABASE_URL="postgres://..."
   ```

4. **Добавьте PostgreSQL**:
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

5. **Деплой**:
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

6. **Выполните миграции**:
   ```bash
   heroku run python manage.py migrate
   heroku run python manage.py createsuperuser
   ```

### 🚂 Railway

1. **Подключите GitHub репозиторий** на [railway.app](https://railway.app)

2. **Настройте переменные окружения** в Railway Dashboard:
   - `SECRET_KEY`
   - `DEBUG=False`
   - `DATABASE_URL` (Railway создаст автоматически)

3. **Деплой произойдет автоматически** после push в GitHub

4. **Выполните миграции**:
   ```bash
   railway run python manage.py migrate
   railway run python manage.py createsuperuser
   ```

### 🎯 Render

1. **Создайте аккаунт** на [render.com](https://render.com)

2. **Создайте новый Web Service**:
   - Подключите GitHub репозиторий
   - Build Command: `pip install -r requirements_production.txt`
   - Start Command: `gunicorn playandjump.wsgi:application`

3. **Настройте переменные окружения**:
   - `SECRET_KEY`
   - `DEBUG=False`
   - `DATABASE_URL`

4. **Добавьте PostgreSQL Database** в Render

5. **Деплой произойдет автоматически**

### 🐳 Docker (опционально)

Создайте `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements_production.txt .
RUN pip install -r requirements_production.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "playandjump.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## 🔧 Пост-деплой настройки

### 1. Создание суперпользователя
```bash
python manage.py createsuperuser
```

### 2. Настройка домена
- Добавьте ваш домен в `ALLOWED_HOSTS`
- Настройте DNS записи

### 3. SSL сертификат
- Включите HTTPS на хостинге
- Настройте редирект с HTTP на HTTPS

### 4. Мониторинг
- Настройте логирование
- Добавьте Sentry для отслеживания ошибок

## 🛠️ Устранение проблем

### Статические файлы не загружаются
```bash
python manage.py collectstatic --noinput
```

### Ошибки миграций
```bash
python manage.py makemigrations
python manage.py migrate
```

### Проблемы с базой данных
```bash
python manage.py dbshell
```

### Логи
```bash
# Просмотр логов Django
tail -f logs/django.log

# Логи хостинга (зависит от платформы)
heroku logs --tail
railway logs
```

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи
2. Убедитесь, что все переменные окружения настроены
3. Проверьте подключение к базе данных
4. Убедитесь, что статические файлы собраны 