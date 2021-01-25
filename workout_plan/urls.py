from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('register.urls')),
    path('', include('routine.urls')),
    path('', include('home.urls')),
    path('', include('tr_calendar.urls')),
    path('', include('discipline.urls')),
    path('', include('character.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + \
              static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)