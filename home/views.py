from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views import generic
from .mixins import WeekWithScheduleMixin
from routine.models import BodyPart
from character.models import Character

# Create your views here.


class Home(LoginRequiredMixin, WeekWithScheduleMixin, generic.TemplateView):
    """週間カレンダーを表示するビュー"""
    template_name = 'home.html'
    model = BodyPart
    week_field = 'week'
    date_field = 'date'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        calendar_context = self.get_week_calendar()
        context.update(calendar_context)
        calendar_context = self.get_today_schedules()
        context.update(calendar_context)
        calendar_context = self.get_today_num()
        context.update(calendar_context)
        calendar_context = {'page_title': 'ホーム', 'breadcrumb_list': None}
        context.update(calendar_context)
        user = self.request.user
        if Character.objects.filter(user=user):  # 既にキャラクターの設定がされている場合
            character = get_object_or_404(Character, user=user)
            character_serif = 'character_serif/character' + character.number + '.html'
        else:  # キャラクター初期設定
            character = Character.objects.create(name='ボディビルダー', number='1', user=user)
            character_serif = 'character_serif/character1.html'

        calendar_context = {'character': character,
                            'character_serif': character_serif,
                            }
        context.update(calendar_context)
        return context

