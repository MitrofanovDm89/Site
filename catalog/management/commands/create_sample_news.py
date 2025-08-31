from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from catalog.models import News
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Создает тестовые новости для демонстрации'

    def handle(self, *args, **options):
        # Получаем первого пользователя как автора
        try:
            author = User.objects.first()
            if not author:
                self.stdout.write(self.style.ERROR('Нет пользователей в системе. Создайте суперпользователя сначала.'))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка при получении пользователя: {e}'))
            return

        # Создаем тестовые новости
        news_data = [
            {
                'title': 'Neue Hüpfburgen verfügbar',
                'excerpt': 'Wir haben unser Sortiment um neue, sichere Hüpfburgen erweitert. Perfekt für Kinderfeste und Events.',
                'content': '''Wir freuen uns, Ihnen mitteilen zu können, dass wir unser Sortiment um neue, sichere Hüpfburgen erweitert haben!

Diese neuen Modelle bieten:
• Verbesserte Sicherheitsstandards
• Moderne Designs und Farben
• Einfache Aufbau- und Abbauprozesse
• Optimale Belüftung

Alle Hüpfburgen sind TÜV-geprüft und entsprechen den neuesten Sicherheitsrichtlinien. Perfekt für Kinderfeste, Geburtstage und Firmenevents.

Kontaktieren Sie uns für weitere Informationen und Buchungsanfragen!''',
                'featured': True,
                'published_at': datetime.now() - timedelta(days=5)
            },
            {
                'title': 'Weihnachts-Special',
                'excerpt': 'Spezielle Angebote für Weihnachtsfeiern und Firmenevents. Buchen Sie jetzt und sparen Sie 20%.',
                'content': '''Das Weihnachtsfest steht vor der Tür und wir haben spezielle Angebote für Sie!

🎄 Weihnachts-Special 2024:
• 20% Rabatt auf alle Buchungen im Dezember
• Kostenlose Lieferung am 24. Dezember
• Spezielle Weihnachts-Dekorationen inklusive
• Flexible Buchungszeiten

Perfekt für:
• Firmen-Weihnachtsfeiern
• Familienfeiern
• Adventsfeiern
• Silvester-Events

Buchen Sie jetzt und sichern Sie sich die besten Termine!''',
                'featured': True,
                'published_at': datetime.now() - timedelta(days=10)
            },
            {
                'title': 'Team-Building Events',
                'excerpt': 'Neue Team-Building Pakete für Firmen. Fördern Sie den Zusammenhalt mit Spaß und Spiel.',
                'content': '''Stärken Sie Ihr Team mit unseren neuen Team-Building Paketen!

🏆 Was bieten wir:
• Professionell organisierte Events
• Verschiedene Schwierigkeitsgrade
• Indoor- und Outdoor-Aktivitäten
• Nachhaltige Teambildung

Unsere Pakete beinhalten:
• Hüpfburgen und Spiele
• Kooperationsspiele
• Wettbewerbe
• Reflexionsrunden

Ideal für:
• Firmen aller Größen
• Abteilungen
• Projektteams
• Neue Mitarbeiter

Kontaktieren Sie uns für ein maßgeschneidertes Angebot!''',
                'featured': False,
                'published_at': datetime.now() - timedelta(days=15)
            },
            {
                'title': 'Sicherheitszertifizierung',
                'excerpt': 'Alle unsere Geräte haben die neuesten Sicherheitszertifizierungen erhalten. Ihre Sicherheit steht an erster Stelle.',
                'content': '''Ihre Sicherheit ist unser höchstes Gut!

🛡️ Neue Sicherheitszertifizierungen:
Alle unsere Geräte haben erfolgreich die neuesten Sicherheitsprüfungen bestanden und entsprechen den höchsten Standards.

Was bedeutet das für Sie:
• TÜV-geprüfte Sicherheit
• Regelmäßige Wartung
• Professionelle Aufsicht
• Versicherungsschutz

Unsere Sicherheitsmaßnahmen:
• Tägliche Inspektionen
• Wöchentliche Wartung
• Monatliche Sicherheitsprüfungen
• Jährliche Zertifizierung

Vertrauen Sie auf unsere Erfahrung und Professionalität!''',
                'featured': False,
                'published_at': datetime.now() - timedelta(days=20)
            }
        ]

        created_count = 0
        for news_item in news_data:
            try:
                news, created = News.objects.get_or_create(
                    title=news_item['title'],
                    defaults={
                        'excerpt': news_item['excerpt'],
                        'content': news_item['content'],
                        'featured': news_item['featured'],
                        'published_at': news_item['published_at'],
                        'author': author,
                        'is_published': True
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Создана новость: {news.title}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Новость уже существует: {news.title}')
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Ошибка при создании новости "{news_item["title"]}": {e}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Готово! Создано {created_count} новых новостей.')
        )
