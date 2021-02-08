from django.shortcuts import render, redirect
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.conf import settings
from . import mixins
from routine.models import BodyPart, TermDecision
from .forms import DayBodyPartForm
from django.views.decorators.http import require_POST
import datetime
from django.utils import timezone


class MonthWithScheduleCalendar(LoginRequiredMixin, mixins.MonthWithScheduleMixin, generic.TemplateView):
    """月間カレンダーを表示するビュー"""
    template_name = 'calendar.html'
    model = BodyPart
    week_field = 'week'
    date_field = 'date'

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)
        calendar_context = self.get_month_calendar()
        context.update(calendar_context)
        all_objects = self.model.objects.filter(user=user)
        calendar_context = {'page_title': 'カレンダー', 'all_objects': all_objects,
                            'breadcrumb_root': True, 'breadcrumb_name': 'calendar',
                            }
        context.update(calendar_context)
        return context


@login_required
def day_schedule_create_or_detail(request, year, month, day, detail=None):
    """指定された日付のトレーニング部位を設定。（5部位まで設定可能）,または設定部位詳細ページへ遷移

    6部位目を設定しようとするとエラー表示されます

    ルーティンで設定したオブジェクト（weekフィールドに曜日が指定されているデータ）と
    日付指定のオブジェクト（dateフィールドに日付が指定されているデータ）とで処理を分けます。

    カレンダーページの新規作成からリンクされた場合、day_schedule_create.htmlへ遷移します。
    カレンダーページの新規作成からリンクされた場合、day_schedule_detaile.htmlへ遷移します。


    """
    user = request.user
    select_day = datetime.date(year=year, month=month, day=day)
    wd = settings.WEEK[select_day.weekday()]
    error = None
    bp_objects = BodyPart.objects.filter(user=user)

    # Noneのdateオブジェクトがあればその最新のレコードのpkを取り出す
    if bp_objects.filter(part=None, date=select_day):
        none_bp_object_pk = bp_objects.filter(part=None, date=select_day).order_by('-pk').first().pk
    else:
        none_bp_object_pk = 0
    # ルーチンオブジェクトがあればその最新のレコードのpkを取り出す
    if bp_objects.filter(week=wd):
        wd_bp_object_pk = bp_objects.filter(week=wd).order_by('-pk').first().pk
    else:
        wd_bp_object_pk = 0

    # ルーチンオブジェクトのほうが古ければwdを Noneにする
    if none_bp_object_pk > wd_bp_object_pk:
        wd = None

    wd_dt_bp_objects = create_wd_bp_objects(user, wd, select_day)

    # データの数をかぞえます。
    data_count = len(wd_dt_bp_objects)

    #  指定日の設定部位（wd_dt_bp_objects）のそれぞれに種目登録がされていれば judge_discipline はTrueになります。※なければFalse
    #  bp_objects_judge_discipline　のリストに [wd_dt_bp_object, judge_discipline]という形で格納した後にそれを
    #  bp_objects_judge_discipline_list に格納していきます。
    bp_objects_judge_discipline_list = []
    if None not in wd_dt_bp_objects:
        for wd_dt_bp_object in wd_dt_bp_objects:
            bp_objects_judge_discipline = []
            bp_objects_judge_discipline.append(wd_dt_bp_object)
            judge_discipline = wd_dt_bp_object.judge_discipline(date=select_day)
            bp_objects_judge_discipline.append(judge_discipline)
            bp_objects_judge_discipline_list.append(bp_objects_judge_discipline)

    if detail:
        return render(request, 'day_schedule_detail.html', {
            'select_day': select_day,
            'page_title': 'カレンダー',
            'breadcrumb_name': '部位詳細',
            'bp_objects_judge_discipline_list': bp_objects_judge_discipline_list
        })

    # POSTで送られてきた部位データをバリデーションしてDBに保存します。
    if request.method == 'POST':
        if data_count != 5:  # データ数が5以下の場合
            form = DayBodyPartForm(data=request.POST, bp_objects=wd_dt_bp_objects)
            if form.is_valid():
                schedule = form.save(commit=False)
                schedule.date = select_day
                schedule.user = user
                schedule.save()

                if not request.POST.get('continue'):  # 登録を続けて行う場合
                    return redirect('tr_calendar:month_with_schedule', year=year, month=month)
                else:
                    return redirect('tr_calendar:day_schedule_create', year=year, month=month, day=day)
        else:  # データ数が5個既にある場合
            error = '※これ以上の登録はできません'
            form = DayBodyPartForm(bp_objects=wd_dt_bp_objects)
    else:
        form = DayBodyPartForm(bp_objects=wd_dt_bp_objects)

    return render(request, 'day_schedule_create.html', {
        'select_day': select_day,
        'form': form,
        'wd_dt_bp_objects': wd_dt_bp_objects,
        'page_title': 'カレンダー',
        'breadcrumb_name': '部位作成',
        'error': error,
    })


