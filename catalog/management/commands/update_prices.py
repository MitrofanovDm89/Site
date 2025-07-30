from django.core.management.base import BaseCommand
from catalog.models import Product


class Command(BaseCommand):
    help = 'Обновляет цены товаров с брутто и нетто значениями'

    def handle(self, *args, **options):
        # Обновляем цены для товаров
        products_to_update = [
            # Hüpfburgen
            {'slug': 'huepfburg-zirkus', 'price_netto': 83.19, 'price_brutto': 99.00},
            {'slug': 'huepfburg-dschungel', 'price_netto': 109.24, 'price_brutto': 130.00},
            {'slug': 'huepfburg-polizei', 'price_netto': 126.05, 'price_brutto': 150.00},
            {'slug': 'huepfburg-madagaskar', 'price_netto': 126.05, 'price_brutto': 150.00},
            {'slug': 'huepfburg-party', 'price_netto': 184.87, 'price_brutto': 220.00},
            {'slug': 'huepfburg-maxi', 'price_netto': 210.08, 'price_brutto': 250.00},
            
            # Spiele & Unterhaltung
            {'slug': 'shooting-combo', 'price_netto': 252.10, 'price_brutto': 300.00},
            {'slug': 'dart-xxl', 'price_netto': 83.19, 'price_brutto': 99.00},
            {'slug': 'fussball-billiard', 'price_netto': 83.19, 'price_brutto': 99.00},
            
            # Vermietung
            {'slug': 'event-betreuung', 'price_netto': 252.10, 'price_brutto': 300.00},
            {'slug': 'fussball-darts', 'price_netto': 83.19, 'price_brutto': 99.00},
            {'slug': 'kinderbetreuung', 'price_netto': 210.08, 'price_brutto': 250.00},
            {'slug': 'animation', 'price_netto': 184.87, 'price_brutto': 220.00},
            {'slug': 'dekorationsservice', 'price_netto': 126.05, 'price_brutto': 150.00},
            {'slug': 'catering-service', 'price_netto': 252.10, 'price_brutto': 300.00},
            {'slug': 'fotograf', 'price_netto': 210.08, 'price_brutto': 250.00},
            {'slug': 'dj-service', 'price_netto': 184.87, 'price_brutto': 220.00},
            {'slug': 'transport-service', 'price_netto': 252.10, 'price_brutto': 300.00},
        ]
        
        updated_count = 0
        for product_data in products_to_update:
            try:
                product = Product.objects.get(slug=product_data['slug'])
                product.price_netto = product_data['price_netto']
                product.price_brutto = product_data['price_brutto']
                product.save()
                updated_count += 1
                self.stdout.write(f"Обновлен: {product.title}")
            except Product.DoesNotExist:
                self.stdout.write(f"Товар не найден: {product_data['slug']}")
        
        self.stdout.write(
            self.style.SUCCESS(f'Успешно обновлено {updated_count} товаров')
        ) 