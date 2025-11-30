from django.shortcuts import render, get_object_or_404
from .models import Game, Platform
from .filters import GameFilter


def game_list(request):
    # 1. Get Base Queryset
    all_games = Game.objects.all().order_by('title')

    # 2. Apply Filter
    my_filter = GameFilter(request.GET, queryset=all_games)

    # 3. Use the Filtered Result (This was the fix!)
    if my_filter.is_valid():
        games = my_filter.qs
    else:
        # If inputs are weird (like ?year=abc), show all
        games = all_games

    # 4. Get Platforms (For the icon bar)
    platforms = Platform.objects.all().order_by('name')

    context = {
        'games': games,
        'filter': my_filter,
        'platforms': platforms,
    }
    return render(request, 'library/game_list.html', context)


# ... (Keep game_detail view as is) ...
def game_detail(request, slug):
    game = get_object_or_404(Game, slug=slug)
    return render(request, 'library/game_detail.html', {'game': game})