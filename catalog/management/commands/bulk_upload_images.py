from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from django.core.files.uploadedfile import UploadedFile
from catalog.models import Product, ProductImage
import os
import glob
from pathlib import Path
from django.db import models


class Command(BaseCommand):
    help = 'Массовая загрузка изображений в продукт из папки'

    def add_arguments(self, parser):
        parser.add_argument(
            'product_id',
            type=int,
            help='ID продукта для загрузки изображений'
        )
        parser.add_argument(
            'folder_path',
            type=str,
            help='Путь к папке с изображениями'
        )
        parser.add_argument(
            '--order',
            type=int,
            default=1,
            help='Начальный порядок для изображений (по умолчанию 1)'
        )
        parser.add_argument(
            '--extensions',
            type=str,
            default='jpg,jpeg,png,gif,webp',
            help='Расширения файлов для загрузки (через запятую)'
        )

    def handle(self, *args, **options):
        product_id = options['product_id']
        folder_path = options['folder_path']
        start_order = options['order']
        extensions = options['extensions'].split(',')

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise CommandError(f'Продукт с ID {product_id} не найден')

        if not os.path.exists(folder_path):
            raise CommandError(f'Папка {folder_path} не существует')

        if not os.path.isdir(folder_path):
            raise CommandError(f'{folder_path} не является папкой')

        # Получаем список файлов с указанными расширениями
        image_files = []
        for ext in extensions:
            ext = ext.strip().lower()
            pattern = os.path.join(folder_path, f'*.{ext}')
            image_files.extend(glob.glob(pattern))
            # Также ищем файлы с заглавными расширениями
            pattern = os.path.join(folder_path, f'*.{ext.upper()}')
            image_files.extend(glob.glob(pattern))

        if not image_files:
            self.stdout.write(
                self.style.WARNING(
                    f'В папке {folder_path} не найдено изображений с расширениями: {extensions}'
                )
            )
            return

        # Сортируем файлы по имени
        image_files.sort()

        # Получаем текущий максимальный порядок
        current_max_order = ProductImage.objects.filter(product=product).aggregate(
            max_order=models.Max('order')
        )['max_order'] or 0

        uploaded_count = 0
        for i, image_path in enumerate(image_files):
            try:
                # Создаем имя файла
                filename = os.path.basename(image_path)
                
                # Проверяем, не существует ли уже изображение с таким именем
                if ProductImage.objects.filter(product=product, image__endswith=filename).exists():
                    self.stdout.write(
                        self.style.WARNING(f'Изображение {filename} уже существует, пропускаем')
                    )
                    continue

                # Открываем файл
                with open(image_path, 'rb') as f:
                    # Создаем UploadedFile
                    uploaded_file = UploadedFile(
                        file=File(f),
                        name=filename,
                        content_type='image/jpeg'  # Можно улучшить определение типа
                    )

                    # Создаем ProductImage
                    product_image = ProductImage(
                        product=product,
                        image=uploaded_file,
                        alt_text=f'{product.title} - {filename}',
                        order=current_max_order + start_order + i
                    )
                    product_image.save()
                    
                    uploaded_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Загружено: {filename}')
                    )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Ошибка при загрузке {image_path}: {e}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Готово! Загружено {uploaded_count} изображений в продукт "{product.title}"'
            )
        )