@login_required
def day_schedule_update(request, pk):
    """  日付指定オブジェクトの変更を行います。

    これはpkから変更先のオブジェクトを取り出して、フォームデータをバリデーションします。
    そしてそれを更新するだけです。
    """
    bp_object = BodyPart.objects.get(pk=pk)
    year = int(bp_object.date.year)
    month = int(bp_object.date.month)
    select_day = bp_object.date
    wd = settings.WEEK[select_day.weekday()]

    wd_dt_bp_objects = create_wd_bp_objects(request.user, wd, select_day)

    if request.method == 'POST':
        form = DayBodyPartForm(request.POST, instance=bp_object, bp_objects=wd_dt_bp_objects)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.date = select_day
            schedule.save()
            return redirect('tr_calendar:month_with_schedule', year=year, month=month)
    else:  # getの場合
        form = DayBodyPartForm(instance=bp_object, bp_objects=wd_dt_bp_objects)

    return render(request, 'day_schedule_update.html', {
        'form': form,
        'select_day': select_day,
        'page_title': 'カレンダー',
        'breadcrumb_name': '部位変更',
    })


@login_required
def day_schedule_update2(request, pk,  year, month, day):
    """  ルーティンオブジェクトの変更を行います。

    この場合処理は少し複雑になります。

    ルーティンオブジェクトをそのまま更新してしまうと、同じ曜日の他の日も更新されることになってしまいます。
    また、日付指定オブジェクトとして更新するとルーティンオブジェクトではなくなるため、同じ曜日の他の日のオブジェクトがなくなってしまいます。
    そのため、更新ではなく新規で日付指定オブジェクトを作成します。
    指定日に変更部位オブジェクトの他にルーティンオブジェクトが存在する場合、
    そのオブジェクトも新規に日付指定オブジェクトとして同じ部位で作成します。

    """
    user = request.user
    date = datetime.date(year=year, month=month, day=day)
    upd_bp_object = BodyPart.objects.get(pk=pk)  # 変更するオブジェクトをとります。
    wd_bp_objects = BodyPart.objects.filter(week=upd_bp_object.week, user=user)  # upd_object と同じ曜日の他のオブジェクトをとります

    wd_dt_bp_objects = create_wd_bp_objects(user, upd_bp_object.week, date)

    if request.method == 'POST':

        # ルーティンオブジェクトを変更する場合、変更するオブジェクトを更新せずに新規で日付指定オブジェクトを作成します。
        form = DayBodyPartForm(request.POST, bp_objects=wd_dt_bp_objects)
        if form.is_valid():
            # upd_object と同じ曜日のオブジェクト(同じ曜日の設定部位)が他にない（upd_objectの1部位）のみの場合、
            # 部位が空白の日付指定オブジェクトをDBに作成します
            if wd_bp_objects.count() == 1:
                BodyPart.objects.create(date=date, user=user)
            for wd_bp_object in wd_bp_objects:
                # wd_bp_object が 変更するオブジェクトではない場合、新しく　wd_object　と同じ部位の日付指定オブジェクトを作ります。
                if wd_bp_object != upd_bp_object:
                    part = wd_bp_object.part
                    detail_part = wd_bp_object.detail_part
                    BodyPart.objects.create(part=part, detail_part=detail_part, date=date, user=user)
                    BodyPart.objects.create(date=date, user=user)
            # DBに保存します
            schedule = form.save(commit=False)
            schedule.date = date
            schedule.user = user
            schedule.save()
            return redirect('tr_calendar:month_with_schedule', year=year, month=month)
    else:  # getの場合
        form = DayBodyPartForm(instance=upd_bp_object, bp_objects=wd_dt_bp_objects)

    return render(request, 'day_schedule_update.html', {
        'form': form,
        'select_day': date,
        'page_title': 'カレンダー',
        'breadcrumb_name': '部位変更',
    })


