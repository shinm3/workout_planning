from django.urls import path
from .views import week_list, routine_create, routine_update, routine_delete, term_decision, routine_decision

app_name = 'routine'
urlpatterns = [
    path('term_decision/', term_decision, name='term_decision'),
    path('week_list/', week_list, name='list'),
    path('routine_create/<int:num>/', routine_create, name='create'),
    path('routine_update/<int:num>/<int:pid>/<int:form_num>/', routine_update, name='update'),
    path('routine_delete/', routine_delete, name='delete'),
    path('routine_delete/<int:num>/', routine_delete, name='delete'),
    path('routine_decision/', routine_decision, name='routine_decision'),

]
