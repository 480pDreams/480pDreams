from django.shortcuts import render, get_object_or_404
from .models import Hardware, HardwareType
from .filters import HardwareFilter
from library.models import Platform, Region


def hardware_list(request):
    # 1. Base Query
    all_items = Hardware.objects.all().order_by('name')

    # DEBUG: Is the DB empty?
    print(f"DEBUG: Hardware Count (Raw): {all_items.count()}")

    # 2. Filter
    my_filter = HardwareFilter(request.GET, queryset=all_items)

    if my_filter.is_valid():
        items = my_filter.qs
    else:
        items = all_items

    # 3. Context
    types = HardwareType.objects.all().order_by('name')
    platforms = Platform.objects.all().order_by('name')
    regions = Region.objects.all().order_by('name')

    context = {
        'items': items,
        'filter': my_filter,
        'types': types,
        'platforms': platforms,
        'regions': regions,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'hardware/partials/hardware_grid.html', context)

    return render(request, 'hardware/hardware_list.html', context)


def hardware_detail(request, slug):
    item = get_object_or_404(Hardware, slug=slug)
    return render(request, 'hardware/hardware_detail.html', {'item': item})