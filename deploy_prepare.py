#!/usr/bin/env python
"""
Скрипт для подготовки проекта к деплою на хостинг.
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Выполняет команду и выводит результат."""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} выполнено успешно")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при {description}: {e}")
        print(f"Вывод: {e.stdout}")
        print(f"Ошибка: {e.stderr}")
        return False

def main():
    """Основная функция подготовки к деплою."""
    print("🚀 Подготовка проекта Play & Jump к деплою...")
    
    # Проверяем, что мы в корне проекта
    if not Path("manage.py").exists():
        print("❌ Ошибка: manage.py не найден. Запустите скрипт из корня проекта.")
        sys.exit(1)
    
    # 1. Собираем статические файлы
    if not run_command("python manage.py collectstatic --noinput", "Сбор статических файлов"):
        sys.exit(1)
    
    # 2. Проверяем миграции
    if not run_command("python manage.py makemigrations --check", "Проверка миграций"):
        print("⚠️  Внимание: есть несохраненные миграции")
    
    # 3. Создаем папку для логов
    logs_dir = Path("logs")
    if not logs_dir.exists():
        logs_dir.mkdir()
        print("✅ Создана папка logs")
    
    # 4. Проверяем .gitignore
    gitignore_path = Path(".gitignore")
    if gitignore_path.exists():
        print("✅ .gitignore найден")
    else:
        print("⚠️  .gitignore не найден")
    
    # 5. Проверяем requirements
    requirements_path = Path("requirements_production.txt")
    if requirements_path.exists():
        print("✅ requirements_production.txt найден")
    else:
        print("⚠️  requirements_production.txt не найден")
    
    # 6. Проверяем production settings
    settings_prod_path = Path("playandjump/settings_production.py")
    if settings_prod_path.exists():
        print("✅ settings_production.py найден")
    else:
        print("⚠️  settings_production.py не найден")
    
    print("\n🎉 Подготовка к деплою завершена!")
    print("\n📋 Следующие шаги:")
    print("1. Настройте переменные окружения на хостинге")
    print("2. Загрузите код на хостинг")
    print("3. Выполните миграции: python manage.py migrate")
    print("4. Создайте суперпользователя: python manage.py createsuperuser")
    print("5. Настройте домен и SSL")

if __name__ == "__main__":
    main() 