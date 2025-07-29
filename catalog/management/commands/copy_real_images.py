from django.core.management.base import BaseCommand
from django.core.files import File
from catalog.models import Product
import os
import shutil
from pathlib import Path


class Command(BaseCommand):
    help = 'Copy real product images from Site 2'

    def handle(self, *args, **options):
        self.stdout.write('Copying real product images from Site 2...')
        
        # Source and destination paths
        source_path = Path('samples/Site2/media/products')
        dest_path = Path('static/images/products')
        
        # Create destination directory
        dest_path.mkdir(parents=True, exist_ok=True)
        
        # Real image mappings from Site 2
        image_mappings = {
            'hupfburg-zirkus': 'zirkus.jpg',
            'hupfburg-dschungel': 'Dschungel.jpg',
            'hupfburg-polizei': 'Polizei-Bounder.jpeg',
            'hupfburg-madagaskar': 'Party-1.jpg',
            'hupfburg-party': 'Party-2.jpg',
            'hupfburg-maxi': 'maxi.jpg',
            'shooting-combo': 'Shooting-Combo.jpg',
            'hupfburg-delphin': 'Party-.jpg',
            'dart-xxl': 'Dart-XXL1.jpg',
            'fussball-billiard': 'Fussball-Billiard.jpg',
            'xxl-schach': 'XXL-Schach-Play-Jump.jpg',
            'fussball-darts': 'Fussball-Darts-scaled.jpg',
            'stockfangen': 'dart.jpg',
            'bull-rodeo': 'maxi.jpg',
            'popcornmaschine': 'POpcornmaschine-Rastatt.jpg',
            'tor-mit-radar': 'Fussball-Darts-1-scaled.jpg',
        }
        
        # Copy images and update products
        for slug, filename in image_mappings.items():
            source_file = source_path / filename
            dest_file = dest_path / filename
            
            try:
                # Copy the image file
                if source_file.exists():
                    shutil.copy2(source_file, dest_file)
                    self.stdout.write(f'  Copied: {filename}')
                else:
                    self.stdout.write(f'  Source file not found: {filename}')
                    continue
                
                # Update product with real image
                product = Product.objects.get(slug=slug)
                with open(dest_file, 'rb') as img_file:
                    product.image.save(filename, File(img_file), save=True)
                self.stdout.write(f'  Updated product: {product.title}')
                    
            except Product.DoesNotExist:
                self.stdout.write(f'  Product not found: {slug}')
            except Exception as e:
                self.stdout.write(f'  Error processing {filename}: {e}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully copied real images from Site 2!')
        ) 