import django_filters
from django import forms
from django.db.models import Q
from .models import Game, Platform, Genre, Region, Developer, Publisher


class GameFilter(django_filters.FilterSet):
    # 1. SEARCH
    title = django_filters.CharFilter(lookup_expr='icontains', label='Search Title')

    # 2. PLATFORM
    platform = django_filters.ModelMultipleChoiceFilter(
        queryset=Platform.objects.all(),
        label='Platform',
        conjoined=False
    )

    # 3. METADATA (M2M) - Added 'conjoined=False' to ensure OR logic
    developers = django_filters.ModelMultipleChoiceFilter(
        queryset=Developer.objects.all(),
        conjoined=False
    )
    publishers = django_filters.ModelMultipleChoiceFilter(
        queryset=Publisher.objects.all(),
        conjoined=False
    )
    regions = django_filters.ModelMultipleChoiceFilter(
        queryset=Region.objects.all(),
        conjoined=False
    )
    genres = django_filters.ModelMultipleChoiceFilter(
        queryset=Genre.objects.all(),
        conjoined=False
    )

    # 4. DATE RANGE
    release_year_min = django_filters.NumberFilter(field_name='release_date', lookup_expr='year__gte')
    release_year_max = django_filters.NumberFilter(field_name='release_date', lookup_expr='year__lte')

    # 5. BOOLEANS - Removing 'widget=CheckboxInput' temporarily to test logic
    # We will use standard dropdowns (Unknown/Yes/No) for a moment to debug the "Silent Fail"
    own_game = django_filters.BooleanFilter(method='filter_own_game')
    missing_box = django_filters.BooleanFilter(method='filter_missing_box')
    missing_manual = django_filters.BooleanFilter(method='filter_missing_manual')

    has_playthrough = django_filters.BooleanFilter(method='filter_has_playthrough')
    has_review = django_filters.BooleanFilter(method='filter_has_review')
    has_unboxing = django_filters.BooleanFilter(method='filter_has_unboxing')
    has_extras = django_filters.BooleanFilter(method='filter_has_extras')

    # 6. SORTING
    ordering = django_filters.OrderingFilter(
        fields=(
            ('title', 'title'),
            ('release_date', 'release_date'),
            ('created_at', 'date_added'),
        ),
        label='Sort By'
    )

    class Meta:
        model = Game
        fields = []

    # LOGIC METHODS (Simplified)
    def filter_own_game(self, queryset, name, value):
        return queryset.filter(own_game=True) if value else queryset

    def filter_missing_box(self, queryset, name, value):
        return queryset.filter(own_box=False) if value else queryset

    def filter_missing_manual(self, queryset, name, value):
        return queryset.filter(own_manual=False) if value else queryset

    def filter_has_playthrough(self, queryset, name, value):
        return queryset.filter(video_playthrough__gt='') if value else queryset

    def filter_has_unboxing(self, queryset, name, value):
        return queryset.filter(video_condition__gt='') if value else queryset

    def filter_has_review(self, queryset, name, value):
        return queryset.filter(Q(written_review__gt='') | Q(video_review__gt='')) if value else queryset

    def filter_has_extras(self, queryset, name, value):
        return queryset.filter(extra_videos__is_patron_only=True).distinct() if value else queryset