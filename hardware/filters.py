import django_filters
from django import forms
from .models import Hardware, HardwareType
from library.models import Platform, Region


class HardwareFilter(django_filters.FilterSet):
    # 1. SEARCH
    name = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Search Name'
    )

    # 2. DROPDOWNS (Set conjoined=False to handle empty/OR logic correctly)
    type = django_filters.ModelMultipleChoiceFilter(
        queryset=HardwareType.objects.all(),
        conjoined=False
    )
    platform = django_filters.ModelMultipleChoiceFilter(
        queryset=Platform.objects.all(),
        conjoined=False
    )
    regions = django_filters.ModelMultipleChoiceFilter(
        queryset=Region.objects.all(),
        conjoined=False
    )

    # 3. DATE RANGE
    release_date_min = django_filters.DateFilter(field_name='release_date', lookup_expr='gte')
    release_date_max = django_filters.DateFilter(field_name='release_date', lookup_expr='lte')

    # 4. BOOLEANS
    own_item = django_filters.BooleanFilter(method='filter_own_item', widget=forms.CheckboxInput)
    missing_box = django_filters.BooleanFilter(method='filter_missing_box', widget=forms.CheckboxInput)
    has_review = django_filters.BooleanFilter(method='filter_has_review', widget=forms.CheckboxInput)
    has_unboxing = django_filters.BooleanFilter(field_name='video_condition', lookup_expr='isnull', exclude=True,
                                                widget=forms.CheckboxInput)

    # 5. SORTING
    ordering = django_filters.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('release_date', 'release_date'),
            ('created_at', 'date_added'),
        ),
        field_labels={
            'name': 'Alphabetical',
            'release_date': 'Release Date',
            'created_at': 'Date Added',
        },
    )

    class Meta:
        model = Hardware
        fields = []

    # LOGIC
    def filter_own_item(self, queryset, name, value):
        return queryset.filter(own_item=True) if value else queryset

    def filter_missing_box(self, queryset, name, value):
        return queryset.filter(own_box=False) if value else queryset

    def filter_has_review(self, queryset, name, value):
        return queryset.filter(video_review__gt='') if value else queryset