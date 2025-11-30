from django.shortcuts import render, get_object_or_404
from .models import Hardware
from .filters import HardwareFilter


def hardware_list(request):
    all_hardware = Hardware.objects.all().order_by('name')
    my_filter = HardwareFilter(request.GET, queryset=all_hardware)

    if my_filter.is_valid():
        items = my_filter.qs
    else:
        items = all_hardware

    context = {
        'items': items,
        'filter': my_filter
    }

    # HTMX Support
    if request.headers.get('HX-Request'):
        return render(request, 'hardware/partials/hardware_grid.html', context)

    return render(request, 'hardware/hardware_list.html', context)


def hardware_detail(request, slug):
    item = get_object_or_404(Hardware, slug=slug)
    return render(request, 'hardware/hardware_detail.html', {'item': item})