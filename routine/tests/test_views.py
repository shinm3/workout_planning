from django.test import TestCase
from django.urls import reverse

from ..testing import factory_term_decision


class TestTermDecision(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.term = factory_term_decision()

    def _getTarget(self):
        return reverse('routine:term_decision')

    def test_get(self):
        session = self.client.session
        session['provisional'] = {'term_form_data': self.term}
        session.save()

        res = self.client.get(self._getTarget())
        self.assertTemplateUsed(res, 'term_decision.html')
        self.assertEqual(res.context['page_title'], 'ルーティン設定')
        self.assertEqual(res.context['form'].inctance, self.term)
