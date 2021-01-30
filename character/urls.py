from django.urls import path
from .views import character_selection

app_name = 'character'
urlpatterns = [
    path('character_selection/', character_selection, name='character_selection'),

]