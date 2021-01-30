from django.urls import path
from .views import MonthWithScheduleCalendar, day_schedule_create_or_detail, routine_day_delete, day_schedule_update, \
    day_schedule_update2

app_name = 'tr_calendar'

urlpatterns = [
    path(
        'month_with_schedule/',
        MonthWithScheduleCalendar.as_view(), name='month_with_schedule'
    ),
    path(
        'month_with_schedule/<int:year>/<int:month>/',
        MonthWithScheduleCalendar.as_view(), name='month_with_schedule'
    ),
    path(
        'day_schedule_create/<int:year>/<int:month>/<int:day>/',
        day_schedule_create_or_detail, name='day_schedule_create'
    ),
    path(
        'day_schedule_detail/<int:year>/<int:month>/<int:day>/<int:detail>/',
        day_schedule_create_or_detail, name='day_schedule_detail'
    ),
    path(
        'routine_day_delete/<int:year>/<int:month>/<int:day>/',
        routine_day_delete, name='routine_day_delete'
    ),
    path(
        'routine_day_delete/',
        routine_day_delete, name='routine_day_delete'
    ),
    path(
        'day_schedule_update/<int:pk>/',
        day_schedule_update, name='day_schedule_update'
    ),
    path(
        'day_schedule_update2/<int:pk>/<int:year>/<int:month>/<int:day>/',
        day_schedule_update2, name='day_schedule_update2'
    ),
]
