from django.shortcuts import render, get_object_or_404
from .models import Game
from .filters import GameFilter


def game_list(request):
    # 1. Get all games, ordered by title
    all_games = Game.objects.all().order_by('title')

    # 2. Feed them into the Filter
    # request.GET contains the search URL parameters (e.g. ?title=mario)
    my_filter = GameFilter(request.GET, queryset=all_games)

    # 3. Get the result
    games = my_filter.qs

    context = {
        'games': games,
        'filter': my_filter  # Pass the filter to the template so we can render the search bar
    }
    return render(request, 'library/game_list.html', context)

# New View
def game_detail(request, slug):
    game = get_object_or_404(Game, slug=slug)
    return render(request, 'library/game_detail.html', {'game': game})