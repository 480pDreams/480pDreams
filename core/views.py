from django.shortcuts import render
from library.models import Game  # Import the Game model from the other app
from hardware.models import Hardware
from .models import NetworkVideo
from itertools import chain
from operator import attrgetter
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import json
from .models import UserProfile

def home(request):
    # ROW 1: New Videos
    new_videos = NetworkVideo.objects.order_by('-created_at')[:8]

    # ROW 2 & 3: Get Data
    # Fetch 5 of each to be safe
    recent_games = list(Game.objects.order_by('-created_at')[:10])
    recent_hardware = list(Hardware.objects.order_by('-created_at')[:10])

    updated_games = list(Game.objects.order_by('-updated_at')[:10])
    updated_hardware = list(Hardware.objects.order_by('-updated_at')[:10])

    # ANNOTATE: Tag them so the template knows what they are
    for g in recent_games: g.kind = 'game'
    for h in recent_hardware: h.kind = 'hardware'

    for g in updated_games: g.kind = 'game'
    for h in updated_hardware: h.kind = 'hardware'

    # MERGE & SORT: Recent Acquisitions
    recent_acquisitions = sorted(
        recent_games + recent_hardware,  # Combine lists
        key=attrgetter('created_at'),
        reverse=True
    )[:8]

    # MERGE & SORT: Recently Updated
    recently_updated = sorted(
        updated_games + updated_hardware,  # Combine lists
        key=attrgetter('updated_at'),
        reverse=True
    )[:8]

    context = {
        'new_videos': new_videos,
        'recent_acquisitions': recent_acquisitions,
        'recently_updated': recently_updated,
    }
    return render(request, 'core/home.html', context)

def about(request):
    return render(request, 'core/about.html')

def hardware(request):
    return render(request, 'core/hardware.html')


@login_required
def update_theme(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_theme = data.get('theme')

            # SELF-HEALING LOGIC:
            # Instead of assuming the profile exists, we use 'get_or_create'.
            # This fixes the issue for old Superusers or broken accounts.
            profile, created = UserProfile.objects.get_or_create(user=request.user)

            profile.theme = new_theme
            profile.save()

            return JsonResponse({'status': 'ok'})
        except Exception as e:
            # Print error to terminal so we can see it if it happens again
            print(f"Theme Update Error: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error'}, status=400)