from django.core.management.base import BaseCommand
from django.core.files import File
from catalog.models import Product
import os
import shutil
from pathlib import Path


class Command(BaseCommand):
    help = 'Copy real product images from Site 2 with correct mapping'

    def handle(self, *args, **options):
        self.stdout.write('Copying real product images from Site 2...')
        
        source_path = Path('samples/Site2/media/products')
        dest_path = Path('static/images/products')
        dest_path.mkdir(parents=True, exist_ok=True)
        
        # Clear existing images first
        for file in dest_path.glob('*.jpg'):
            file.unlink()
        for file in dest_path.glob('*.jpeg'):
            file.unlink()
        for file in dest_path.glob('*.png'):
            file.unlink()
        
        # Exact mapping based on Site 2 data
        image_mappings = {
            'huepfburg-zirkus': 'zirkus.jpg',
            'huepfburg-dschungel': 'Dschungel.jpg',
            'huepfburg-polizei': 'HUePFBURG-POLIZEI.jpg',
            'huepfburg-madagaskar': 'Madagaskar.jpg',
            'huepfburg-party': 'Party-2.jpg',
            'huepfburg-maxi': 'maxi.jpg',
            'shooting-combo': 'Shooting-Combo.jpg',
            'dart-xxl': 'Dart-XXL1.jpg',
            'fussball-billiard': 'Fussball-Billiard.jpg',
            'xxl-schach': 'XXL-Schach-Play-Jump.jpg'
        }
        
        copied_count = 0
        for product_slug, image_filename in image_mappings.items():
            try:
                # Find the product
                product = Product.objects.get(slug=product_slug)
                
                # Check if source image exists
                source_image = source_path / image_filename
                if not source_image.exists():
                    self.stdout.write(f'  Warning: Source image not found: {image_filename}')
                    continue
                
                # Copy image to destination
                dest_image = dest_path / image_filename
                shutil.copy2(source_image, dest_image)
                
                # Update product with image
                with open(dest_image, 'rb') as f:
                    product.image.save(image_filename, File(f), save=True)
                
                self.stdout.write(f'  Copied: {image_filename} -> {product.title}')
                copied_count += 1
                
            except Product.DoesNotExist:
                self.stdout.write(f'  Error: Product not found: {product_slug}')
            except Exception as e:
                self.stdout.write(f'  Error copying {image_filename}: {str(e)}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully copied {copied_count} images from Site 2!')
        ) 