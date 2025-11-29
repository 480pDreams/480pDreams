import django_filters
from django import forms
from .models import Game, Platform, Genre


class GameFilter(django_filters.FilterSet):
    # Search by Title (contains text)
    title = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Search Title',
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Silent Hill'})
    )

    # Filter by Platform
    platform = django_filters.ModelChoiceFilter(
        queryset=Platform.objects.all(),
        label='Platform'
    )

    # Filter by Genre
    genres = django_filters.ModelMultipleChoiceFilter(
        queryset=Genre.objects.all(),
        label='Genre'
    )

    # The New "Owned" Toggle
    # This looks at the 'own_game' boolean we just made
    own_game = django_filters.BooleanFilter(
        label='Owned (Disc/Cart)',
        widget=forms.Select(choices=[
            (None, 'Show All (Including Ghosts)'),
            (True, 'Owned Only'),
            (False, 'Wishlist / Ghosts Only')
        ])
    )

    class Meta:
        model = Game
        fields = ['title', 'platform', 'genres', 'own_game']