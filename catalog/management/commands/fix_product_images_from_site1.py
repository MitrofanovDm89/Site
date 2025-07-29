import os
import shutil
import requests
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from catalog.models import Product
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse
import re


class Command(BaseCommand):
    help = 'Анализирует сайт 1 и исправляет картинки товаров на нашем сайте'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Только показать что будет исправлено, не делать изменения',
        )

    def handle(self, *args, **options):
        self.stdout.write('🔍 Начинаю анализ сайта 1...')
        
        # Пути к сайту 1
        site1_path = Path(settings.BASE_DIR) / 'samples' / 'Site1'
        xml_file = site1_path / 'playampjump.WordPress.2025-07-24.xml'
        uploads_path = site1_path / 'backup_2025-07-08-1500_Play_amp_Jump_e3006729b37c-uploads' / 'uploads'
        
        if not xml_file.exists():
            self.stdout.write(self.style.ERROR(f'❌ XML файл не найден: {xml_file}'))
            return
            
        if not uploads_path.exists():
            self.stdout.write(self.style.ERROR(f'❌ Папка uploads не найдена: {uploads_path}'))
            return

        # Анализируем сайт 1
        site1_products = self.analyze_site1(xml_file, uploads_path)
        
        if not site1_products:
            self.stdout.write(self.style.ERROR('❌ Не удалось извлечь данные из сайта 1'))
            return
            
        self.stdout.write(f'✅ Найдено {len(site1_products)} товаров на сайте 1')
        
        # Проверяем наш сайт
        mismatches = self.check_our_site(site1_products)
        
        if not mismatches:
            self.stdout.write('✅ Все картинки соответствуют!')
            return
            
        self.stdout.write(f'⚠️ Найдено {len(mismatches)} несоответствий')
        
        # Исправляем несоответствия
        if not options['dry_run']:
            self.fix_mismatches(mismatches, uploads_path)
        else:
            self.show_mismatches(mismatches)

    def analyze_site1(self, xml_file, uploads_path):
        """Анализирует XML файл сайта 1 и извлекает соответствия товаров и картинок"""
        products = {}
        
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            self.stdout.write(f'📄 Анализирую XML файл: {xml_file}')
            self.stdout.write(f'📊 Найдено элементов item: {len(root.findall(".//item"))}')
            
            # Создаем словарь соответствий названий товаров и картинок
            product_image_mapping = {
                'Dschungel': 'Dschungel.jpg',
                'Fussball-Billiard': 'Fussball-Billiard.jpg', 
                'Madagaskar': 'Madagaskar.jpg',
                'Party': 'Party-2.jpg',
                'Play-Jump-Darts-XXL': 'Play-Jump-Darts-XXL-scaled.jpg',
                'Play-Jump-Huepfburg-Maxi': 'Play-Jump-Huepfburg-Maxi.jpg',
                'Play-Jump-Huepfburg-Zirkus': 'Play-Jump-Huepfburg-Zirkus.jpg',
                'Play-Jump-Polizei': 'Play-Jump-Polizei-1-scaled.jpg',
                'Play-Jump-Shooting-Combo': 'Play-Jump-Shooting-Combo-1.jpg',
                'XXL-Schach-Play-Jump': 'XXL-Schach-Play-Jump.jpg',
                'Tor mit Radar': 'tor-mit-radar.jpg',
                'Riesen Rutsche': 'riesen-rutsche.jpg',
                'Stockfangen': 'stockfangen.jpg',
                'Bull Rodeo': 'bull-rodeo.jpg',
                'Kickertisch': 'kickertisch.jpg',
                'Fußball Darts': 'fussball-darts.jpg',
                '4 gewinnt XXL': '4-gewinnt-xxl.jpg',
                'POPCORNMASCHINE': 'popcornmaschine.jpg'
            }
            
            # Ищем товары в XML и сопоставляем с картинками
            for i, item in enumerate(root.findall('.//item')):
                title_elem = item.find('title')
                if title_elem is None or title_elem.text is None:
                    continue
                    
                title = title_elem.text.strip()
                
                # Ищем соответствие в нашем словаре
                for product_name, image_name in product_image_mapping.items():
                    if product_name.lower() in title.lower():
                        products[title] = {
                            'title': title,
                            'image': f'/wp-content/uploads/{image_name}',
                            'all_images': [f'/wp-content/uploads/{image_name}']
                        }
                        self.stdout.write(f'✅ Найдено соответствие: {title} -> {image_name}')
                        break
                        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Ошибка при анализе XML: {e}'))
            
        return products

    def extract_images_from_content(self, content):
        """Извлекает URL картинок из HTML контента"""
        if not content:
            return []
            
        # Ищем img теги
        img_pattern = r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>'
        images = re.findall(img_pattern, content)
        
        # Фильтруем только локальные картинки
        local_images = []
        for img in images:
            if img.startswith('/') or not img.startswith('http'):
                local_images.append(img)
                
        return local_images

    def check_our_site(self, site1_products):
        """Проверяет наш сайт на соответствие с сайтом 1"""
        mismatches = []
        
        for product in Product.objects.all():
            # Ищем соответствующий товар на сайте 1
            site1_product = self.find_matching_product(product.title, site1_products)
            
            if site1_product:
                # Проверяем соответствие картинки
                self.stdout.write(f'🔍 Проверяю: {product.title}')
                self.stdout.write(f'   Наша картинка: {product.image}')
                self.stdout.write(f'   Картинка с сайта 1: {site1_product["image"]}')
                
                if not self.images_match(product.image, site1_product['image']):
                    self.stdout.write(f'   ❌ НЕ СООТВЕТСТВУЕТ!')
                    mismatches.append({
                        'our_product': product,
                        'site1_product': site1_product,
                        'our_image': product.image.name if product.image else None,
                        'site1_image': site1_product['image']
                    })
                else:
                    self.stdout.write(f'   ✅ Соответствует')
                    
        return mismatches

    def find_matching_product(self, our_title, site1_products):
        """Ищет соответствующий товар на сайте 1"""
        # Создаем словарь соответствий наших товаров с товарами сайта 1
        our_to_site1_mapping = {
            'Hüpfburg Dschungel': 'Dschungel',
            'Hüpfburg Madagaskar': 'Madagaskar', 
            'Hüpfburg Party': 'Party',
            'Hüpfburg Zirkus': 'Play-Jump-Huepfburg-Zirkus',
            'Hüpfburg Polizei': 'Play-Jump-Polizei',
            'HÜPFBURG MAXI': 'Play-Jump-Huepfburg-Maxi',
            'SHOOTING COMBO': 'Play-Jump-Shooting-Combo',
            'DART XXL': 'Play-Jump-Darts-XXL',
            'FUSSBALL-BILLIARD': 'Fussball-Billiard',
            'XXL SCHACH': 'XXL-Schach-Play-Jump',
            'POPCORNMASCHINE': 'POPCORNMASCHINE',
            'Fußball Darts': 'Fußball Darts',
            'Kickertisch': 'Kickertisch',
            '4 gewinnt XXL': '4 gewinnt XXL',
            'Stockfangen': 'Stockfangen',
            'Bull Rodeo': 'Bull Rodeo',
            'Tor mit Radar': 'Tor mit Radar',
            'Riesen Rutsche': 'Riesen Rutsche'
        }
        
        # Ищем соответствие
        if our_title in our_to_site1_mapping:
            site1_title = our_to_site1_mapping[our_title]
            for title, product_data in site1_products.items():
                if self.titles_similar(site1_title, title):
                    return product_data
                    
        # Если не нашли в словаре, пробуем общее сравнение
        for title, product_data in site1_products.items():
            if self.titles_similar(our_title, title):
                return product_data
        return None

    def titles_similar(self, title1, title2):
        """Проверяет схожесть названий товаров"""
        # Нормализуем названия
        t1 = title1.lower().strip()
        t2 = title2.lower().strip()
        
        # Простое сравнение
        return t1 == t2 or t1 in t2 or t2 in t1

    def images_match(self, our_image, site1_image):
        """Проверяет соответствие картинок"""
        if not our_image:
            return False
            
        our_filename = os.path.basename(str(our_image))
        site1_filename = os.path.basename(site1_image)
        
        # Нормализуем имена файлов для сравнения
        our_normalized = our_filename.lower().replace('_', '').replace('-', '').replace('.', '')
        site1_normalized = site1_filename.lower().replace('_', '').replace('-', '').replace('.', '')
        
        # Проверяем точное соответствие по ключевым словам
        # Картинка должна содержать точное название товара
        if 'dschungel' in our_normalized and 'dschungel' in site1_normalized:
            # Проверяем что это именно Dschungel, а не huepfburg-dschungel
            if 'huepfburg' in our_normalized and not our_normalized.endswith('dschungel'):
                return False
            return True
        elif 'madagaskar' in our_normalized and 'madagaskar' in site1_normalized:
            if 'huepfburg' in our_normalized and not our_normalized.endswith('madagaskar'):
                return False
            return True
        elif 'party' in our_normalized and 'party' in site1_normalized:
            if 'huepfburg' in our_normalized and not our_normalized.endswith('party'):
                return False
            return True
        elif 'fussball' in our_normalized and 'fussball' in site1_normalized:
            return True
        elif 'billiard' in our_normalized and 'billiard' in site1_normalized:
            return True
            
        # Если не нашли соответствие, считаем что картинки не совпадают
        return False

    def show_mismatches(self, mismatches):
        """Показывает найденные несоответствия"""
        self.stdout.write('\n📋 Найденные несоответствия:')
        for i, mismatch in enumerate(mismatches, 1):
            self.stdout.write(f'\n{i}. Товар: {mismatch["our_product"].title}')
            self.stdout.write(f'   Наша картинка: {mismatch["our_image"]}')
            self.stdout.write(f'   Картинка с сайта 1: {mismatch["site1_image"]}')

    def fix_mismatches(self, mismatches, uploads_path):
        """Исправляет несоответствия картинок"""
        self.stdout.write('\n🔧 Исправляю несоответствия...')
        
        for mismatch in mismatches:
            try:
                self.fix_single_product(mismatch, uploads_path)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Ошибка при исправлении {mismatch["our_product"].title}: {e}'))

    def fix_single_product(self, mismatch, uploads_path):
        """Исправляет картинку одного товара"""
        product = mismatch['our_product']
        site1_image = mismatch['site1_image']
        
        self.stdout.write(f'🔄 Исправляю картинку для товара: {product.title}')
        
        # Ищем картинку в папке uploads сайта 1
        image_path = self.find_image_in_uploads(site1_image, uploads_path)
        
        if not image_path:
            self.stdout.write(self.style.WARNING(f'⚠️ Картинка не найдена: {site1_image}'))
            return
            
        # Копируем картинку
        self.copy_image_to_our_site(image_path, product)
        
        self.stdout.write(f'✅ Картинка исправлена для товара: {product.title}')

    def find_image_in_uploads(self, image_url, uploads_path):
        """Ищет картинку в папке uploads сайта 1"""
        # Извлекаем имя файла из URL
        if image_url.startswith('/'):
            image_url = image_url[1:]
            
        filename = image_url.split('/')[-1]
        
        # Ищем в статических файлах
        static_products_path = Path(settings.BASE_DIR) / 'static' / 'images' / 'products'
        if static_products_path.exists():
            for file_path in static_products_path.iterdir():
                if file_path.is_file() and file_path.name == filename:
                    return file_path
                    
        # Ищем во всех папках uploads рекурсивно
        for root, dirs, files in os.walk(uploads_path):
            for file in files:
                # Точное совпадение
                if file == filename:
                    return Path(root) / file
                    
                # Ищем похожие файлы по ключевым словам
                if self.files_match_by_keywords(filename, file):
                    return Path(root) / file
                    
        return None
        
    def files_match_by_keywords(self, target_filename, actual_filename):
        """Проверяет соответствие файлов по ключевым словам"""
        # Нормализуем имена файлов
        target = target_filename.lower().replace('_', '').replace('-', '').replace('.', '')
        actual = actual_filename.lower().replace('_', '').replace('-', '').replace('.', '')
        
        # Словарь соответствий ключевых слов
        keyword_mapping = {
            'tor-mit-radar': ['tor-mit-radar', 'tor-mit-radar-1', 'tor-mit-radar-2'],
            'kickertisch': ['kickertisch', 'kickertisch2'],
            'bull-rodeo': ['bull-rodeo', 'bull-riding'],
            'stockfangen': ['stockfangen', 'stockfangen2'],
            'riesen-rutsche': ['rutsche', 'rutsche-1', 'rutsche-2', 'rutsche-play-jump'],
            '4-gewinnt-xxl': ['4-gewinnt-xxl', 'xxl-schach', 'xxl-schach-play-jump', 'xxlschachplayjump'],
            'popcornmaschine': ['popcornmaschine', 'popcorn', 'zuckerwattemaschine']
        }
        
        # Проверяем соответствие по ключевым словам
        for target_key, actual_keys in keyword_mapping.items():
            if target_key in target:
                for actual_key in actual_keys:
                    if actual_key in actual:
                        return True
                        
        # Дополнительная проверка для XXL Schach
        if '4-gewinnt-xxl' in target or '4gewinntxxl' in target:
            if 'xxl' in actual and 'schach' in actual:
                return True
                
        return False

    def copy_image_to_our_site(self, source_path, product):
        """Копирует картинку на наш сайт"""
        # Создаем папку для картинок товаров
        media_products_path = Path(settings.MEDIA_ROOT) / 'products'
        media_products_path.mkdir(exist_ok=True)
        
        # Генерируем имя файла на основе оригинального
        original_filename = source_path.name
        filename = f"{product.slug}_{original_filename}"
        dest_path = media_products_path / filename
        
        # Копируем файл
        shutil.copy2(source_path, dest_path)
        
        # Обновляем модель товара
        product.image = f'products/{filename}'
        product.save()
        
        self.stdout.write(f'📁 Скопирован файл: {source_path.name} -> {filename}') 