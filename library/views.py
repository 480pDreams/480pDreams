from django.shortcuts import render, get_object_or_404
from .models import Game, Platform
from .filters import GameFilter


def game_list(request):
    all_games = Game.objects.all().order_by('title')
    my_filter = GameFilter(request.GET, queryset=all_games)
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