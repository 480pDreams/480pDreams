from django.core.management.base import BaseCommand
from core.models import NetworkVideo
import feedparser
from datetime import datetime
import time


class Command(BaseCommand):
    help = 'Fetches latest videos from YouTube RSS feeds'

    def handle(self, *args, **kwargs):
        # 1. Configuration: Map Channel IDs to your Database Choices
        # Find ID by viewing source of channel page -> "externalId"
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

            for entry in feed.entries[:5]:  # Check top 5
                video_id = entry.yt_videoid
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                title = entry.title

                # Check if exists
                if not NetworkVideo.objects.filter(url=video_url).exists():
                    NetworkVideo.objects.create(
                        title=title,
                        channel=channel['type'],
                        url=video_url,
                        # We can't grab the high-res thumb easily via RSS,
                        # but embed_video handles fetching it on save usually,
                        # or we can manually construct it:
                        # thumbnail = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
                    )
                    self.stdout.write(self.style.SUCCESS(f"  + Added: {title}"))
                else:
                    self.stdout.write(f"  - Skipped (Exists): {title}")