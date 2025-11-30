import django_filters
from django import forms
from django.db.models import Q
from .models import Game, Platform, Genre, Region, Developer, Publisher


class GameFilter(django_filters.FilterSet):
    # 1. SEARCH
    title = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Search Title',
    )

    # 2. PLATFORM (Icon Bar)
    # conjoined=False means OR logic (Platform A OR Platform B)
    platform = django_filters.ModelMultipleChoiceFilter(
        queryset=Platform.objects.all(),
        label='Platform',
        conjoined=False
    )

    # 3. METADATA FILTERS (Tom Select Chips)
    # distinct=True is CRITICAL for Many-to-Many relationships to prevent duplicates
    developers = django_filters.ModelMultipleChoiceFilter(queryset=Developer.objects.all(), distinct=True)
    publishers = django_filters.ModelMultipleChoiceFilter(queryset=Publisher.objects.all(), distinct=True)
    regions = django_filters.ModelMultipleChoiceFilter(queryset=Region.objects.all(), distinct=True)
    genres = django_filters.ModelMultipleChoiceFilter(queryset=Genre.objects.all(), distinct=True)

    # 4. DATE RANGE (Matches HTML inputs: release_year_min / release_year_max)
    release_year_min = django_filters.NumberFilter(field_name='release_date', lookup_expr='year__gte')
    release_year_max = django_filters.NumberFilter(field_name='release_date', lookup_expr='year__lte')

    # 5. CHECKBOXES
    # Standard Boolean filters for the toggles
    own_game = django_filters.BooleanFilter(method='filter_own_game', widget=forms.CheckboxInput)
    missing_box = django_filters.BooleanFilter(method='filter_missing_box', widget=forms.CheckboxInput)
    missing_manual = django_filters.BooleanFilter(method='filter_missing_manual', widget=forms.CheckboxInput)

    # Content Checks
    has_playthrough = django_filters.BooleanFilter(field_name='video_playthrough', lookup_expr='isnull', exclude=True,
                                                   widget=forms.CheckboxInput)
    has_review = django_filters.BooleanFilter(method='filter_has_review', widget=forms.CheckboxInput)
    has_unboxing = django_filters.BooleanFilter(field_name='video_condition', lookup_expr='isnull', exclude=True,
                                                widget=forms.CheckboxInput)
    has_extras = django_filters.BooleanFilter(method='filter_has_extras', widget=forms.CheckboxInput)

    # 6. SORTING
    ordering = django_filters.OrderingFilter(
        fields=(
            ('title', 'title'),
            ('release_date', 'release_date'),
            ('created_at', 'date_added'),
        ),
        field_labels={
            'title': 'Alphabetical',
            'release_date': 'Release Date',
            'created_at': 'Date Added',
        },
    )

    class Meta:
        model = Game
        fields = []

    # --- CUSTOM LOGIC METHODS ---

    def filter_own_game(self, queryset, name, value):
        # If checked, show owned. If unchecked, show ALL (ignore filter).
        return queryset.filter(own_game=True) if value else queryset

    def filter_missing_box(self, queryset, name, value):
        return queryset.filter(own_box=False) if value else queryset

    def filter_missing_manual(self, queryset, name, value):
        return queryset.filter(own_manual=False) if value else queryset

    def filter_has_review(self, queryset, name, value):
        # Checks if either Written Review OR Video Review exists
        return queryset.filter(Q(written_review__gt='') | Q(video_review__isnull=False)) if value else queryset

    def filter_has_extras(self, queryset, name, value):
        # Checks if there are any videos marked 'is_patron_only'
        return queryset.filter(extra_videos__is_patron_only=True).distinct() if value else queryset