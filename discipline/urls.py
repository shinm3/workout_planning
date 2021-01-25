from django.urls import path
from .views import day_schedule_discipline, discipline_create, discipline_update, discipline_delete

app_name = 'discipline'

urlpatterns = [
    path(
        'day_schedule_discipline/<int:pk>/<int:year>/<int:month>/<int:day>/',
        day_schedule_discipline, name='day_schedule_discipline'
    ),
    path(
        'discipline_create/<int:pk>/<int:year>/<int:month>/<int:day>/<int:new>/',
        discipline_create, name='discipline_create'
    ),
    path(
        'discipline_update/<int:pk>/<int:year>/<int:month>/<int:day>/',
        discipline_update, name='discipline_update'
    ),
    path(
        'discipline_delete/<int:year>/<int:month>/<int:day>/',
        discipline_delete, name='discipline_delete'
    )
]