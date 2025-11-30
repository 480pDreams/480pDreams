import django_filters
from django import forms
from django.db.models import Q
from .models import Game, Platform, Genre, Region, Developer, Publisher


class GameFilter(django_filters.FilterSet):
    # 1. TOP SECTION
    title = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Search Title',
        widget=forms.TextInput(attrs={'placeholder': 'Enter title...'})
    )

    platform = django_filters.ModelMultipleChoiceFilter(
        queryset=Platform.objects.all(),
        label='Platform'
    )

    # Date Range with Calendar Widget
    release_date = django_filters.DateFromToRangeFilter(
        field_name='release_date',
        label='Release Date',
        widget=django_filters.widgets.RangeWidget(attrs={'type': 'date'})
    )

    # 2. MIDDLE SECTION (Multi-Selects)
    developers = django_filters.ModelMultipleChoiceFilter(queryset=Developer.objects.all(), label='Developer')
    publishers = django_filters.ModelMultipleChoiceFilter(queryset=Publisher.objects.all(), label='Publisher')
    regions = django_filters.ModelMultipleChoiceFilter(queryset=Region.objects.all(), label='Region')
    genres = django_filters.ModelMultipleChoiceFilter(queryset=Genre.objects.all(), label='Genre')

    # 3. BOTTOM SECTION (Booleans)

    # "In Collection" (Own Game)
    own_game = django_filters.BooleanFilter(label='In Collection', widget=forms.CheckboxInput)

    # "Missing Box" -> We check if own_box is False
    missing_box = django_filters.BooleanFilter(method='filter_missing_box', label='Missing Box',
                                               widget=forms.CheckboxInput)

    # "Missing Manual" -> We check if own_manual is False
    missing_manual = django_filters.BooleanFilter(method='filter_missing_manual', label='Missing Manual',
                                                  widget=forms.CheckboxInput)

    has_playthrough = django_filters.BooleanFilter(field_name='video_playthrough', lookup_expr='isnull', exclude=True,
                                                   label='Has Playthrough', widget=forms.CheckboxInput)

    has_review = django_filters.BooleanFilter(method='filter_has_review', label='Has Review',
                                              widget=forms.CheckboxInput)

    has_unboxing = django_filters.BooleanFilter(field_name='video_condition', lookup_expr='isnull', exclude=True,
                                                label='Has Unboxing/Condition Video', widget=forms.CheckboxInput)

    has_extras = django_filters.BooleanFilter(method='filter_has_extras', label='Has Member Content',
                                              widget=forms.CheckboxInput)

    # 4. SORTING
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
        label='Sort By'
    )

    class Meta:
        model = Game
        fields = []

    # Custom Logic
    def filter_missing_box(self, queryset, name, value):
        return queryset.filter(own_box=False) if value else queryset

    def filter_missing_manual(self, queryset, name, value):
        return queryset.filter(own_manual=False) if value else queryset

    def filter_has_review(self, queryset, name, value):
        return queryset.filter(Q(written_review__gt='') | Q(video_review__isnull=False)) if value else queryset

    def filter_has_extras(self, queryset, name, value):
        return queryset.filter(extra_videos__is_patron_only=True).distinct() if value else queryset