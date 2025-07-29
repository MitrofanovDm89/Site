from django.core.management.base import BaseCommand
from django.utils.text import slugify
from catalog.models import Category, Product, Service
from decimal import Decimal


class Command(BaseCommand):
    help = 'Populate catalog with sample categories and products'

    def handle(self, *args, **options):
        self.stdout.write('Creating categories and products...')
        
        # Create Categories
        categories_data = [
            {
                'name': 'Hüpfburgen',
                'description': 'Große Auswahl an sicheren und hochwertigen Hüpfburgen für Kinderfeste und Events. Alle unsere Hüpfburgen sind TÜV-geprüft und entsprechen den höchsten Sicherheitsstandards. Perfekt für Geburtstage, Sommerfeste und Events.',
                'products': [
                    {
                        'title': 'Prinzessin Hüpfburg "Magical Castle"',
                        'description': 'Eine zauberhafte Hüpfburg im Prinzessinnen-Design mit Türmen, Rutschen und vielen Spielmöglichkeiten. Die "Magical Castle" Hüpfburg ist der Traum jeder kleinen Prinzessin! Mit glitzernden Elementen, rosafarbenen Türmen und einer eleganten Rutschbahn. Perfekt für Mädchengeburtstage und Prinzessinnen-Partys. Größe: 4x4m, Höhe: 3m. Maximale Belastung: 8 Kinder gleichzeitig.',
                        'price': Decimal('180.00'),
                        'image_placeholder': 'fas fa-crown'
                    },
                    {
                        'title': 'Piraten Hüpfburg "Adventure Island"',
                        'description': 'Abenteuerliche Hüpfburg im Piraten-Design mit Schatzkiste, Anker und Piratenflagge. Die "Adventure Island" bietet spannende Spielmöglichkeiten für kleine Seeräuber! Mit Kletterelementen, Schatzsuche-Bereich und Piraten-Dekoration. Ideal für Jungengeburtstage und Piraten-Partys. Größe: 5x4m, Höhe: 3.5m. Maximale Belastung: 10 Kinder gleichzeitig.',
                        'price': Decimal('220.00'),
                        'image_placeholder': 'fas fa-ship'
                    },
                    {
                        'title': 'Dinosaurier Hüpfburg "Jurassic World"',
                        'description': 'Spannende Hüpfburg im Dinosaurier-Design mit großen Zähnen und wildem Aussehen. Die "Jurassic World" Hüpfburg ist ein Hit bei allen Dino-Fans! Mit realistischen Dinosaurier-Elementen, Fossilien-Bereich und wilder Dschungel-Dekoration. Ein Hit bei allen Kindern! Größe: 4.5x4m, Höhe: 3.2m. Maximale Belastung: 8 Kinder gleichzeitig.',
                        'price': Decimal('200.00'),
                        'image_placeholder': 'fas fa-dragon'
                    },
                    {
                        'title': 'Jungle Safari Hüpfburg "Wild Africa"',
                        'description': 'Wilde Hüpfburg im Safari-Design mit Tieren, Palmen und Abenteuer-Elementen. Die "Wild Africa" Hüpfburg bringt den Dschungel zu Ihnen! Mit exotischen Tieren, Safari-Dekoration und Abenteuer-Spielbereichen. Perfekt für Natur- und Tierliebhaber. Größe: 5x4.5m, Höhe: 3.3m. Maximale Belastung: 10 Kinder gleichzeitig.',
                        'price': Decimal('240.00'),
                        'image_placeholder': 'fas fa-leaf'
                    },
                    {
                        'title': 'Superhelden Hüpfburg "Hero City"',
                        'description': 'Actiongeladene Hüpfburg im Superhelden-Design mit Comic-Elementen und Superkräften! Die "Hero City" Hüpfburg ist perfekt für kleine Superhelden! Mit Comic-Dekoration, Superhelden-Symbolen und actionreichen Spielbereichen. Größe: 4.5x4m, Höhe: 3.1m. Maximale Belastung: 8 Kinder gleichzeitig.',
                        'price': Decimal('210.00'),
                        'image_placeholder': 'fas fa-mask'
                    },
                    {
                        'title': 'Eiszeit Hüpfburg "Frozen World"',
                        'description': 'Coole Hüpfburg im Eiszeit-Design mit Eisbären, Schnee und Polarlichtern! Die "Frozen World" Hüpfburg bringt die Arktis zu Ihnen! Mit Eis-Dekoration, Polartieren und coolen Spielbereichen. Größe: 4x4m, Höhe: 3m. Maximale Belastung: 8 Kinder gleichzeitig.',
                        'price': Decimal('190.00'),
                        'image_placeholder': 'fas fa-snowflake'
                    }
                ]
            },
            {
                'name': 'Gesellschaftsspiele',
                'description': 'Klassische und moderne Gesellschaftsspiele für alle Altersgruppen. Von Brettspielen bis hin zu interaktiven Spielen - hier ist für jeden etwas dabei. Perfekt für Familienfeste, Firmenevents und Gartenpartys.',
                'products': [
                    {
                        'title': 'Riesen Jenga XXL "Tower Master"',
                        'description': 'Das klassische Jenga-Spiel in XXL-Größe für maximalen Spielspaß! Der "Tower Master" besteht aus 54 massiven Holzblöcken (15x7.5x2.5cm) und bietet stundenlangen Spielspaß im Freien oder Innenbereich. Perfekt für Gartenpartys, Firmenevents und Familienfeste. Das Spiel fördert Geschicklichkeit, Konzentration und strategisches Denken. Inklusive Spielanleitung und Transportkiste.',
                        'price': Decimal('120.00'),
                        'image_placeholder': 'fas fa-cubes'
                    },
                    {
                        'title': 'Riesen 4 Gewinnt "Connect Four Pro"',
                        'description': 'Das beliebte Strategiespiel in großer Ausführung für viele Teilnehmer! Das "Connect Four Pro" hat eine Spielfeldgröße von 1.2x1.2m und ist perfekt für Gartenpartys und Events mit vielen Teilnehmern. Mit 42 großen Spielsteinen und stabiler Konstruktion. Fördert strategisches Denken und macht Spaß für alle Altersgruppen.',
                        'price': Decimal('140.00'),
                        'image_placeholder': 'fas fa-circle'
                    },
                    {
                        'title': 'Riesen Schach "Chess Master"',
                        'description': 'Elegantes Schachspiel mit großen Figuren und Spielbrett für Profis und Anfänger! Der "Chess Master" hat eine Brettgröße von 1.2x1.2m mit 30cm hohen Figuren. Ideal für strategische Denker und Schachliebhaber. Perfekt für Gartenpartys, Parks und öffentliche Events. Mit hochwertigen Holzfiguren und stabiler Konstruktion.',
                        'price': Decimal('180.00'),
                        'image_placeholder': 'fas fa-chess'
                    },
                    {
                        'title': 'Riesen Memory "Brain Trainer"',
                        'description': 'Das beliebte Memory-Spiel mit großen Karten für bessere Sichtbarkeit! Der "Brain Trainer" besteht aus 32 großen Karten (20x20cm) und ist perfekt für Kinder und Erwachsene. Fördert Gedächtnis, Konzentration und visuelle Wahrnehmung. Perfekt für Familienfeste, Schulen und Seniorenheime.',
                        'price': Decimal('100.00'),
                        'image_placeholder': 'fas fa-brain'
                    },
                    {
                        'title': 'Riesen Domino "Domino Master"',
                        'description': 'Klassisches Domino in XXL-Größe für große Gruppen! Das "Domino Master" Set besteht aus 28 großen Steinen (15x7.5cm) und ist perfekt für Gartenpartys und Events. Mit stabiler Holzqualität und langlebiger Konstruktion. Fördert strategisches Denken und Gruppenspiel.',
                        'price': Decimal('90.00'),
                        'image_placeholder': 'fas fa-square'
                    },
                    {
                        'title': 'Riesen Twister "Twister Pro"',
                        'description': 'Das beliebte Geschicklichkeitsspiel in großer Ausführung! Der "Twister Pro" hat eine Spielfeldgröße von 2x3m und ist perfekt für Gartenpartys und Events. Mit großen, wetterfesten Farbfeldern und stabiler Konstruktion. Fördert Koordination, Balance und macht viel Spaß!',
                        'price': Decimal('110.00'),
                        'image_placeholder': 'fas fa-hand-paper'
                    }
                ]
            },
            {
                'name': 'Unterhaltungsgeräte',
                'description': 'Moderne Unterhaltungsgeräte und elektronische Spiele für unvergessliche Events. Von Karaoke bis hin zu Gaming-Stationen - wir haben alles für perfekte Unterhaltung.',
                'products': [
                    {
                        'title': 'Karaoke Anlage "Star Voice Pro"',
                        'description': 'Professionelle Karaoke-Anlage mit Mikrofonen, Verstärker und umfangreicher Liedauswahl! Die "Star Voice Pro" Anlage umfasst: 2 Funkmikrofone, 1000+ Lieder, LED-Beleuchtung, Echo-Effekt und 200W Verstärker. Perfekt für Partys und Events. Mit deutscher und internationaler Musikauswahl. Inklusive Transportkoffer und Aufbau.',
                        'price': Decimal('280.00'),
                        'image_placeholder': 'fas fa-microphone'
                    },
                    {
                        'title': 'Gaming Station "Game Zone Pro"',
                        'description': 'Voll ausgestattete Gaming-Station mit Konsole, großen Bildschirmen und beliebten Spielen! Die "Game Zone Pro" umfasst: PlayStation 5, 55" 4K TV, Gaming-Stühle, 20+ Spiele und Surround-Sound. Ein Hit bei Jugendlichen und Erwachsenen! Perfekt für Gaming-Events, LAN-Partys und Firmenevents.',
                        'price': Decimal('350.00'),
                        'image_placeholder': 'fas fa-gamepad'
                    },
                    {
                        'title': 'Fotobox "Photo Booth Deluxe"',
                        'description': 'Interaktive Fotobox mit Kostümen, Requisiten und sofortiger Bildausgabe! Die "Photo Booth Deluxe" umfasst: HD-Kamera, Touchscreen, Drucker, 50+ Kostüme, 100+ Requisiten und sofortige Bildausgabe. Schafft unvergessliche Erinnerungen! Perfekt für Hochzeiten, Geburtstage und Firmenevents.',
                        'price': Decimal('250.00'),
                        'image_placeholder': 'fas fa-camera'
                    },
                    {
                        'title': 'DJ Equipment "Mix Master Pro"',
                        'description': 'Professionelle DJ-Ausrüstung mit Mischpult, Lautsprechern und umfangreicher Musikbibliothek! Das "Mix Master Pro" Set umfasst: DJ-Mischpult, 2x 1000W Lautsprecher, Subwoofer, Mikrofone und 10.000+ Songs. Perfekt für Partys, Hochzeiten und Events. Mit professionellem DJ-Service optional.',
                        'price': Decimal('400.00'),
                        'image_placeholder': 'fas fa-music'
                    },
                    {
                        'title': 'Virtual Reality Station "VR World"',
                        'description': 'Moderne VR-Station mit Oculus Quest 2 und 20+ VR-Spielen! Die "VR World" Station bietet: 2x Oculus Quest 2, Gaming-PC, 20+ VR-Spiele und 4K-Monitor. Perfekt für Events, Messen und Firmenpräsentationen. Mit VR-Betreuer optional.',
                        'price': Decimal('320.00'),
                        'image_placeholder': 'fas fa-vr-cardboard'
                    },
                    {
                        'title': 'Laser Tag Arena "Battle Zone"',
                        'description': 'Spannende Laser Tag Arena für Action und Spaß! Die "Battle Zone" umfasst: 8 Laser Tag Pistolen, Arena-Aufbau, Soundeffekte und LED-Beleuchtung. Perfekt für Geburtstage, Firmenevents und Teambuilding. Mit Arena-Aufbau und Betreuer inklusive.',
                        'price': Decimal('380.00'),
                        'image_placeholder': 'fas fa-crosshairs'
                    }
                ]
            },
            {
                'name': 'Kinderfeste',
                'description': 'Komplette Pakete für unvergessliche Kinderfeste. Von der Dekoration bis hin zur Unterhaltung - wir kümmern uns um alles. Professionelle Betreuung und maßgeschneiderte Lösungen.',
                'products': [
                    {
                        'title': 'Prinzessin Party Paket "Royal Dream"',
                        'description': 'Komplettes Prinzessin-Party-Paket mit Dekoration, Kostümen, Spielen und Hüpfburg! Das "Royal Dream" Paket umfasst: Prinzessin-Hüpfburg, 10 Prinzessinnen-Kostüme, Dekoration, Schminkstation, Prinzessinnen-Spiele, Fotobox und professionelle Betreuung. Perfekt für Mädchengeburtstage (5-12 Jahre). Dauer: 4 Stunden.',
                        'price': Decimal('450.00'),
                        'image_placeholder': 'fas fa-crown'
                    },
                    {
                        'title': 'Piraten Party Paket "Adventure Quest"',
                        'description': 'Abenteuerliches Piraten-Party-Paket mit Schatzsuche, Kostümen und Piraten-Hüpfburg! Das "Adventure Quest" Paket umfasst: Piraten-Hüpfburg, 10 Piraten-Kostüme, Schatzsuche-Spiel, Piraten-Dekoration, Schminkstation, Piraten-Spiele und professionelle Betreuung. Ideal für Jungengeburtstage (5-12 Jahre). Dauer: 4 Stunden.',
                        'price': Decimal('480.00'),
                        'image_placeholder': 'fas fa-skull-crossbones'
                    },
                    {
                        'title': 'Dinosaurier Party Paket "Jurassic Adventure"',
                        'description': 'Wilde Dinosaurier-Party mit Dino-Hüpfburg, Fossilien-Ausgrabung und Dino-Spielen! Das "Jurassic Adventure" Paket umfasst: Dinosaurier-Hüpfburg, 10 Dino-Kostüme, Fossilien-Ausgrabung, Dino-Dekoration, Schminkstation, Dino-Spiele und professionelle Betreuung. Ein Hit bei allen Kindern (4-10 Jahre). Dauer: 4 Stunden.',
                        'price': Decimal('460.00'),
                        'image_placeholder': 'fas fa-dragon'
                    },
                    {
                        'title': 'Superhelden Party Paket "Hero Academy"',
                        'description': 'Actiongeladene Superhelden-Party mit Kostümen, Training und Superkräften! Das "Hero Academy" Paket umfasst: Superhelden-Dekoration, 10 Superhelden-Kostüme, Superkräfte-Training, Schminkstation, Superhelden-Spiele, Fotobox und professionelle Betreuung. Perfekt für Jungen und Mädchen (5-12 Jahre). Dauer: 4 Stunden.',
                        'price': Decimal('470.00'),
                        'image_placeholder': 'fas fa-mask'
                    },
                    {
                        'title': 'Eiszeit Party Paket "Frozen Adventure"',
                        'description': 'Coole Eiszeit-Party mit Eisbären, Schnee-Spielen und Polarlichtern! Das "Frozen Adventure" Paket umfasst: Eiszeit-Dekoration, 10 Eisbären-Kostüme, Schnee-Spiele, Schminkstation, Eiszeit-Spiele, Fotobox und professionelle Betreuung. Perfekt für alle Altersgruppen (4-10 Jahre). Dauer: 4 Stunden.',
                        'price': Decimal('440.00'),
                        'image_placeholder': 'fas fa-snowflake'
                    },
                    {
                        'title': 'Jungle Safari Party Paket "Wild Expedition"',
                        'description': 'Wilde Safari-Party mit Tierkostümen, Safari-Spielen und Jungle-Hüpfburg! Das "Wild Expedition" Paket umfasst: Safari-Hüpfburg, 10 Tier-Kostüme, Safari-Spiele, Dschungel-Dekoration, Schminkstation, Tier-Spiele und professionelle Betreuung. Perfekt für Naturliebhaber (4-10 Jahre). Dauer: 4 Stunden.',
                        'price': Decimal('490.00'),
                        'image_placeholder': 'fas fa-tree'
                    }
                ]
            },
            {
                'name': 'Events',
                'description': 'Professionelle Event-Ausstattung für Firmenfeiern, Hochzeiten und große Veranstaltungen. Wir machen Ihr Event unvergesslich mit hochwertiger Ausstattung und professionellem Service.',
                'products': [
                    {
                        'title': 'Firmenfeier Paket "Corporate Event Pro"',
                        'description': 'Komplettes Paket für Firmenfeiern mit Unterhaltungsgeräten, Spielen und professioneller Betreuung! Das "Corporate Event Pro" Paket umfasst: 2 Hüpfburgen, Gesellschaftsspiele, Fotobox, Karaoke-Anlage, DJ-Equipment, Dekoration und professionelle Betreuung. Perfekt für Firmenfeiern, Sommerfeste und Events. Dauer: 6-8 Stunden.',
                        'price': Decimal('650.00'),
                        'image_placeholder': 'fas fa-building'
                    },
                    {
                        'title': 'Hochzeits Unterhaltung "Wedding Dream"',
                        'description': 'Elegante Unterhaltungsoptionen für Hochzeiten mit Fotobox, Karaoke und stilvollen Spielen! Das "Wedding Dream" Paket umfasst: Hochzeits-Fotobox, Karaoke-Anlage, Gesellschaftsspiele, elegante Dekoration, professionelle Betreuung und Hochzeits-Spiele. Perfekt für Hochzeiten und Hochzeitsfeiern. Dauer: 6-8 Stunden.',
                        'price': Decimal('750.00'),
                        'image_placeholder': 'fas fa-heart'
                    },
                    {
                        'title': 'Sommerfest Ausstattung "Summer Festival"',
                        'description': 'Umfangreiche Ausstattung für Sommerfeste mit Hüpfburgen, Spielen und Unterhaltungsgeräten! Das "Summer Festival" Paket umfasst: 3 Hüpfburgen, Gesellschaftsspiele, Fotobox, DJ-Equipment, Dekoration und professionelle Betreuung. Perfekt für Sommerfeste, Stadtfeste und große Events. Dauer: 8-10 Stunden.',
                        'price': Decimal('580.00'),
                        'image_placeholder': 'fas fa-sun'
                    },
                    {
                        'title': 'Geburtstags Special "Birthday Master"',
                        'description': 'Personalisiertes Geburtstags-Paket mit individueller Gestaltung und Wunschausstattung! Das "Birthday Master" Paket umfasst: Wunsch-Hüpfburg, Gesellschaftsspiele, Fotobox, Dekoration nach Wunsch, Schminkstation, personalisierte Spiele und professionelle Betreuung. Perfekt für besondere Geburtstage. Dauer: 4-6 Stunden.',
                        'price': Decimal('520.00'),
                        'image_placeholder': 'fas fa-birthday-cake'
                    },
                    {
                        'title': 'Weihnachtsfeier Paket "Christmas Magic"',
                        'description': 'Festliche Weihnachtsfeier mit winterlichen Spielen und Dekoration! Das "Christmas Magic" Paket umfasst: Weihnachts-Dekoration, Gesellschaftsspiele, Fotobox, Weihnachts-Spiele, Schminkstation und professionelle Betreuung. Perfekt für Weihnachtsfeiern und winterliche Events. Dauer: 4-6 Stunden.',
                        'price': Decimal('480.00'),
                        'image_placeholder': 'fas fa-snowman'
                    },
                    {
                        'title': 'Halloween Party Paket "Spooky Night"',
                        'description': 'Gruselige Halloween-Party mit Kostümen, Dekoration und Spooky-Spielen! Das "Spooky Night" Paket umfasst: Halloween-Dekoration, 10 Halloween-Kostüme, Grusel-Spiele, Schminkstation, Fotobox und professionelle Betreuung. Perfekt für Halloween-Partys und gruselige Events. Dauer: 4-6 Stunden.',
                        'price': Decimal('460.00'),
                        'image_placeholder': 'fas fa-ghost'
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
        
        # Create Services
        services_data = [
            {
                'title': 'Lieferung und Aufbau',
                'description': 'Professionelle Lieferung und Aufbau aller Geräte an Ihrem Wunschort. Wir kümmern uns um alles! Inklusive Transport, Aufbau, Abbau und Abholung. Kostenlose Lieferung innerhalb von 50km.',
                'price': Decimal('80.00')
            },
            {
                'title': 'Betreuung vor Ort',
                'description': 'Erfahrene Betreuer kümmern sich um die Sicherheit und den reibungslosen Ablauf Ihres Events. Professionelle Betreuung für alle Altersgruppen. Inklusive Sicherheitsüberwachung und Spieleleitung.',
                'price': Decimal('120.00')
            },
            {
                'title': 'Dekoration',
                'description': 'Professionelle Dekoration passend zu Ihrem Event-Thema. Wir gestalten Ihre Veranstaltung individuell. Inklusive Ballons, Banner, Tischdekoration und thematische Gestaltung.',
                'price': Decimal('150.00')
            },
            {
                'title': 'Fotograf',
                'description': 'Professioneller Fotograf dokumentiert Ihr Event und liefert hochwertige Bilder als Erinnerung. Inklusive 100+ bearbeitete Fotos, Online-Galerie und USB-Stick mit allen Bildern.',
                'price': Decimal('300.00')
            },
            {
                'title': 'DJ Service',
                'description': 'Professioneller DJ für Ihre Veranstaltung mit umfangreicher Musikauswahl. Inklusive DJ-Equipment, Musikbibliothek, Lichtshow und professionellem DJ-Service.',
                'price': Decimal('250.00')
            },
            {
                'title': 'Catering Service',
                'description': 'Umfangreiches Catering für Ihr Event mit Getränken, Snacks und warmen Speisen. Inklusive Service-Personal, Geschirr und Aufräumservice.',
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
            self.style.SUCCESS('Successfully populated catalog with categories, products and services!')
        ) 