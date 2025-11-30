from django.shortcuts import render, get_object_or_404
from .models import Game, Platform
from .filters import GameFilter


def game_list(request):
    # 1. Get Base Queryset
    all_games = Game.objects.all().order_by('title')

    # DEBUG PRINT: Check logs to see this number
    print(f"DEBUG: Total Games in Database: {all_games.count()}")

    # 2. Apply Filter (But we will ignore the result for a second)
    my_filter = GameFilter(request.GET, queryset=all_games)

    if not my_filter.is_valid():
        print(f"DEBUG: Filter Errors: {my_filter.errors}")

    # 3. FORCE DATA (Bypass filter to see if data exists)
    # If this works, we know the database is fine and the Filter is the culprit.
    # If this is still empty, your database is empty.
    games = all_games

    # Get Platforms (For the icon bar)
    platforms = Platform.objects.all().order_by('name')

    context = {
        'games': games,  # Sending RAW list (unfiltered)
        'filter': my_filter,  # Sending filter form (visuals only)
        'platforms': platforms,
        'debug_mode': True  # Flag for template
    }
    return render(request, 'library/game_list.html', context)

def game_detail(request, slug):
    game = get_object_or_404(Game, slug=slug)
    return render(request, 'library/game_detail.html', {'game': game})