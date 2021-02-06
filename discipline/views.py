from django.shortcuts import render, redirect, get_object_or_404
from routine.models import BodyPart
from .models import Discipline
from .forms import DisciplineForm
from django.views.decorators.http import require_POST

import datetime


def discipline_create(request, pk, year, month, day, new):
    """ 新規に指定部位の種目を作成します。 """

    date = datetime.date(year=year, month=month, day=day)
    body_part = get_object_or_404(BodyPart, pk=pk)  # 指定した部位のオブジェクト取得
    discipline_set = body_part.discipline_set.filter(date=date)  # 指定した日付に設定してあるオブジェクトのセット取得
    # ページタイトルの作成
    page_title = body_part.page_title()

    if request.method == 'POST':
        form = DisciplineForm(request.POST)
        if form.is_valid():
            discipline = form.save(commit=False)
            discipline.date = date
            discipline.body_part = body_part
            discipline.save()
            if not request.POST.get('continue'):  # 続けて種目登録する場合の処理
                return redirect('discipline:day_schedule_discipline',
                                pk=pk, year=year, month=month, day=day)
            else:
                return redirect('discipline:discipline_create', pk=pk, year=year, month=month, day=day, new=new)
    else:
        form = DisciplineForm()

    return render(request, 'discipline_create.html', {
        'form': form,
        'date': date,
        'discipline_set': discipline_set,
        'pk': pk,
        'year': year,
        'month': month,
        'day': day,
        'new': new,
        'page_title': page_title,
        'breadcrumb_name': '種目作成',
    })


def day_schedule_discipline(request, pk, year, month, day):
    """ 指定部位の種目一覧を表示させます。 """

    date = datetime.date(year=year, month=month, day=day)
    body_part = get_object_or_404(BodyPart, pk=pk)  # 指定した部位のオブジェクト取得
    discipline_set = body_part.discipline_set.filter(date=date)  # 指定した日付に設定してあるオブジェクトのセット取得

    # ページタイトルの作成
    page_title = body_part.page_title()

    return render(request, 'day_schedule_discipline.html', {
        'body_part': body_part,
        'discipline_set': discipline_set,
        'date': date,
        'pk': pk,
        'year': year,
        'month': month,
        'day': day,
        'page_title': page_title,
        'breadcrumb_name': '種目一覧',
    })


def discipline_update(request, pk, year, month, day):
    """ 指定部位の種目を更新します。 """

    new = 0  # すでに指定部位の種目が一つでも設定されてあれば０、されてなければ1となります。更新なので既に設定されてるため0になります
    date = datetime.date(year=year, month=month, day=day)
    discipline = get_object_or_404(Discipline, pk=pk)
    body_part_pk = discipline.body_part.pk
    body_part = discipline.body_part

    # ページタイトルの作成
    page_title = body_part.page_title()

    if request.method == 'POST':
        form = DisciplineForm(request.POST, instance=discipline)
        if form.is_valid():
            form.save()
            return redirect('discipline:discipline_create', pk=body_part_pk, year=year, month=month, day=day, new=new)
    else:
        form = DisciplineForm(instance=discipline)

    return render(request, 'discipline_update.html', {
        'date': date,
        'form': form,
        'pk': body_part_pk,
        'year': year,
        'month': month,
        'day': day,
        'new': new,
        'page_title': page_title,
        'breadcrumb_name': '種目変更',
    })


@require_POST
def discipline_delete(request, year, month, day):
    """ 指定部位の種目を削除します。 """
    del_pk_list = request.POST.getlist('delete')  # 削除する種目のpkリスト
    # 削除する前に種目設定してある先の部位のpkを取得
    del_pk = del_pk_list[0]
    discipline = get_object_or_404(Discipline, pk=del_pk)
    body_part_pk = discipline.body_part.pk
    # 選んだ種目を削除
    del_objects = Discipline.objects.filter(pk__in=del_pk_list)
    del_objects.delete()

    new = 1  # 全て削除されれば設定されている種目がなくなるので１になります。

    # 削除後、削除されていない種目のオブジェクトを取得
    date = datetime.date(year=year, month=month, day=day)
    body_part = get_object_or_404(BodyPart, pk=body_part_pk)
    discipline_set = body_part.discipline_set.filter(date=date)
    if discipline_set:  # 削除されていない種目があれば既に設定されている種目があるので「new」を０にします
        new = 0

    return redirect('discipline:discipline_create', pk=body_part_pk, year=year, month=month, day=day, new=new)
