from .models import TermDecision
from ..register.testing import factory_user
import datetime


def factory_term_decision(**kwargs):
    """ テスト用のterm_decisionのデータを作る
    """
    d = {
        'start_date': datetime.datetime(2020, 9, 1),
        'end_date': datetime.datetime(2020, 12, 1),
        'user': factory_user()
    }

    return TermDecision.objects.create(**d)
