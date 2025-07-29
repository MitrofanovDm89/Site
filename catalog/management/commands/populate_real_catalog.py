from django.core.management.base import BaseCommand
from django.utils.text import slugify
from catalog.models import Category, Product, Service
from decimal import Decimal


class Command(BaseCommand):
    help = 'Populate catalog with real data from Site 2'

    def handle(self, *args, **options):
        self.stdout.write('Creating real categories and products from Site 2...')
        
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
                        'image_placeholder': 'fas fa-tent'
                    },
                    {
                        'title': 'Hüpfburg Dschungel',
                        'description': 'Eine farbenfrohe und optisch ansprechende Hüpfburg mit Rutsche und zwei Mittelsäulen. Die Kinder bekamen einen Ansturm. Maße: 4,2 x 4,7 x 2,8 m (L x B x H), Gewicht: 88 kg, Kapazität: 6 Kinder, Aufbauzeit: 10 Minuten, Benötigte Personen: 1, Zubehör: elektrisches Gebläse 1,1 kW, Unterlegeplane, Kabeltrommel 25 m.',
                        'price': Decimal('130.00'),
                        'image_placeholder': 'fas fa-leaf'
                    },
                    {
                        'title': 'Hüpfburg Polizei',
                        'description': 'Manchmal ist ein Eingreifen der Polizei erforderlich, um eine Party zu beruhigen. Länge 5m, Breite 4m, Höhe 4m, Anzahl Spieler 9, Max. Größe Spieler 1,8m, Personen für Aufbau/Abbau: 2 Personen, Gebläse 1,1 kW x 1, Gebläse = 17 kg, Zubehör: Unterlege Plane, Verlängerung Kabel, Fallschutzmatten.',
                        'price': Decimal('150.00'),
                        'image_placeholder': 'fas fa-shield-alt'
                    },
                    {
                        'title': 'Hüpfburg Madagaskar',
                        'description': 'Bitte bereiten Sie sich auf verrückten Spaß mit lächelnden Tieren vor. Maße: 5,9 x 3,8 x 3,6 m (L x B x H), Gewicht: 98 kg, Kapazität: 10 Kinder, Aufbauzeit: 10 Minuten, Benötigte Personen: 1-2, Zubehör: elektrisches Gebläse 1,1 kW, Unterlegeplane, Kabeltrommel 25 m.',
                        'price': Decimal('150.00'),
                        'image_placeholder': 'fas fa-smile'
                    },
                    {
                        'title': 'Hüpfburg Party',
                        'description': 'Die schöne Hüpfburg bietet nicht nur viel Spass, sondern auch Sicherheit. Die Rutsche befindet sich seitlich am Eingang, was das Beobachten von spielenden Kindern erleichtert. Maße: 5,9 x 3,7 x 2,8 m (L x B x H), Gewicht: 110 kg, Kapazität: 12 Kinder, Aufbauzeit: 10 Minuten, Benötigte Personen: 1-2, Zubehör: elektrisches Gebläse 1,1 kW, Unterlegeplane, Kabeltrommel 25 m.',
                        'price': Decimal('220.00'),
                        'image_placeholder': 'fas fa-birthday-cake'
                    },
                    {
                        'title': 'HÜPFBURG MAXI',
                        'description': 'Maxi Hüpfburg bietet Platz für 14 hüpfende Kinder gleichzeitig. Die perfekte Wahl für Feiern, Kindergartenfeste oder anhlisches. Maße: 6,6 x 5,0 x 4,1 m (L x B x H), Gewicht: 180 kg, Kapazität: 14 Kinder, Aufbauzeit: 20 Minuten, Benötigte Personen: 2, Zubehör: elekrtisches Gebläse 1,1kW, Unterlegeplane, Kabeltrommel 25 m.',
                        'price': Decimal('250.00'),
                        'image_placeholder': 'fas fa-expand-arrows-alt'
                    },
                    {
                        'title': 'SHOOTING COMBO',
                        'description': 'Kann man nur auf Hüpfburg springen? Nicht! Sie können auch die Rutsche hinunterrutschen und Kugeln aus zwei Kanonen schießen. Maße: 6,3 x 4,5 x 5,0 m (L x B x H), Gewicht: 155 kg, Kapazität: 10 Kinder, Aufbauzeit: 15 Minuten, 2 shooterkanonnen und 100 Bälle sind dabei, Zubehör: elektrisches Gebläse 1,1 kW, Unterlegeplane, Kabeltrommel 25 m.',
                        'price': Decimal('300.00'),
                        'image_placeholder': 'fas fa-crosshairs'
                    },
                    {
                        'title': 'Hüpfburg Delphin',
                        'description': 'Schöne und stabile Hüpfburg für Mädchen und Jungen. Sehr gemütliche Drucke auf der Seite fallen auf und erfreuen das Auge. Maße: 4,5x5x4 m (LxBxH), Gewicht: 114 kg, Kapazität: 8 Kinder, Aufbauzeit: 10 Minuten, Zubehör: elektrisches Gebläse 1,1 kW, Unterlegeplane, Kabeltrommel 25 m.',
                        'price': Decimal('150.00'),
                        'image_placeholder': 'fas fa-fish'
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
                        'image_placeholder': 'fas fa-bullseye'
                    },
                    {
                        'title': 'FUSSBALL-BILLIARD',
                        'description': 'Eine interessante Abwechslung für Ihre Veranstaltung. Nicht nur für junge Fußballer, auch Eltern und Großeltern können Spaß haben. Maße: 4,6m x 2,9m x 0,5m (LxBxH), Gewicht: ca.20 kg, Aufbauzeit: 5 Minuten, Benötigte Personen: 1, Zubehör: elektrisches Gebläse 750 W, Kabeltrommel 25 m.',
                        'price': Decimal('99.00'),
                        'image_placeholder': 'fas fa-futbol'
                    },
                    {
                        'title': 'XXL SCHACH',
                        'description': 'Gemeinsame Treffen mit Familie und Freunden, z. B. beim Grillen, können jetzt durch spektakulärer Spiel angenehmer gestaltet werden, die die Gäste sicherlich gerne anfeuern. Die neue Dimension des Schachs ist Bewegung und Aktion nicht nur im Freien.',
                        'price': Decimal('120.00'),
                        'image_placeholder': 'fas fa-chess'
                    },
                    {
                        'title': 'Fußball Darts',
                        'description': 'Jeder kann schießen, aber wer trifft die Mitte? Größe: 3.0m x 1.2m x 3.0m, Zubehör: elektrische Pumpe, spezielle Bälle, Unterlage Plane, Kabel 25 M.',
                        'price': Decimal('99.00'),
                        'image_placeholder': 'fas fa-crosshairs'
                    },
                    {
                        'title': 'Stockfangen',
                        'description': '"Stockfangen" ist ein einfaches und unterhaltsames Spiel, das im Freien oder in größeren Innenräumen gespielt werden kann. Maße: 2,5m x 1,4m, Gewicht: 15 kg, Aufbauzeit ca. 10 Minute, Max. Größe Spieler 1,8m, Benötigte Personen: 1, Zubehör: Bravo OV6 Gebläse = 1,3 kg.',
                        'price': Decimal('99.00'),
                        'image_placeholder': 'fas fa-running'
                    },
                    {
                        'title': 'Bull Rodeo',
                        'description': 'Ein großer Spaß für Kinder und Erwachsene. Testen Sie Ihr Gleichgewicht und Ihre Beweglichkeit!!! Maße: 4,5x5x4 m (LxBxH), Gewicht: ca.350 kg, Kapazität: 1 Kinder, Aufbauzeit: 20 Minuten, Zubehör: elektrisches Gebläse 1,1 kW, Unterlegeplane, Kabeltrommel 25 m.',
                        'price': Decimal('425.00'),
                        'image_placeholder': 'fas fa-bull'
                    }
                ]
            },
            {
                'name': 'Zubehör & Catering',
                'description': 'Zusätzliche Ausstattung und Catering-Service für perfekte Events. Von Popcorn-Maschinen bis hin zu professionellen Services.',
                'products': [
                    {
                        'title': 'POPCORNMASCHINE',
                        'description': 'Nicht nur Kinder lieben Popcorn. Frisch schmeckt natürlich am besten. Süß oder salzig entscheiden Sie selbst. Leistung: 1.600 Watt, Arbeitsleistung: 5 kg/h, 16 L/h, Topfdurchmesser: Oben: 18,5 cm, Topfbeschichtung: Teflon, mobil einsetzbar, 50g Pocpornmais und 50 ml Öl (Kokos- Palm-Sonnenblumenöl) und 50 g Zucker für ein Portion.',
                        'price': Decimal('79.00'),
                        'image_placeholder': 'fas fa-popcorn'
                    },
                    {
                        'title': 'Tor mit Radar',
                        'description': 'Ein "Tor mit Radar" ist eine moderne Variante eines Fußballtores, das mit Radar- oder Sensortechnologie ausgestattet ist, um Torschüsse zu erkennen und zu verfolgen. Gewicht ca. 80 kg, Größe: 4m x 5m, Radar, Strombetrieben, Unteregplane, Gebläse, Verlängerungskabel.',
                        'price': Decimal('200.00'),
                        'image_placeholder': 'fas fa-radar'
                    }
                ]
            }
        ]
        
        # Create categories and products
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'slug': slugify(cat_data['name']),
                    'description': cat_data['description']
                }
            )
            
            if created:
                self.stdout.write(f'Created category: {category.name}')
            else:
                self.stdout.write(f'Category already exists: {category.name}')
            
            # Create products for this category
            for prod_data in cat_data['products']:
                product, created = Product.objects.get_or_create(
                    title=prod_data['title'],
                    defaults={
                        'slug': slugify(prod_data['title']),
                        'description': prod_data['description'],
                        'price': prod_data['price'],
                        'category': category,
                        'is_active': True
                    }
                )
                
                if created:
                    self.stdout.write(f'  Created product: {product.title}')
                else:
                    self.stdout.write(f'  Product already exists: {product.title}')
        
        # Create Services based on Site 2
        services_data = [
            {
                'title': 'Lieferung und Aufbau',
                'description': 'Professionelle Lieferung und Aufbau aller Geräte an Ihrem Wunschort. Kostenlose Lieferung innerhalb von 30km, 60 Euro im Radius von 30 km.',
                'price': Decimal('60.00')
            },
            {
                'title': 'Betreuung vor Ort',
                'description': 'Erfahrene Betreuer kümmern sich um die Sicherheit und den reibungslosen Ablauf Ihres Events. Professionelle Betreuung für alle Altersgruppen.',
                'price': Decimal('120.00')
            },
            {
                'title': 'Dekoration',
                'description': 'Professionelle Dekoration passend zu Ihrem Event-Thema. Wir gestalten Ihre Veranstaltung individuell.',
                'price': Decimal('150.00')
            },
            {
                'title': 'Fotograf',
                'description': 'Professioneller Fotograf dokumentiert Ihr Event und liefert hochwertige Bilder als Erinnerung.',
                'price': Decimal('300.00')
            },
            {
                'title': 'DJ Service',
                'description': 'Professioneller DJ für Ihre Veranstaltung mit umfangreicher Musikauswahl.',
                'price': Decimal('250.00')
            },
            {
                'title': 'Catering Service',
                'description': 'Umfangreiches Catering für Ihr Event mit Getränken, Snacks und warmen Speisen.',
                'price': Decimal('400.00')
            }
        ]
        
        for service_data in services_data:
            service, created = Service.objects.get_or_create(
                title=service_data['title'],
                defaults={
                    'slug': slugify(service_data['title']),
                    'description': service_data['description'],
                    'price': service_data['price'],
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(f'Created service: {service.title}')
            else:
                self.stdout.write(f'Service already exists: {service.title}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated catalog with real data from Site 2!')
        ) 