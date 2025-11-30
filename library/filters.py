import django_filters
from django import forms
from django.db.models import Q
from .models import Game, Platform, Genre, Region


class GameFilter(django_filters.FilterSet):
    # 1. SEARCH
    title = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Title Search',
        widget=forms.TextInput(attrs={'placeholder': 'Search games...'})
    )

    # 2. PLATFORM (We handle the Icons in the template, but this logic is needed backend)
    platform = django_filters.ModelMultipleChoiceFilter(
        queryset=Platform.objects.all(),
        label='Platform'
    )

    # 3. METADATA FILTERS
    developer = django_filters.CharFilter(lookup_expr='icontains', label='Developer')
    publisher = django_filters.CharFilter(lookup_expr='icontains', label='Publisher')

    # Date Range (Year)
    release_year_min = django_filters.NumberFilter(field_name='release_date', lookup_expr='year__gte',
                                                   label='Year (From)')
    release_year_max = django_filters.NumberFilter(field_name='release_date', lookup_expr='year__lte',
                                                   label='Year (To)')

    region = django_filters.ModelChoiceFilter(queryset=Region.objects.all(), label='Region')
    genres = django_filters.ModelMultipleChoiceFilter(queryset=Genre.objects.all(), label='Genre')

    # 4. CONTENT & STATUS
    # "Has Review" checks if EITHER video OR written review exists
    has_review = django_filters.BooleanFilter(method='filter_has_review', label='Has Review')

    has_playthrough = django_filters.BooleanFilter(field_name='video_playthrough', lookup_expr='isnull', exclude=True,
                                                   label='Has Playthrough')

    # "CIB" Check (Game + Box + Manual)
    is_cib = django_filters.BooleanFilter(method='filter_is_cib', label='Complete (CIB)')

    # 5. SORTING
    ordering = django_filters.OrderingFilter(
        fields=(
            ('title', 'title'),
            ('release_date', 'release_date'),
            ('created_at', 'date_added'),
        ),
        field_labels={
            'title': 'Alphabetical (A-Z)',
            'release_date': 'Release Date',
            'created_at': 'Date Added (Default)',
        },
        label='Sort By'
    )

    class Meta:
        model = Game
        fields = []

    # Custom Filter Logic
    def filter_has_review(self, queryset, name, value):
        if value:
            return queryset.filter(Q(written_review__gt='') | Q(video_review__isnull=False))
        return queryset

    def filter_is_cib(self, queryset, name, value):
        if value:
            return queryset.filter(own_game=True, own_box=True, own_manual=True)
        return queryset