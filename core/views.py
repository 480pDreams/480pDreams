from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from operator import attrgetter
import json

# Model Imports
from library.models import Game, Platform
from hardware.models import Hardware
from .models import NetworkVideo, UserProfile
from blog.models import Post

# Form & Filter Imports
from .forms import UserUpdateForm, ProfileUpdateForm
from .filters import VideoFilter

def home(request):
    # 1. New Videos (Top Row)
    new_videos = NetworkVideo.objects.order_by('-created_at')[:8]

    # 2. Latest Articles (Newsstand)
    latest_news = Post.objects.filter(is_published=True)[:3]

    # 3. Recent Acquisitions (Strict 30 Day Window)
    # Only show items acquired in the last 30 days
    cutoff_date = timezone.now().date() - timedelta(days=30)

    # Games: Must own game AND be acquired recently
    recent_games = list(
        Game.objects.filter(own_game=True, date_acquired__gte=cutoff_date).order_by('-date_acquired')[:8])
    # Hardware: Must own item AND be acquired recently
    recent_hardware = list(
        Hardware.objects.filter(own_item=True, date_acquired__gte=cutoff_date).order_by('-date_acquired')[:8])

    # Tag them so template knows which card style to use
    for g in recent_games: g.kind = 'game'
    for h in recent_hardware: h.kind = 'hardware'

    # Merge and sort by ACQUISITION date
    recent_acquisitions = sorted(
        recent_games + recent_hardware,
        key=attrgetter('date_acquired'),
        reverse=True
    )[:8]

    # 4. Recently Updated (Any edits to database)
    # Filter out ghosts (unowned items) so we only see collection updates
    updated_games = list(Game.objects.filter(own_game=True).order_by('-updated_at')[:8])
    updated_hardware = list(Hardware.objects.filter(own_item=True).order_by('-updated_at')[:8])

    for g in updated_games: g.kind = 'game'
    for h in updated_hardware: h.kind = 'hardware'

    recently_updated = sorted(
        updated_games + updated_hardware,
        key=attrgetter('updated_at'),
        reverse=True
    )[:8]

    context = {
        'new_videos': new_videos,
        'latest_news': latest_news,
        'recent_acquisitions': recent_acquisitions,
        'recently_updated': recently_updated,
    }
    return render(request, 'core/home.html', context)


def about(request):
    return render(request, 'core/about.html')


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('core:profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        # Ensure profile exists (Self-Healing)
        if not hasattr(request.user, 'profile'):
            UserProfile.objects.create(user=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'core/profile.html', context)


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
def vault(request):
    return render(request, 'core/vault.html')


def video_list(request):
    all_videos = NetworkVideo.objects.all().order_by('-created_at')
    my_filter = VideoFilter(request.GET, queryset=all_videos)

    if my_filter.is_valid():
        qs = my_filter.qs
    else:
        qs = all_videos

    # PAGINATION: 20 items
    paginator = Paginator(qs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    platforms = Platform.objects.all().order_by('name')

    context = {
        'videos': page_obj,  # Pass the Page Object
        'filter': my_filter,
        'platforms': platforms,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'core/partials/video_grid.html', context)

    return render(request, 'core/video_list.html', context)