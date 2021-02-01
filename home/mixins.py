import datetime
from tr_calendar.mixins import BaseCalendarMixin


class WeekCalendarMixin(BaseCalendarMixin):
    """週間カレンダーの機能を提供するMixin"""

    def get_week_days(self):
        """その週の日を全て返す"""
        month = self.kwargs.get('month')
        year = self.kwargs.get('year')
        day = self.kwargs.get('day')
        if month and year and day:
            date = datetime.date(year=int(year), month=int(month), day=int(day))
        else:
            date = datetime.date.today()

        for week in self._calendar.monthdatescalendar(date.year, date.month):
            if date in week:  # 週ごとに取り出され、中身は全てdatetime.date型。該当の日が含まれていれば、それが今回表示すべき週です
                return week

    def get_week_calendar(self):
        """週間カレンダー情報の入った辞書を返す"""
        self.setup_calendar()
        days = self.get_week_days()
        first = days[0]
        last = days[-1]
        week_days_names = zip(days, self.get_week_names())
        calendar_data = {
            'now': datetime.date.today(),
            'week_days': days,
            'week_previous': first - datetime.timedelta(days=7),
            'week_next': first + datetime.timedelta(days=7),
            'week_names': self.get_week_names(),
            'week_first': first,
            'week_last': last,
            'week_days_names': week_days_names,
        }
        return calendar_data


class WeekWithScheduleMixin(WeekCalendarMixin):
    """スケジュール付きの、週間カレンダーを提供するMixin"""

    def get_week_schedules(self, days):
        """それぞれの日とスケジュールを返す"""
        user = self.request.user
        # ルーティン期間を取得します。
        term_date = self.get_term_date()

        # コンテキストのvalueとなる辞書を作る
        # {1日のdatetime: 1日のスケジュール全て, 2日のdatetime: 2日の全て...}のような辞書を作る
        day_schedules = {}
        for day in days:
            week = self.week_names[day.weekday()]
            dt_bp_objects = self.model.objects.filter(date=day, user=user)  # 日付指定のクエリセットを取得
            wd_bp_objects = self.model.objects.filter(week__startswith=week, user=user)  # ルーティンのクエリセットを取得

            #  一週間を一日ずつ取り出して、その日付のスケジュールリスト（またはクエリセット）をday_schedules[day]に格納する
            #  例：　{2020/11/25 : [week='水曜日'の部位オブジェクト一つ目, week='水曜日'の部位オブジェクト二つ目, ....],{2020/....}
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


        return day_schedules

    def get_week_calendar(self):
        """ self.get_week_schedules()から部位の順番ごとに一週間分を格納したリストを辞書にします。

        リストの中身は左から（表示される）週の始まりのCOUNT番目の部位となります。
        部位が設定されていない日付は何部位目でもNoneと表示されます。
        1部位以上設定されている日付で二部位目以降に部位設定がされていないと'temporary'となります。

        例：

            max_count = 2　の場合

        　　最初の一部位目　0: ['胸', None, '背中', None, '脚', '肩', None]
          最初の二部位目　1: ['腕', None, 'temporary', None, '腹筋', temporary', None]

        """

        calendar_context = super().get_week_calendar()
        day_schedules = self.get_week_schedules(
            calendar_context['week_days']
        )

        # 一週間の中で一番設定部位数が多い日の部位数を取得します
        max_count = 0
        for day_schedule in day_schedules.values():
            if len(day_schedule) > max_count:
                max_count = len(day_schedule)
        week_schedules = {}
        for count in range(max_count):
            week_schedules[count] = []  # リストにcount回目の一週間分の部位を格納する。
            for i, schedule in enumerate(day_schedules.values()):
                if len(schedule) >= (count + 1):  # count回目に部位設定されていれば
                    week_schedules[count].append(schedule[count])
                elif count > 0 and week_schedules[count - 1][i] is not None:  # 部位が設定されてなく同じ日付にNoneがなければ
                    week_schedules[count].append('temporary')
                else:  # 部位が設定されていなければ
                    week_schedules[count].append(None)

        calendar_context['week_day_schedules'] = week_schedules
        return calendar_context

    def get_today_schedules(self):
        date = datetime.date.today()
        next_date = date + datetime.timedelta(days=1)
        dates = [date, next_date]
        dates_schedules = self.get_week_schedules(dates)
        calendar_context = super().get_week_calendar()
        calendar_context['today_schedules'] = dates_schedules[date]
        return calendar_context

    def get_today_num(self):
        """ 曜日番号を作成してコンテキストに格納します """
        today = datetime.date.today()
        today_num = today.isoweekday()
        calendar_context = super().get_week_calendar()
        calendar_context['today_num'] = today_num

        return calendar_context