@require_POST
def routine_day_delete(request, year=timezone.now().year, month=timezone.now().month, day=timezone.now().day):
    user = request.user
    date = datetime.date(year=year, month=month, day=day)
    wd = settings.WEEK[date.weekday()]

    # カレンダーから全て削除する場合
    if request.POST.get('delete_all'):
        del_objects = BodyPart.objects.filter(user=user)
        del_objects.delete()

    # day_schedule_create.html で日付指定オブジェクトを削除する場合
    if request.POST.getlist('delete_dt_obj'):
        del_pk_list = request.POST.getlist('delete_dt_obj')
        del_objects = BodyPart.objects.filter(pk__in=del_pk_list)

        # redirect時に　yearとmonthを返す必要があるのでここで取得します。
        del_object = del_objects[0]
        year = int(del_object.date.year)
        month = int(del_object.date.month)

        del_objects.delete()

    if request.POST.getlist('delete_wd_obj'):  # ルーチンオブジェクトを削除する場合
        del_pk_list = request.POST.getlist('delete_wd_obj')
        del_objects = BodyPart.objects.filter(pk__in=del_pk_list)
        wd_objects = BodyPart.objects.filter(week=wd, user=user)

        # 削除する曜日のルーティンオブジェクトにおいて、削除する部位以外の日付オブジェクトをDBに作成します。
        for wd_object in wd_objects:
            if wd_object not in del_objects:
                part = wd_object.part
                detail_part = wd_object.detail_part
                BodyPart.objects.create(part=part, detail_part=detail_part, date=date, user=user)
        # 部位が空の日付指定オブジェクトをDBに作成します。
        BodyPart.objects.create(date=date, user=user)

    return redirect('tr_calendar:month_with_schedule', year=year, month=month)


def create_wd_bp_objects(user, wd, date):
    """ テンプレートに表示する部位オブジェクトをリストに格納します。

    wd_bp_objects, dt_bp_objects　にオブジェクトがあればそれをwd_dt_bp_objectsに格納します。
    なければNoneを入れます。
    これはバリデーションの時に同じ部位がすでに登録してないかを判定するために使います。※formの引数に渡します"""

    dt_bp_objects = BodyPart.objects.filter(date=date, user=user).exclude(part=None)
    if wd == None:  #　曜日がNoneとなっている場合
        wd_bp_objects = None
    elif TermDecision.objects.filter(user=user).exists():  # ルーチン期間外の場合
        if not TermDecision.objects.get(user=user).judge_term_date(date=date):
            wd_bp_objects = None
        else:  # ルーチン期間内の場合
            wd_bp_objects = BodyPart.objects.filter(week=wd, user=user)
    else:
        wd_bp_objects = BodyPart.objects.filter(week=wd, user=user)

    wd_dt_bp_objects = []

    if wd_bp_objects:
        for wd_bp_object in wd_bp_objects:
            wd_dt_bp_objects.append(wd_bp_object)
    if dt_bp_objects:
        for dt_bp_object in dt_bp_objects:
            wd_dt_bp_objects.append(dt_bp_object)
    if not wd_bp_objects and not dt_bp_objects:
        wd_dt_bp_objects.append(None)

    return wd_dt_bp_objects
