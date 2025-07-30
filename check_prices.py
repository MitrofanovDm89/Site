import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'playandjump.settings')
django.setup()

from catalog.models import Product

products = Product.objects.all()
print("Проверка цен товаров:")
print("-" * 50)

for product in products:
    print(f"{product.title}:")
    print(f"  price: {product.price}")
    print(f"  price_netto: {product.price_netto}")
    print(f"  price_brutto: {product.price_brutto}")
    print(f"  has_both_prices: {product.has_both_prices}")
    print(f"  display_price: {product.display_price}")
    print("-" * 30) 