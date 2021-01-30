import calendar
import datetime
from dateutil import relativedelta
from django.utils import timezone
import itertools
from collections import deque

from routine.models import TermDecision


class BaseCalendarMixin:
    """カレンダー関連Mixinの、基底クラス"""
    first_weekday = 0  # 0は月曜から、1は火曜から。6なら日曜日からになります。お望みなら、継承したビューで指定してください。
    week_names = ['月', '火', '水', '木', '金', '土', '日']  # これは、月曜日から書くことを想定します。['Mon', 'Tue'...

    def setup_calendar(self):
        """内部カレンダーの設定処理

        calendar.Calendarクラスの機能を利用するため、インスタンス化します。
        Calendarクラスのmonthdatescalendarメソッドを利用していますが、デフォルトが月曜日からで、
        火曜日から表示したい(first_weekday=1)、といったケースに対応するためのセットアップ処理です。

        """
        self._calendar = calendar.Calendar(self.first_weekday)

    def get_week_names(self):
        """first_weekday(最初に表示される曜日)にあわせて、week_namesをシフトする"""
        week_names = deque(self.week_names)
        week_names.rotate(-self.first_weekday)  # リスト内の要素を右に1つずつ移動...なんてときは、dequeを使うと中々面白いです
        return week_names

    def get_term_date(self):
        """ ルーティン期間を取得します。　なければ現在から3か月後までで作成します。 """
        # ルーティン期間オブジェクトがあれば取り出します。
        if TermDecision.objects.filter(user=self.request.user).exists():
            return TermDecision.objects.get(user=self.request.user)

        today = timezone.now()
        after_3_month = today + relativedelta.relativedelta(months=3)
        return TermDecision.objects.create(start_date=today, end_date=after_3_month, user=self.request.user)


class MonthCalendarMixin(BaseCalendarMixin):
    """月間カレンダーの機能を提供するMixin"""

    def get_previous_month(self, date):
        """前月を返す"""
        if date.month == 1:
            return date.replace(year=date.year-1, month=12, day=1)
        else:
            return date.replace(month=date.month-1, day=1)

    def get_next_month(self, date):
        """次月を返す"""
        if date.month == 12:
            return date.replace(year=date.year+1, month=1, day=1)
        else:
            return date.replace(month=date.month+1, day=1)

    def get_month_days(self, date):
        """その月の全ての日を返す"""
        return self._calendar.monthdatescalendar(date.year, date.month)

    def get_current_month(self):
        """現在の月を返す"""
        month = self.kwargs.get('month')
        year = self.kwargs.get('year')
        if month and year:
            month = datetime.date(year=int(year), month=int(month), day=1)
        else:
            month = datetime.date.today().replace(day=1)
        return month

    def get_month_calendar(self):
        """月間カレンダー情報の入った辞書を返す
        views.pyでの[MonthCalendar]でコンテキストとして返される
        """
        self.setup_calendar()
        current_month = self.get_current_month()
        calendar_data = {
            'now': datetime.date.today(),
            'month_days': self.get_month_days(current_month),
            'month_current': current_month,
            'month_previous': self.get_previous_month(current_month),
            'month_next': self.get_next_month(current_month),
            'week_names': self.get_week_names(),
        }
        return calendar_data


class MonthWithScheduleMixin(MonthCalendarMixin):
    """スケジュール付きの、月間カレンダーを提供するMixin"""

    def get_month_schedules(self, days):
        """それぞれの日とスケジュールを返す"""
        user = self.request.user

        # ルーティン期間を取得します。
        term_date = self.get_term_date()

        # コンテキストのvalueとなる辞書を作る
        day_schedules = {}

        # 月の週ごとの日付リストを取り出してさらにそこから一日ずつ取り出して処理
        # {1日のdatetime: 1日のスケジュール全て, 2日のdatetime: 2日の全て...}のような辞書を作る
        for one_week in days:
            for day in one_week:
                week = self.week_names[day.weekday()] + '曜日'  # day が何曜日が取得する
                # objects.filter　を使っているのでクエリセットがない場合、空のクエリセットを返します
                dt_bp_objects = self.model.objects.filter(date=day, user=user)  # 日付がdayの日付指定のクエリセットを取得
                wd_bp_objects = self.model.objects.filter(week=week, user=user)  # 曜日がweekの日付指定のクエリセットを取得

                #  一週間を一日ずつ取り出して、その日付のスケジュールリスト（またはクエリセット）をday_schedules[day]に格納する
                #  例：　{2020/11/25 : [week='水曜日'の部位オブジェクト一つ目, week='水曜日'の部位オブジェクト二つ目,....],{2020/....}
                if wd_bp_objects:  # ルーティンのクエリセットが存在する場合
                    if term_date.judge_term_date(date=day):
                        if not dt_bp_objects:  # ルーティンのクエリセットのみの場合
                            day_schedules[day] = wd_bp_objects
                        # ルーティンのクエリセットとpartがNoneではない日付指定のクエリセットが存在する場合
                        elif None not in [dt_bp_object.part for dt_bp_object in dt_bp_objects]:
                            bp_objects = [dt_bp_object for dt_bp_object in dt_bp_objects]
                            for wd_bp_object in wd_bp_objects:
                                bp_objects.append(wd_bp_object)
                            day_schedules[day] = bp_objects
                        else:  # ルーティンのクエリセットとpartがNoneの日付指定のクエリセットが存在する場合
                            day_schedules[day] = dt_bp_objects.exclude(part=None)
                    else:
                        day_schedules[day] = dt_bp_objects.exclude(part=None)
                else:  # 日付指定のクエリセットのみの場合
                    day_schedules[day] = dt_bp_objects.exclude(part=None)

        # day_schedules辞書を、周毎に分割する。[{1日: 1日のスケジュール...}, {8日: 8日のスケジュール...}, ...]
        # 7個ずつ取り出して分割しています。
        size = len(day_schedules)

        return [{key: day_schedules[key] for key in itertools.islice(day_schedules, i, i+7)} for i in range(0, size, 7)]

    def get_month_calendar(self):
        calendar_context = super().get_month_calendar()
        month_days = calendar_context['month_days']
        calendar_context['month_day_schedules'] = self.get_month_schedules(
            month_days,
        )

        return calendar_context
