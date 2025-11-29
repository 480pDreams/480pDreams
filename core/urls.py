from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('hardware/', views.hardware, name='hardware'),
    path('api/update-theme/', views.update_theme, name='update_theme'),
]