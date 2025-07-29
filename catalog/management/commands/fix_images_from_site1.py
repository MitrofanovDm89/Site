import os
import shutil
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from catalog.models import Product


class Command(BaseCommand):
    help = 'Исправляет изображения на основе скринов с сайта 1'

    def handle(self, *args, **options):
        # Создаем папку для изображений если её нет
        images_dir = Path(settings.MEDIA_ROOT) / 'products'
        images_dir.mkdir(parents=True, exist_ok=True)

        # Правильный маппинг на основе скринов с сайта 1
        product_images = {
            # Исправляем на основе скринов
            '4-gewinnt-xxl': ['4-x-gewinnt-scaled.jpeg'],  # Правильная игра 4 в ряд
            'stockfangen': ['Stockfangen.jpeg'],  # Зеленая конструкция с фермерской тематикой
            'tor-mit-radar': ['Tor-mit-Radar.jpg'],  # Арка с табло
            'fussball-billiard': ['Fussball-Billiard-Rastatt-scaled.jpg'],  # Футбольный бильярд
            
            # Остальные товары оставляем как есть
            'popcornmaschine': ['POpcornmaschine-Rastatt.jpg'],
            'fussball-darts': ['Fussball-Darts-scaled.jpg'],
            'kickertisch': ['kregle.jpg'],
            'bull-rodeo': ['maxi.jpg'],
            'riesen-rutsche': ['Shooting-Combo.jpg'],
            'dart-xxl': ['Dart-XXL1.jpg'],
            'xxl-schach': ['XXL-Schach-Play-Jump.jpg']
        }

        # Источник изображений
        source_dir = Path('samples/Site2/media/products')

        for slug, image_files in product_images.items():
            try:
                product = Product.objects.get(slug=slug)
                
                # Берем первое изображение из списка
                source_image = source_dir / image_files[0]
                
                if source_image.exists():
                    # Копируем изображение
                    dest_image = images_dir / f"{slug}.jpg"
                    shutil.copy2(source_image, dest_image)
                    
                    # Обновляем товар
                    product.image = f'products/{slug}.jpg'
                    product.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'Исправлено изображение для {product.title}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Изображение не найдено: {source_image}')
                    )
                    
            except Product.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Товар не найден: {slug}')
                )

        self.stdout.write(
            self.style.SUCCESS('Исправление изображений на основе сайта 1 завершено')
        ) 