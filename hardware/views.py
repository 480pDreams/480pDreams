from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Hardware, HardwareType
from .filters import HardwareFilter
from library.models import Platform, Region


def hardware_list(request):
    all_items = Hardware.objects.all().order_by('name')
    my_filter = HardwareFilter(request.GET, queryset=all_items)

    if my_filter.is_valid():
        qs = my_filter.qs
    else:
        qs = all_items

    # PAGINATION: 20 items
    paginator = Paginator(qs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    types = HardwareType.objects.all().order_by('name')
    platforms = Platform.objects.all().order_by('name')
    regions = Region.objects.all().order_by('name')

    context = {
        'items': page_obj,  # Pass the Page Object
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