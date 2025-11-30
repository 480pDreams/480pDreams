from django.shortcuts import render, get_object_or_404
from .models import Game, Platform
from .filters import GameFilter


def game_list(request):
    # 1. Get Base Queryset
    all_games = Game.objects.all().order_by('title')

    # 2. Apply Filter
    my_filter = GameFilter(request.GET, queryset=all_games)
    games = my_filter.qs

    # 3. Get Platforms (For the icon bar)
    platforms = Platform.objects.all().order_by('name')

    context = {
        'games': games,
        'filter': my_filter,
        'platforms': platforms,  # <--- Crucial: Pass this to the template!
    }
    return render(request, 'library/game_list.html', context)

def game_detail(request, slug):
    game = get_object_or_404(Game, slug=slug)
    return render(request, 'library/game_detail.html', {'game': game})