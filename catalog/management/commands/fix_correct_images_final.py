from django.core.management.base import BaseCommand
from django.core.files import File
from catalog.models import Product
import os
import shutil
from pathlib import Path


class Command(BaseCommand):
    help = 'Fix correct image mapping for each product with proper Site 2 images'

    def handle(self, *args, **options):
        self.stdout.write('Fixing correct image mapping with proper Site 2 images...')
        
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
        
        # CORRECT mapping based on Site 2 file analysis
        image_mappings = {
            'huepfburg-zirkus': 'Play-Jump-Huepfburg-Zirkus.jpg',  # Main Zirkus image
            'huepfburg-dschungel': 'Dschungel.jpg',  # Main Dschungel image
            'huepfburg-polizei': 'Play-Jump-Polizei-1-scaled.jpg',  # Main Polizei image
            'huepfburg-madagaskar': 'Madagaskar.jpg',  # Main Madagaskar image
            'huepfburg-party': 'Party-2.jpg',  # Main Party image
            'huepfburg-maxi': 'Play-Jump-Huepfburg-Maxi.jpg',  # Main Maxi image
            'shooting-combo': 'Play-Jump-Shooting-Combo-1.jpg',  # Main Shooting Combo image
            'dart-xxl': 'Play-Jump-Darts-XXL-scaled.jpg',  # Main Dart XXL image
            'fussball-billiard': 'Fussball-Billiard.jpg',  # Main Fussball Billiard image
            'xxl-schach': 'XXL-Schach-Play-Jump.jpg'  # Main XXL Schach image
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