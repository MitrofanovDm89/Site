# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements и устанавливаем Python зависимости
COPY requirements_production.txt .
RUN pip install --no-cache-dir -r requirements_production.txt

# Копируем код проекта
COPY . .

# Создаем папку для логов
RUN mkdir -p logs

# Собираем статические файлы
RUN python manage.py collectstatic --noinput

# Создаем пользователя для безопасности
RUN useradd -m -u 1000 django && chown -R django:django /app
USER django

# Открываем порт
EXPOSE 8000

# Запускаем приложение
CMD ["gunicorn", "playandjump.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"] 