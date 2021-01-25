# それぞれのトレーニング部位の曜日,日付をリストで取得
#  queryset = self.model.objects.filter(user=user)
        # week_day_list = self.model.objects.filter(user=user).values_list('week', flat=True)
        # date_list = self.model.objects.filter(user=user).values_list('date', flat=True)
        # none_bp_objects = self.model.objects.filter(part=None, date=day, user=user)  # 部位がNoneのクエリセットを取得
# 日付がdayの日付指定のクエリセットがあればその最新のpkを取得する
#  if dt_bp_objects:
#   latest_day_pk = self.model.objects.filter(date=day, user=user).order_by('-pk').first().pk
                # else:  # なければ、latest_day_pkは0にする
#     latest_day_pk = 0
#  if none_bp_objects:  # 部位がNoneで日付がdayの日付指定のクエリセットがあればその最新のpkを取得する
#     latest_none_pk = self.model.objects.filter(part=None, date=day, user=user).order_by('-pk').first().pk
                # else:  # なければ、latest_day_pkは0にする
#      latest_none_pk = 0
#  if self.model.objects.filter(week=week, user=user):  # dayの曜日のルーティンクエリセットがあればその最新のpkを取得する
#      latest_routine_pk = self.model.objects.filter(week=week, user=user).order_by('-pk').first().pk
               #  else:  # なければ、latest_day_pkは0にする
#       latest_routine_pk = 0
                # 部位がNoneで日付がdayの日付指定のクエリセットの最新pkよりdayの曜日のルーティンクエリセットの最新pkが大きければ
                # 部位がNoneで日付がdayの日付指定のクエリセットは削除する。
#    if latest_none_pk < latest_routine_pk:
#       none_bp_objects.delete()

                    # 日付がdayの日付指定のクエリセットの最新pkよりdayの曜日のルーティンクエリセットの最新pkが大きければ
                    # 日付がdayの日付指定のクエリセットは削除する。
#    if term_date.judge_term_date(date=day):
#       if latest_day_pk < latest_routine_pk and latest_day_pk != 0:
#           dt_bp_objects.delete()


# 全てのルーティンオブジェクトのweekの値のリストに　dayの曜日があり、
#        if week in week_day_list:
                    # dayの曜日のルーティンクエリセットの最新pkより部位がNoneで日付がdayの日付指定のクエリセットの最新pkが大きければ
#          if latest_none_pk > latest_routine_pk:
#                for schedule in queryset:
#                  schedule_date = getattr(schedule, self.date_field)
#                 if schedule_date == day and schedule.part is not None:
#                     day_schedules[day].append(schedule)
             #        elif latest_none_pk == 0:
#            for schedule in queryset:
#             schedule_date = getattr(schedule, self.date_field)
#            schedule_week = getattr(schedule, self.week_field)
#             if schedule_date == day and schedule.part is not None:
#                day_schedules[day].append(schedule)
                 #            elif schedule_week == week and schedule.part is not None:
#               if term_date.start_date <= day <= term_date.end_date:
#                      day_schedules[day].append(schedule)
              #       elif day not in date_list:
#           if term_date.start_date <= day <= term_date.end_date:
#               for schedule in queryset:
#                   if schedule.week:
#                       schedule_week = getattr(schedule, self.week_field)
#                      key = [i for i, week in enumerate(self.week_names) if week + '曜日' == schedule_week][0]
#                      if day.weekday() == key:
#                         day_schedules[day].append(schedule)
              #   else:
#       for schedule in queryset:
#          schedule_date = getattr(schedule, self.date_field)
#           if schedule_date == day and schedule.part is not None:
#              day_schedules[day].append(schedule)