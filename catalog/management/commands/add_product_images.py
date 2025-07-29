from django.core.management.base import BaseCommand
from django.core.files import File
from catalog.models import Product
import os
from pathlib import Path


class Command(BaseCommand):
    help = 'Add real product images from static/images/products/'

    def handle(self, *args, **options):
        self.stdout.write('Adding product images...')
        
        # Base path for images
        base_path = Path('static/images/products')
        
        # Product image mappings
        product_images = {
            'prinzessin-hupfburg-magical-castle': 'princess-castle.jpg',
            'piraten-hupfburg-adventure-island': 'pirate-island.jpg',
            'dinosaurier-hupfburg-jurassic-world': 'dinosaur-world.jpg',
            'jungle-safari-hupfburg-wild-africa': 'safari-jungle.jpg',
            'superhelden-hupfburg-hero-city': 'superhero-city.jpg',
            'eiszeit-hupfburg-frozen-world': 'frozen-world.jpg',
            'riesen-jenga-xxl-tower-master': 'giant-jenga.jpg',
            'riesen-4-gewinn-connect-four-pro': 'giant-connect4.jpg',
            'riesen-schach-chess-master': 'giant-chess.jpg',
            'riesen-memory-brain-trainer': 'giant-memory.jpg',
            'riesen-domino-domino-master': 'giant-domino.jpg',
            'riesen-twister-twister-pro': 'giant-twister.jpg',
            'karaoke-anlage-star-voice-pro': 'karaoke-system.jpg',
            'gaming-station-game-zone-pro': 'gaming-station.jpg',
            'fotobox-photo-booth-deluxe': 'photo-booth.jpg',
            'dj-equipment-mix-master-pro': 'dj-equipment.jpg',
            'virtual-reality-station-vr-world': 'vr-station.jpg',
            'laser-tag-arena-battle-zone': 'laser-tag.jpg',
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
            self.style.SUCCESS('Successfully added product images!')
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