from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Game, Platform
from .filters import GameFilter


def game_list(request):
    all_games = Game.objects.all().order_by('title')
    my_filter = GameFilter(request.GET, queryset=all_games)

    if my_filter.is_valid():
        qs = my_filter.qs
    else:
        qs = all_games

    # PAGINATION: 20 items
    paginator = Paginator(qs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    platforms = Platform.objects.all().order_by('name')

    context = {
        'games': page_obj,  # Pass the Page Object, not the raw list
        'filter': my_filter,
        'platforms': platforms,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'library/partials/game_grid.html', context)

    return render(request, 'library/game_list.html', context)


def game_detail(request, slug):
    game = get_object_or_404(Game.objects.prefetch_related('regional_releases'), slug=slug)
    return render(request, 'library/game_detail.html', {'game': game})