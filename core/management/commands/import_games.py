import csv
import os
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.base import ContentFile
from library.models import Game, Platform, Genre, Region, Developer, Publisher
from datetime import datetime


class Command(BaseCommand):
    help = 'Import games from a CSV file (games.csv) in the project root'

    def handle(self, *args, **kwargs):
        file_path = os.path.join(settings.BASE_DIR, 'games.csv')

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR('games.csv not found in project root!'))
            return

        # encoding='utf-8-sig' handles Excel's hidden BOM characters
        with open(file_path, 'r', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0

            for row in reader:
                title = row['Title'].strip()
                if not title: continue

                self.stdout.write(f"Processing: {title}...")

                # 1. GET OR CREATE PLATFORM
                plat_name = row['Platform'].strip()
                platform, _ = Platform.objects.get_or_create(
                    name=plat_name,
                    defaults={'slug': plat_name.lower().replace(' ', '-')}
                )

                # 2. CREATE GAME
                game, created = Game.objects.update_or_create(
                    title=title,
                    platform=platform,
                    defaults={
                        'description': row.get('Description', ''),
                        'slug': f"{title.lower().replace(' ', '-')}-{platform.slug}"[:50],
                        'release_date': self.parse_date(row.get('Release Date')),
                        'game_format': row.get('Format', 'PHYSICAL').upper(),
                        # Booleans (Accepts TRUE/FALSE, YES/NO, 1/0)
                        'own_game': self.parse_bool(row.get('Own Game')),
                        'own_box': self.parse_bool(row.get('Own Box')),
                        'own_manual': self.parse_bool(row.get('Own Manual')),
                        'condition_notes': row.get('Notes', ''),
                    }
                )

                # 3. HANDLE M2M (Comma separated)
                self.add_m2m(game.genres, Genre, row.get('Genres', ''))
                self.add_m2m(game.regions, Region, row.get('Regions', ''))
                self.add_m2m(game.developers, Developer, row.get('Developers', ''))
                self.add_m2m(game.publishers, Publisher, row.get('Publishers', ''))

                # 4. DOWNLOAD IMAGE (If provided and missing)
                image_url = row.get('Image URL', '').strip()
                if image_url and not game.box_art:
                    self.download_image(game, image_url)

                # Save to trigger compression logic
                game.save()

                if created:
                    count += 1

            self.stdout.write(self.style.SUCCESS(f'Finished! Imported {count} new games.'))

    def parse_date(self, date_str):
        if not date_str: return None
        try:
            # Expects YYYY-MM-DD
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return None

    def parse_bool(self, val):
        return str(val).lower() in ['true', '1', 'yes', 'y']

    def add_m2m(self, field, model, data_str):
        if not data_str: return
        # Split by comma
        items = [x.strip() for x in data_str.split(',')]
        for item in items:
            if not item: continue
            obj, _ = model.objects.get_or_create(
                name=item,
                defaults={'slug': item.lower().replace(' ', '-')}
            )
            field.add(obj)

    def download_image(self, game, url):
        try:
            self.stdout.write(f"  - Downloading art...")
            # Pretend to be a browser to avoid blocks
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                # Guess extension
                ext = 'jpg'
                if '.png' in url.lower(): ext = 'png'

                filename = f"{game.slug}.{ext}"
                # save=False because we save the game object later
                game.box_art.save(filename, ContentFile(response.content), save=False)
            else:
                self.stdout.write(self.style.WARNING(f"  ! Failed to download (Status {response.status_code})"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"  ! Error downloading: {e}"))