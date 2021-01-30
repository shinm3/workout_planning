from django.urls import path
from .views import Home

app_name = 'home'
urlpatterns = [
    path('home/', Home.as_view(), name='home'),
    path('home/<int:year>/<int:month>/<int:day>/', Home.as_view(), name='home'),
]
