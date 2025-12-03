from django.urls import path
from . import views

app_name = 'comments'

urlpatterns = [
    path('add/<int:content_type_id>/<int:object_id>/', views.add_comment, name='add_comment'),
]