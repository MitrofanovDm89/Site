from django.core.management.base import BaseCommand
from django.utils.text import slugify
from catalog.models import Category, Product, Service
from decimal import Decimal
from django.utils import timezone


class Command(BaseCommand):
    help = 'Import real data from Site 2 with correct mapping'

    def handle(self, *args, **options):
        self.stdout.write('Importing real data from Site 2...')
        
        # Clear existing data
        Product.objects.all().delete()
        Category.objects.all().delete()
        
        # Create Categories based on Site 2
        categories_data = [
            {
                'name': 'Hüpfburgen',
                'description': 'Große Auswahl an sicheren und hochwertigen Hüpfburgen für Kinderfeste und Events. Alle unsere Hüpfburgen sind TÜV-geprüft und entsprechen den höchsten Sicherheitsstandards.',
                'products': [
                    {
                        'title': 'Hüpfburg Zirkus',
                        'description': 'Die kleinste Hüpfburg in unserem Arsenal. Schöne Drucke im Inneren und stabile Wände sorgen für guten und sicheren Spielspaß. Maße: 4x3x3m (LxBxH), Gewicht: 78kg, Kapazität: 6 Kinder, Aufbauzeit: 10 Minuten, Benötigte Personen: 1, Zubehör: elektrisches Gebläse 1,1kW, Unterlegeplane, Kabeltrommel 25 m.',
                        'price': Decimal('99.00'),
                        'slug': 'huepfburg-zirkus'
                    },
                    {
                        'title': 'Hüpfburg Dschungel',
                        'description': 'Eine farbenfrohe und optisch ansprechende Hüpfburg mit Rutsche und zwei Mittelsäulen. Die Kinder bekamen einen Ansturm. Maße: 4,2 x 4,7 x 2,8 m (L x B x H), Gewicht: 88 kg, Kapazität: 6 Kinder, Aufbauzeit: 10 Minuten, Benötigte Personen: 1, Zubehör: elektrisches Gebläse 1,1 kW, Unterlegeplane, Kabeltrommel 25 m.',
                        'price': Decimal('130.00'),
                        'slug': 'huepfburg-dschungel'
                    },
                    {
                        'title': 'Hüpfburg Polizei',
                        'description': 'Manchmal ist ein Eingreifen der Polizei erforderlich, um eine Party zu beruhigen. Länge 5m, Breite 4m, Höhe 4m, Anzahl Spieler 9, Max. Größe Spieler 1,8m, Personen für Aufbau/Abbau: 2 Personen, Gebläse 1,1 kW x 1, Gebläse = 17 kg, Zubehör: Unterlege Plane, Verlängerung Kabel, Fallschutzmatten.',
                        'price': Decimal('150.00'),
                        'slug': 'huepfburg-polizei'
                    },
                    {
                        'title': 'Hüpfburg Madagaskar',
                        'description': 'Bitte bereiten Sie sich auf verrückten Spaß mit lächelnden Tieren vor. Maße: 5,9 x 3,8 x 3,6 m (L x B x H), Gewicht: 98 kg, Kapazität: 10 Kinder, Aufbauzeit: 10 Minuten, Benötigte Personen: 1-2, Zubehör: elektrisches Gebläse 1,1 kW, Unterlegeplane, Kabeltrommel 25 m.',
                        'price': Decimal('150.00'),
                        'slug': 'huepfburg-madagaskar'
                    },
                    {
                        'title': 'Hüpfburg Party',
                        'description': 'Die schöne Hüpfburg bietet nicht nur viel Spass, sondern auch Sicherheit. Die Rutsche befindet sich seitlich am Eingang, was das Beobachten von spielenden Kindern erleichtert. Maße: 5,9 x 3,7 x 2,8 m (L x B x H), Gewicht: 110 kg, Kapazität: 12 Kinder, Aufbauzeit: 10 Minuten, Benötigte Personen: 1-2, Zubehör: elektrisches Gebläse 1,1 kW, Unterlegeplane, Kabeltrommel 25 m.',
                        'price': Decimal('220.00'),
                        'slug': 'huepfburg-party'
                    },
                    {
                        'title': 'HÜPFBURG MAXI',
                        'description': 'Maxi Hüpfburg bietet Platz für 14 hüpfende Kinder gleichzeitig. Die perfekte Wahl für Feiern, Kindergartenfeste oder anhlisches. Maße: 6,6 x 5,0 x 4,1 m (L x B x H), Gewicht: 180 kg, Kapazität: 14 Kinder, Aufbauzeit: 20 Minuten, Benötigte Personen: 2, Zubehör: elekrtisches Gebläse 1,1kW, Unterlegeplane, Kabeltrommel 25 m.',
                        'price': Decimal('250.00'),
                        'slug': 'huepfburg-maxi'
                    },
                    {
                        'title': 'SHOOTING COMBO',
                        'description': 'Kann man nur auf Hüpfburg springen? Nicht! Sie können auch die Rutsche hinunterrutschen und Kugeln aus zwei Kanonen schießen. Maße: 6,3 x 4,5 x 5,0 m (L x B x H), Gewicht: 155 kg, Kapazität: 10 Kinder, Aufbauzeit: 15 Minuten, 2 shooterkanonnen und 100 Bälle sind dabei, Zubehör: elektrisches Gebläse 1,1 kW, Unterlegeplane, Kabeltrommel 25 m.',
                        'price': Decimal('300.00'),
                        'slug': 'shooting-combo'
                    }
                ]
            },
            {
                'name': 'Spiele & Unterhaltung',
                'description': 'Verschiedene Spiele und Unterhaltungsgeräte für alle Altersgruppen. Von Dart bis hin zu Fußballspielen - hier ist für jeden etwas dabei.',
                'products': [
                    {
                        'title': 'DART XXL',
                        'description': 'Ein tolles Partyspiel in der XXL-Version. Spaß garantiert für Groß und Klein. Maße: 2,5m x 2,3m x 2m (HxBxL), Gewicht: ca.25 kg, Aufbauzeit: 5 Minuten, Benötigte Personen: 1, Zubehör: elektrische Luftpumpe 1200 W, Kabeltrommel 25 m.',
                        'price': Decimal('99.00'),
                        'slug': 'dart-xxl'
                    },
                    {
                        'title': 'FUSSBALL-BILLIARD',
                        'description': 'Eine interessante Abwechslung für Ihre Veranstaltung. Nicht nur für junge Fußballer, auch Eltern und Großeltern können Spaß haben. Maße: 4,6m x 2,9m x 0,5m (LxBxH), Gewicht: ca.20 kg, Aufbauzeit: 5 Minuten, Benötigte Personen: 1, Zubehör: elektrisches Gebläse 750 W, Kabeltrommel 25 m.',
                        'price': Decimal('99.00'),
                        'slug': 'fussball-billiard'
                    },
                    {
                        'title': 'XXL SCHACH',
                        'description': 'Gemeinsame Treffen mit Familie und Freunden, z. B. beim Grillen, können jetzt durch spektakulärer Spiel angenehmer gestaltet werden, die die Gäste sicherlich gerne anfeuern. Die neue Dimension des Schachs ist Bewegung und Aktion nicht nur im Freien.',
                        'price': Decimal('120.00'),
                        'slug': 'xxl-schach'
                    }
                ]
            }
        ]
        
        # Create categories and products
        for cat_data in categories_data:
            category = Category.objects.create(
                name=cat_data['name'],
                slug=slugify(cat_data['name']),
                description=cat_data['description']
            )
            
            self.stdout.write(f'Created category: {category.name}')
            
            # Create products for this category
            for prod_data in cat_data['products']:
                product = Product.objects.create(
                    title=prod_data['title'],
                    slug=prod_data['slug'],
                    description=prod_data['description'],
                    price=prod_data['price'],
                    category=category,
                    is_active=True
                )
                
                self.stdout.write(f'  Created product: {product.title}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully imported data from Site 2!')
        ) 