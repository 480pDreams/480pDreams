from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('mainframe/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('core.urls')),
    path('library/', include('library.urls')),
    path('hardware/', include('hardware.urls')),
    path('blog/', include('blog.urls')),
    path('membership/', include('membership.urls')),
    path('comments/', include('comments.urls')),
]
