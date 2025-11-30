from django.core.management.base import BaseCommand
from core.models import NetworkVideo
from django.core.files.base import ContentFile
from library.models import compress_image  # <--- Reusing your existing tool!
import feedparser
import requests
from io import BytesIO


class Command(BaseCommand):
    help = 'Fetches latest videos, downloads HD thumbs, and compresses them'

    def handle(self, *args, **kwargs):
        CHANNELS = [
            {
                'name': '480pDreams (Main)',
                'id': 'UCOeFweCdYGFDtOknBotLEEw',
                'type': 'main'
            },
            {
                'name': '480pReviews',
                'id': 'UCBGlYlZ5M-_qMOGt_xzJ32g',
                'type': 'reviews'
            },
            {
                'name': '480pGames',
                'id': 'UCKjqyPNFZ_MQAlqdmSj7CuA',
                'type': 'gameplay'
            },
        ]

        for channel in CHANNELS:
            url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel['id']}"
            self.stdout.write(f"Checking {channel['name']}...")

            feed = feedparser.parse(url)

            for entry in reversed(feed.entries[:10]):
                video_id = entry.yt_videoid
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                title = entry.title

                if not NetworkVideo.objects.filter(url=video_url).exists():
                    self.stdout.write(f"  + Processing: {title}")

                    video_obj = NetworkVideo(
                        title=title,
                        channel=channel['type'],
                        url=video_url
                    )

                    # 1. Download High Res
                    thumb_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
                    response = requests.get(thumb_url)

                    if response.status_code != 200:
                        # Fallback
                        thumb_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
                        response = requests.get(thumb_url)

                    # 2. Compress & Save
                    if response.status_code == 200:
                        # Wrap the raw downloaded bytes in a container so Pillow can read it
                        image_stream = BytesIO(response.content)

                        # Run your compressor (Resize to 800px width is perfect for shelves)
                        compressed_file = compress_image(image_stream, max_width=800)

                        if compressed_file:
                            file_name = f"{video_id}.jpg"
                            video_obj.thumbnail.save(file_name, compressed_file, save=True)
                        else:
                            # If compression fails, save raw
                            video_obj.thumbnail.save(f"{video_id}.jpg", ContentFile(response.content), save=True)
                    else:
                        video_obj.save()

                else:
                    self.stdout.write(f"  - Skipped: {title}")