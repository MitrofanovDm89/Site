from django.core.management.base import BaseCommand
from django.core.files import File
from catalog.models import Product
import os
import shutil
from pathlib import Path


class Command(BaseCommand):
    help = 'Fix correct image mapping for each product'

    def handle(self, *args, **options):
        self.stdout.write('Fixing correct image mapping...')
        
        # Source and destination paths
        source_path = Path('samples/Site2/media/products')
        dest_path = Path('static/images/products')
        
        # Create destination directory
        dest_path.mkdir(parents=True, exist_ok=True)
        
        # CORRECT image mappings - based on actual product names
        image_mappings = {
            # Hüpfburgen - правильные изображения
            'hupfburg-zirkus': 'zirkus.jpg',  # Hüpfburg Zirkus
            'hupfburg-dschungel': 'Dschungel.jpg',  # Hüpfburg Dschungel  
            'hupfburg-polizei': 'HUePFBURG-POLIZEI.jpg',  # Hüpfburg Polizei
            'hupfburg-madagaskar': 'Madagaskar.jpg',  # Hüpfburg Madagaskar
            'hupfburg-party': 'Party-2.jpg',  # Hüpfburg Party
            'hupfburg-maxi': 'maxi.jpg',  # HÜPFBURG MAXI
            'shooting-combo': 'Shooting-Combo.jpg',  # SHOOTING COMBO
            'hupfburg-delphin': 'Delphin.jpg',  # Hüpfburg Delphin
            
            # Spiele & Unterhaltung - правильные изображения
            'dart-xxl': 'Dart-XXL1.jpg',  # DART XXL
            'fussball-billiard': 'Fussball-Billiard.jpg',  # FUSSBALL-BILLIARD
            'xxl-schach': 'XXL-Schach-Play-Jump.jpg',  # XXL SCHACH
            'fussball-darts': 'Fussball-Darts-scaled.jpg',  # Fußball Darts
            'stockfangen': 'dart.jpg',  # Stockfangen
            'bull-rodeo': 'maxi.jpg',  # Bull Rodeo
            
            # Zubehör & Catering - правильные изображения
            'popcornmaschine': 'POpcornmaschine-Rastatt.jpg',  # POPCORNMASCHINE
            'tor-mit-radar': 'Fussball-Darts-1-scaled.jpg',  # Tor mit Radar
        }
        
        # Clear existing images first
        for file in dest_path.glob('*.jpg'):
            file.unlink()
        for file in dest_path.glob('*.jpeg'):
            file.unlink()
        for file in dest_path.glob('*.png'):
            file.unlink()
        
        # Copy images and update products
        for slug, filename in image_mappings.items():
            source_file = source_path / filename
            dest_file = dest_path / filename
            
            try:
                # Copy the image file
                if source_file.exists():
                    shutil.copy2(source_file, dest_file)
                    self.stdout.write(f'  Copied: {filename} -> {slug}')
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
            self.style.SUCCESS('Successfully fixed correct image mapping!')
        ) 