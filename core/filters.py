import django_filters
from django import forms
from .models import NetworkVideo
from library.models import Platform


class VideoFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Search Title',
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Halo...'})
    )

    # Chips (Multi-select)
    channel = django_filters.MultipleChoiceFilter(
        choices=NetworkVideo.CHANNEL_CHOICES,
        conjoined=False
    )
    video_type = django_filters.MultipleChoiceFilter(
        choices=NetworkVideo.TYPE_CHOICES,
        conjoined=False,
        label="Content Type"
    )
    platform = django_filters.ModelMultipleChoiceFilter(
        queryset=Platform.objects.all(),
        conjoined=False
    )

    ordering = django_filters.OrderingFilter(
        fields=(('created_at', 'date'), ('title', 'title')),
        field_labels={'created_at': 'Date Added', 'title': 'Alphabetical'},
        label='Sort By'
    )

    class Meta:
        model = NetworkVideo
        fields = []