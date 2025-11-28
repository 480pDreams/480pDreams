from django.shortcuts import render, get_object_or_404
from .models import Hardware

def hardware_list(request):
    items = Hardware.objects.all().order_by('name')
    return render(request, 'hardware/hardware_list.html', {'items': items})

def hardware_detail(request, slug):
    item = get_object_or_404(Hardware, slug=slug)
    return render(request, 'hardware/hardware_detail.html', {'item': item})