from django.utils import timezone

from . import models


def factory_user(**kwargs):
    d = {
        'email': 'test@test.com',
        'first_name': '名',
        'last_name': '姓',
        'is_staff': False,
        'is_active': True,
        'date_joined': timezone.now
    }
    password = kwargs.pop('password', None)
    d.update(kwargs)
    user = models.User(**d)
    if password:
        user.set_password(password)
    user.save()
    return user
