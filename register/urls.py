from django.urls import path
from .views import (
    Top, Login, Logout, user_create, UserCreateDone, UserCreateComplete,
    UserDetail, PasswordChange, PasswordChangeDone, PasswordReset, PasswordResetDone,
    PasswordResetConfirm, PasswordResetComplete, user_data_input, user_data_confirm,
    EmailChange, EmailChangeDone, EmailChangeComplete, PhoneChange, PhoneChangeDone,
    NameChange, NameChangeDone
)

app_name = 'register'

urlpatterns = [
    path('', Top.as_view(), name='top'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('user_create/', user_create, name='user_create'),
    path('user_create/done', UserCreateDone.as_view(), name='user_create_done'),
    path('user_create/complete/<token>/', UserCreateComplete.as_view(), name='user_create_complete'),
    path('user_detail/<int:pk>/', UserDetail.as_view(), name='user_detail'),
    path('password_change/', PasswordChange.as_view(), name='password_change'),
    path('password_change/done/', PasswordChangeDone.as_view(), name='password_change_done'),
    path('password_reset/', PasswordReset.as_view(), name='password_reset'),
    path('password_reset/done/', PasswordResetDone.as_view(), name='password_reset_done'),
    path('password_reset/confirm/<uidb64>/<token>/', PasswordResetConfirm.as_view(),
         name='password_reset_confirm'),
    path('password_reset/complete/', PasswordResetComplete.as_view(), name='password_reset_complete'),
    path('user_data_input/', user_data_input, name='user_data_input'),
    path('user_data_confirm/', user_data_confirm, name='user_data_confirm'),
    path('email/change/', EmailChange.as_view(), name='email_change'),
    path('email/change/done/', EmailChangeDone.as_view(), name='email_change_done'),
    path('email/change/complete/<str:token>/', EmailChangeComplete.as_view(), name='email_change_complete'),
    path('phone_change/<int:pk>/', PhoneChange.as_view(), name='phone_change'),
    path('phone_change/done/', PhoneChangeDone.as_view(), name='phone_change_done'),
    path('name_change/<int:pk>/', NameChange.as_view(), name='name_change'),
    path('name_change/done/', NameChangeDone.as_view(), name='name_change_done'),
]
