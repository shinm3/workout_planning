from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('register.urls')),
    path('', include('routine.urls')),
    path('', include('home.urls')),
    path('', include('tr_calendar.urls')),
    path('', include('discipline.urls')),
    path('', include('character.urls')),
]
