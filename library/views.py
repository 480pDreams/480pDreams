from django.shortcuts import render, get_object_or_404
from .models import Game, Platform
from .filters import GameFilter


def game_list(request):
    all_games = Game.objects.all().order_by('title')
    my_filter = GameFilter(request.GET, queryset=all_games)

    # DEBUG: Check if filter is valid
    if not my_filter.is_valid():
        print("FILTER ERRORS:", my_filter.errors)
        # If invalid, we show all games instead of hiding them
        games = all_games
    else:
        games = my_filter.qs

    platforms = Platform.objects.all().order_by('name')

    context = {
        'games': games,
        'filter': my_filter,
        'platforms': platforms,
    }
    return render(request, 'library/game_list.html', context)

def game_detail(request, slug):
    game = get_object_or_404(Game, slug=slug)
    return render(request, 'library/game_detail.html', {'game': game})