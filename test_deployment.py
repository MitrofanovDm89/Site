#!/usr/bin/env python
"""
Скрипт для тестирования готовности проекта к деплою.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_file_exists(filepath, description):
    """Проверяет существование файла."""
    if Path(filepath).exists():
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description} - ФАЙЛ НЕ НАЙДЕН")
        return False

def check_import(module, description):
    """Проверяет возможность импорта модуля."""
    try:
        __import__(module)
        print(f"✅ {description}")
        return True
    except ImportError:
        print(f"❌ {description} - МОДУЛЬ НЕ УСТАНОВЛЕН")
        return False

def run_django_command(command, description):
    """Выполняет Django команду."""
    try:
        result = subprocess.run(
            f"python manage.py {command}",
            shell=True, 
            capture_output=True, 
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print(f"✅ {description}")
            return True
        else:
            print(f"❌ {description} - ОШИБКА")
            print(f"Ошибка: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"❌ {description} - ТАЙМАУТ")
        return False
    except Exception as e:
        print(f"❌ {description} - ИСКЛЮЧЕНИЕ: {e}")
        return False

def main():
    """Основная функция тестирования."""
    print("🔍 Тестирование готовности проекта к деплою...")
    print("=" * 50)
    
    # Проверяем, что мы в корне проекта
    if not Path("manage.py").exists():
        print("❌ Ошибка: manage.py не найден. Запустите скрипт из корня проекта.")
        sys.exit(1)
    
    tests_passed = 0
    total_tests = 0
    
    # 1. Проверка основных файлов
    print("\n📁 Проверка файлов проекта:")
    files_to_check = [
        ("manage.py", "manage.py"),
        ("requirements_production.txt", "requirements_production.txt"),
        ("playandjump/settings_production.py", "settings_production.py"),
        ("playandjump/wsgi.py", "wsgi.py"),
        ("Procfile", "Procfile (для Heroku)"),
        ("railway.json", "railway.json (для Railway)"),
        ("Dockerfile", "Dockerfile"),
        ("docker-compose.yml", "docker-compose.yml"),
        ("DEPLOYMENT.md", "DEPLOYMENT.md"),
        (".gitignore", ".gitignore"),
    ]
    
    for filepath, description in files_to_check:
        total_tests += 1
        if check_file_exists(filepath, description):
            tests_passed += 1
    
    # 2. Проверка зависимостей
    print("\n📦 Проверка зависимостей:")
    dependencies = [
        ("django", "Django"),
        ("gunicorn", "Gunicorn"),
        ("whitenoise", "WhiteNoise"),
        ("psycopg2", "psycopg2-binary"),
        ("PIL", "Pillow"),
    ]
    
    for module, description in dependencies:
        total_tests += 1
        if check_import(module, description):
            tests_passed += 1
    
    # 3. Проверка Django команд
    print("\n⚙️  Проверка Django команд:")
    django_commands = [
        ("check --deploy", "Django check --deploy"),
        ("collectstatic --dry-run", "collectstatic (dry run)"),
        ("makemigrations --check", "makemigrations --check"),
    ]
    
    for command, description in django_commands:
        total_tests += 1
        if run_django_command(command, description):
            tests_passed += 1
    
    # 4. Проверка структуры проекта
    print("\n🏗️  Проверка структуры проекта:")
    directories = [
        ("templates", "templates/"),
        ("static", "static/"),
        ("catalog", "catalog/"),
        ("main", "main/"),
        ("playandjump", "playandjump/"),
    ]
    
    for dirpath, description in directories:
        total_tests += 1
        if Path(dirpath).exists():
            print(f"✅ {description}")
            tests_passed += 1
        else:
            print(f"❌ {description} - ПАПКА НЕ НАЙДЕНА")
    
    # 5. Проверка шаблонов
    print("\n📄 Проверка шаблонов:")
    templates = [
        ("templates/base.html", "base.html"),
        ("templates/index.html", "index.html"),
        ("templates/catalog/index.html", "catalog/index.html"),
    ]
    
    for template_path, description in templates:
        total_tests += 1
        if check_file_exists(template_path, description):
            tests_passed += 1
    
    # Результаты
    print("\n" + "=" * 50)
    print(f"📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print(f"✅ Пройдено: {tests_passed}")
    print(f"❌ Провалено: {total_tests - tests_passed}")
    print(f"📈 Процент успеха: {(tests_passed/total_tests)*100:.1f}%")
    
    if tests_passed == total_tests:
        print("\n🎉 ПРОЕКТ ГОТОВ К ДЕПЛОЮ!")
        print("\n📋 Следующие шаги:")
        print("1. Настройте переменные окружения")
        print("2. Выберите хостинг (см. DEPLOYMENT.md)")
        print("3. Загрузите код на хостинг")
        print("4. Выполните миграции")
        print("5. Создайте суперпользователя")
    else:
        print("\n⚠️  ПРОЕКТ НЕ ГОТОВ К ДЕПЛОЮ!")
        print("Исправьте ошибки и запустите тест снова.")
        sys.exit(1)

if __name__ == "__main__":
    main() 