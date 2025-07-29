from django.core.management.base import BaseCommand
from catalog.models import Category, Product
from decimal import Decimal


class Command(BaseCommand):
    help = 'Добавляет товары в категорию Spiele & Unterhaltung'

    def handle(self, *args, **options):
        # Получаем категорию
        category, created = Category.objects.get_or_create(
            name='Spiele & Unterhaltung',
            defaults={
                'slug': 'spiele-unterhaltung',
                'description': 'Spiele und Unterhaltungsgeräte für alle Altersgruppen'
            }
        )

        # Список товаров для добавления
        products_data = [
            {
                'title': 'POPCORNMASCHINE',
                'slug': 'popcornmaschine',
                'description': 'Nicht nur Kinder lieben Popcorn. Frisch schmeckt natürlich am besten. Süß oder salzig entscheiden Sie selbst. Leistung: 1.600 Watt, Arbeitsleistung: 5 kg/h, 16 L/h, Topfdurchmesser: Oben: 18,5 cm, Topfbeschichtung: Teflon, mobil einsetzbar, 50g Pocpornmais und 50 ml Öl (Kokos- Palm-Sonnenblumenöl) und 50 g Zucker für ein Portion',
                'price': Decimal('79.00')
            },
            {
                'title': 'Fußball Darts',
                'slug': 'fussball-darts',
                'description': 'Jeder kann schießen, aber wer trifft die Mitte? Größe: 3.0m x 1.2m x 3.0m, Zubehör: elektrische Pumpe, spezielle Bälle, Unterlage Plane, Kabel 25 M',
                'price': Decimal('99.00')
            },
            {
                'title': 'Kickertisch',
                'slug': 'kickertisch',
                'description': 'Jeder kann kicken, aber wer schießt schneller? Außenmaße: L 142 cm x B 73,5 cm x H 91 cm, Spielfeldmaße: L 120 cm x B 68 cm, Wandstärke: 2,8 cm, Material: MDF, Höhe: 91 cm - 95 cm, Gesamtgewicht: ca. 90 kg',
                'price': Decimal('79.00')
            },
            {
                'title': '4 gewinnt XXL',
                'slug': '4-gewinnt-xxl',
                'description': 'XXL Version des klassischen 4 gewinnt Spiels. Perfekt für Events und Partys. Großes Spielbrett für maximalen Spaß.',
                'price': Decimal('89.00')
            },
            {
                'title': 'Stockfangen',
                'slug': 'stockfangen',
                'description': 'Stockfangen ist ein einfaches und unterhaltsames Spiel, das im Freien oder in größeren Innenräumen gespielt werden kann. Es fördert Bewegung, Koordination und Spaß. Maße: 2,5m x 1,4m, Gewicht: 15 kg, Aufbauzeit ca. 10 Minuten, Max. Größe Spieler 1,8m, Benötigte Personen: 1, Zubehör: Bravo OV6 Gebläse = 1,3 kg',
                'price': Decimal('99.00')
            },
            {
                'title': 'Bull Rodeo',
                'slug': 'bull-rodeo',
                'description': 'Ein großer Spaß für Kinder und Erwachsene. Testen Sie Ihr Gleichgewicht und Ihre Beweglichkeit! Maße: 4,5x5x4 m (LxBxH), Gewicht: ca.350 kg, Kapazität: 1 Kinder, Aufbauzeit: 20 Minuten, Zubehör: elektrisches Gebläse 1,1 kW, Unterlegeplane, Kabeltrommel25 m',
                'price': Decimal('425.00')
            },
            {
                'title': 'Tor mit Radar',
                'slug': 'tor-mit-radar',
                'description': 'Ein "Tor mit Radar" ist eine moderne Variante eines Fußballtores, das mit Radar- oder Sensortechnologie ausgestattet ist, um Torschüsse zu erkennen und zu verfolgen. Die Messung erfolgt hinter dem Tor, das von einem Netz umgeben ist. Gewicht ca. 80 kg, Größe: 4m x 5m, Radar, Strombetrieben, Unteregplane, Gebläse, Verlängerungskabel',
                'price': Decimal('200.00')
            },
            {
                'title': 'Riesen Rutsche',
                'slug': 'riesen-rutsche',
                'description': 'Eine aufblasbare Rutsche ist eine unterhaltsame Attraktion, die oft bei Veranstaltungen im Freien, wie Geburtstagsfeiern, Festivals oder anderen Events, zu finden ist. Sie besteht aus einem aufblasbaren Material, das in der Regel aus PVC besteht und mit Luft gefüllt wird, um eine große, rutschige Oberfläche zu schaffen.',
                'price': Decimal('150.00')
            }
        ]

        # Добавляем товары
        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                slug=product_data['slug'],
                defaults={
                    'title': product_data['title'],
                    'description': product_data['description'],
                    'price': product_data['price'],
                    'category': category,
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Создан товар: {product.title}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Товар уже существует: {product.title}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Добавлено {len(products_data)} товаров в категорию {category.name}')
        ) 