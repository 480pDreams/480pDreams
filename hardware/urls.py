from django.urls import path
from . import views

app_name = 'hardware'

urlpatterns = [
    path('', views.hardware_list, name='hardware_list'),
    path('<slug:slug>/', views.hardware_detail, name='hardware_detail'),
]