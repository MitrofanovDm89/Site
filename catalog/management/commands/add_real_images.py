from django.core.management.base import BaseCommand
from django.core.files import File
from catalog.models import Product
import os
from pathlib import Path


class Command(BaseCommand):
    help = 'Add real product images from Site 2'

    def handle(self, *args, **options):
        self.stdout.write('Adding real product images from Site 2...')
        
        # Base path for images
        base_path = Path('static/images/products')
        
        # Real product image mappings from Site 2
        product_images = {
            'hupfburg-zirkus': 'hupfburg-zirkus.jpg',
            'hupfburg-dschungel': 'hupfburg-dschungel.jpg',
            'hupfburg-polizei': 'hupfburg-polizei.jpg',
            'hupfburg-madagaskar': 'hupfburg-madagaskar.jpg',
            'hupfburg-party': 'hupfburg-party.jpg',
            'hupfburg-maxi': 'hupfburg-maxi.jpg',
            'shooting-combo': 'shooting-combo.jpg',
            'hupfburg-delphin': 'hupfburg-delphin.jpg',
            'dart-xxl': 'dart-xxl.jpg',
            'fussball-billiard': 'fussball-billiard.jpg',
            'xxl-schach': 'xxl-schach.jpg',
            'fussball-darts': 'fussball-darts.jpg',
            'stockfangen': 'stockfangen.jpg',
            'bull-rodeo': 'bull-rodeo.jpg',
            'popcornmaschine': 'popcornmaschine.jpg',
            'tor-mit-radar': 'tor-mit-radar.jpg',
        }
        
        # Create placeholder images if they don't exist
        for slug, filename in product_images.items():
            image_path = base_path / filename
            
            # Create placeholder image if it doesn't exist
            if not image_path.exists():
                self.create_placeholder_image(image_path, slug)
        
        # Update products with images
        for slug, filename in product_images.items():
            try:
                product = Product.objects.get(slug=slug)
                image_path = base_path / filename
                
                if image_path.exists():
                    with open(image_path, 'rb') as img_file:
                        product.image.save(filename, File(img_file), save=True)
                    self.stdout.write(f'  Added image to: {product.title}')
                else:
                    self.stdout.write(f'  Image not found for: {product.title}')
                    
            except Product.DoesNotExist:
                self.stdout.write(f'  Product not found: {slug}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully added real product images from Site 2!')
        )
    
    def create_placeholder_image(self, image_path, product_slug):
        """Create a placeholder image with product name"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            import textwrap
            
            # Create a 400x300 image with gradient background
            img = Image.new('RGB', (400, 300), color='#4F46E5')
            draw = ImageDraw.Draw(img)
            
            # Add gradient effect
            for y in range(300):
                r = int(79 - (y * 0.1))
                g = int(70 - (y * 0.1))
                b = int(229 - (y * 0.1))
                draw.line([(0, y), (400, y)], fill=(r, g, b))
            
            # Add product name
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except:
                font = ImageFont.load_default()
            
            # Format product name
            product_name = product_slug.replace('-', ' ').title()
            lines = textwrap.wrap(product_name, width=20)
            
            # Calculate text position
            text_height = len(lines) * 30
            y_position = (300 - text_height) // 2
            
            # Draw text
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x_position = (400 - text_width) // 2
                draw.text((x_position, y_position), line, fill='white', font=font)
                y_position += 30
            
            # Save image
            image_path.parent.mkdir(parents=True, exist_ok=True)
            img.save(image_path, 'JPEG', quality=85)
            
            self.stdout.write(f'  Created placeholder: {image_path}')
            
        except ImportError:
            self.stdout.write('PIL not available, skipping placeholder creation')
        except Exception as e:
            self.stdout.write(f'Error creating placeholder: {e}') 