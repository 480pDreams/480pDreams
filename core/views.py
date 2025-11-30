from django.shortcuts import render
from library.models import Game
from hardware.models import Hardware
from .models import NetworkVideo, UserProfile
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from itertools import chain
from operator import attrgetter
from blog.models import Post
from django.contrib import messages
from .forms import UserUpdateForm, ProfileUpdateForm


def home(request):
    # ROW 1: New Videos
    new_videos = NetworkVideo.objects.order_by('-created_at')[:8]

    # --- FETCH DATA ---
    # 1. Games (Only show OWNED games, hide wishlist/ghosts)
    recent_games = list(Game.objects.filter(own_game=True).order_by('-created_at')[:10])
    updated_games = list(Game.objects.filter(own_game=True).order_by('-updated_at')[:10])

    # 2. Hardware (Fetch all)
    # <--- THESE LINES WERE MISSING/BROKEN --->
    recent_hardware = list(Hardware.objects.order_by('-created_at')[:10])
    updated_hardware = list(Hardware.objects.order_by('-updated_at')[:10])
    latest_news = Post.objects.filter(is_published=True)[:3]

    # --- TAG DATA ---
    for g in recent_games: g.kind = 'game'
    for h in recent_hardware: h.kind = 'hardware'

    for g in updated_games: g.kind = 'game'
    for h in updated_hardware: h.kind = 'hardware'

    # --- MERGE & SORT ---
    # Recent Acquisitions
    recent_acquisitions = sorted(
        recent_games + recent_hardware,
        key=attrgetter('created_at'),
        reverse=True
    )[:8]

    # Recently Updated
    recently_updated = sorted(
        updated_games + updated_hardware,
        key=attrgetter('updated_at'),
        reverse=True
    )[:8]

    context = {
        'new_videos': new_videos,
        'recent_acquisitions': recent_acquisitions,
        'recently_updated': recently_updated,
        'latest_news': latest_news,
    }
    return render(request, 'core/home.html', context)


def about(request):
    return render(request, 'core/about.html')


def hardware(request):
    # This is a placeholder if you haven't linked the main hardware url yet
    return render(request, 'core/hardware.html')


@login_required
def update_theme(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_theme = data.get('theme')

            # Self-Healing Profile Logic
            profile, created = UserProfile.objects.get_or_create(user=request.user)

            profile.theme = new_theme
            profile.save()
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error'}, status=400)


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('core:profile')  # Redirect prevents "Confirm Resubmission" on refresh

    else:
        u_form = UserUpdateForm(instance=request.user)
        # Ensure profile exists (Self-Healing in case it's missing)
        if not hasattr(request.user, 'profile'):
            UserProfile.objects.create(user=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'core/profile.html', context)


@login_required
def vault(request):
    return render(request, 'core/vault.html')