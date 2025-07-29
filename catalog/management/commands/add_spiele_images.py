import os
import shutil
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from catalog.models import Product


class Command(BaseCommand):
    help = 'Добавляет изображения к товарам категории Spiele & Unterhaltung'

    def handle(self, *args, **options):
        # Создаем папку для изображений если её нет
        images_dir = Path(settings.MEDIA_ROOT) / 'products'
        images_dir.mkdir(parents=True, exist_ok=True)

        # Маппинг товаров и их изображений
        product_images = {
            'popcornmaschine': ['POpcornmaschine-Rastatt.jpg'],
            'fussball-darts': ['Fussball-Darts-scaled.jpg', 'Fussball-Darts-1-scaled.jpg'],
            'kickertisch': ['kregle.jpg'],  # Используем изображение кеглей как заглушку
            '4-gewinnt-xxl': ['XXL-Schach-Play-Jump.jpg'],  # Используем шахматы как заглушку
            'stockfangen': ['Dart-XXL1.jpg'],  # Используем дартс как заглушку
            'bull-rodeo': ['maxi.jpg'],  # Используем макси как заглушку
            'tor-mit-radar': ['Fussball-Billiard1.jpeg'],  # Используем футбол как заглушку
            'riesen-rutsche': ['Shooting-Combo.jpg']  # Используем комбо как заглушку
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
                        self.style.SUCCESS(f'Добавлено изображение для {product.title}')
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
            self.style.SUCCESS('Добавление изображений завершено')
        ) 