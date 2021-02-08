from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import BodyPart, TermDecision
from .forms import BodyPartForm, TermDecisionForm

FORM_TYPE = ['ex_form_data_', 'create_form_data_', 'update_form_data_']


@login_required
def term_decision(request):
    """ ルーティン期間を設定します """
    user = request.user
    term_object = TermDecision.objects.get(user__pk=user.pk)
    if request.method == 'POST':
        form = TermDecisionForm(request.POST)
        if form.is_valid():
            # request.provisionalにルーティン期間を仮保存
            request.provisional.add_form_data({'term_form_data': request.POST})
            return redirect('routine:list')
    else:
        if request.provisional.term_form_data:
            form = TermDecisionForm(request.provisional.term_form_data['term_form_data'])
        else:
            form = TermDecisionForm(instance=term_object)
    return render(request, 'term_decision.html', {'form': form,
                                                  'page_title': 'ルーティン設定',
                                                  'breadcrumb_name': '期間設定',
                                                  })


@login_required
def week_list(request):
    """テンプレートでは各曜日ごとに仮設定した種目を表示させます。

    provisionalに格納されている各データを取得、表示します。
    曜日ごとに各データを取得して、body_parts というリストに格納します。
    順番は　[月曜日のリスト, 火曜日のリスト, 水曜日のリスト,　.....日曜日のリスト]となります。

    すでに設定されている各曜日のbody_partオブジェクトと新規作成、変更したデータで処理を分けます。

    max_countは最も多いデータを持っている曜日のデータ数です。
    body_part_i_set では曜日ごとにｎ個目のセッションデータ（なければ空のリスト）が格納されているリストを　max_count　個格納します

    例：
      [[月１,火空, 水１, 木１, 金1, 土空, 日1][月2,火空, 水空, 木空, 金2, 土空, 日2]......]

    term_object　ではルーティン期間のオブジェクトまたは辞書データが格納されます
    """
    user = request.user

    body_parts = []  # 各曜日のデータのリストが入ります。　例　[月曜日のリスト, 火曜日のリスト, 水曜日のリスト,　.....]
    body_part_i_set = []
    count_list = []  # 各曜日のの個数が入ります。　例　[月曜日のデータ個数, 火曜日のデータ個数, 水曜日のデータ個数,　...]

    # 月~日の各曜日ごとに既に設定済みbody_partオブジェクトがあればその各フィールドの値を辞書に置き換えてprovisionalに格納します。
    # それをデータのリストにまとめたものを「body_parts」リストに入れます。
    # 例　for文の一巡目：　i = 0 , day = '月曜日'

    for i, wd in enumerate(settings.WEEK):

        # 該当する曜日のフィールドを持つすでに設定済みのbody_partオブジェクト（ルーティンオブジェクト）があれば取得する。
        ex_many_data = BodyPart.objects.filter(week=wd, user=user)

        # ex_many_dataからルーティンオブジェクトを一つずつ取得
        for ex_data in ex_many_data:
            ex_form_data = 'ex_form_data_' + str(i) + str(ex_data.pk)  # 例  ex_form_data_015
            # ex_data.pkを持つデータがなければprovisionalにex_form_dataを追加します。
            if request.provisional.judge_have_id_data(ex_data.pk):
                image = ex_data.get_image_url()
                # request.provisionalに設定済みのルーティンを仮保存
                request.provisional.add_form_data({ex_form_data: {
                    'week': ex_data.week,
                    'part': ex_data.part,
                    'detail_part': ex_data.detail_part,
                    'image': image,
                    'pid': ex_data.pk,
                    'form_num': 0,  # これはex_form_dataであることを示します。　※定数FORM_TYPEのインデックス番号0
                }})

        # 該当の曜日のデータ（辞書形式）が入ります。
        # 例 月曜日の場合: [ex_form_data_015:{'week': '月曜日', 'part': '大胸筋', 'detail_part': '上部',
        # 'image2': ex_data.image.url, 'pid': 10}, ex_form_data_016:{'week': '月曜日', 'part': .......}]
        form_data = request.provisional.get_form_data(wd)
        body_parts.append(form_data)  # 該当曜日のデータが存在しない場合は空のリストが追加されます
        count_list.append(len(form_data))  # 該当曜日のデータの個数をcount_listに追加

    body_parts_count = body_parts.count([])  # 各曜日の空のリストの個数
    max_count = max(count_list)  # 最もデータが多い曜日の個数
    # 月曜日～日曜日の各曜日のデータを一つずつ（なければ空を）　i_list　に追加
    # 日曜日まで追加した　i_list　を　body_part_i_set　に追加して、これをmax_count回繰り返します
    for i in range(max_count):
        i_list = []
        for body_part in body_parts:
            # 該当の曜日のデータ数が現在の繰り返し数以上であれば繰り返し数と一致するデータを追加します。
            if len(body_part) >= i + 1:
                i_list.append(body_part[i])
            else:
                i_list.append([])  # 現在の繰り返し数より少なければ空のリストを追加しましす。
        body_part_i_set.append(i_list)
    # テンプレートで表示するルーティンの期間をとります。
    # sessionに　'term_form_data'　があれば（term_decisionにて変更をしてれば）formからバリデーションしてterm_objectを取得します。
    # なければ設定済み、または初期設定のterm_objectを取得します。
    if request.provisional.term_form_data:
        form = TermDecisionForm(request.provisional.term_form_data['term_form_data'])
        if form.is_valid():
            term_object = {
                'start_date': form.cleaned_data['start_date'],
                'end_date': form.cleaned_data['end_date'],
            }
        else:
            term_object = TermDecision.objects.get(user__pk=user.pk)
    else:
        term_object = TermDecision.objects.get(user__pk=user.pk)

    return render(request, 'week_list.html', {
        'body_parts_count': body_parts_count,
        'body_part_i_set': body_part_i_set,
        'term_object': term_object,
        'page_title': 'ルーティン設定',
        'breadcrumb_root': True,
        'breadcrumb_name': 'list',
    })


@login_required
def routine_create(request, num):
    """ 指定された曜日のトレーニング部位を設定。（5部位まで設定可能）
    6部位目を設定しようとするとエラー表示される
    この時点では設定をするだけでDBに登録するのは決定ボタンが押されてからになります。

    部位の削除、変更（変更画面へのリンク）を行うために最後に指定された曜日のデータ（部位）を
    全て取得します。

    num　は曜日番号になります。　※　月：0, 火：1, 水：2, 木：3, 金：4, 土：5, 日：6
    data_count は指定した曜日の設定されたデータ（部位）数になります
    pid　は指定した曜日のデータの何個目かを表す数値になります。　※-1した値になります。　2個目のデータなら値は1になります。

    """
    wd = settings.WEEK[num]  # 曜日を取得
    error = None
    form_data = request.provisional.get_form_data(wd)
    # 指定した曜日のデータの何個目かを表す数値になります。　※-1した値になります。　2個目のデータなら値は1になります。
    pid = len(request.provisional.create_form_data)
    data_count = len(form_data)
    # provisionalに格納するときのキー値になります。（num番目の曜日のpid個目の新規作成データという意味です）
    create_form_data = 'create_form_data_' + str(num) + str(pid)

    if request.method == 'POST':
        if data_count != 5:  # データ数が5以下の場合
            form = BodyPartForm(request.POST, bp_objects=form_data)
            if form.is_valid():
                # 画像のパスなどを整えたうえでセッションprovisionalに入力データを格納する。
                arrange_form_data = request.provisional.arrange_form_data(form, pid)
                request.provisional.add_form_data({create_form_data: arrange_form_data})
                if request.POST.get('continue'):  # 登録を続けて行う場合
                    return redirect('routine:create', num=num)
                return redirect('routine:list')
        else:  # データ数が5個既にある場合
            error = '※これ以上の登録はできません'
            form = BodyPartForm(bp_objects=form_data)
    else:  # GETの場合
        form = BodyPartForm(bp_objects=form_data)

    return render(request, 'routine_create.html', {
            'wd': wd,
            'form': form,
            'num': num,
            'pid': pid,
            'bp_objects': form_data,
            'page_title': 'ルーティン設定',
            'breadcrumb_name': '部位作成',
            'error': error,
    })


@login_required
def routine_update(request, num, pid, form_num):
    """ 指定された曜日の特定のトレーニング部位を変更。
    'ex_form_data_'つまり既に登録済みのデータを変更する場合、セッションから'ex_form_data_'
    を削除して'update_form_data_'として新しくセッションデータを作ります。
    'update_form_data_'つまり'ex_form_data_'を一回以上変更しているデータをさらに変更する場合
    'update_form_data_'のままセッションデータを更新します。
    'create_form_data_'は変更しても'create_form_data_'のままセッションデータを更新します。
    """
    wd = settings.WEEK[num]
    form_data = FORM_TYPE[form_num] + str(num) + str(pid)  # 変更対象のセッションデータキー
    update_form_data = 'update_form_data_' + str(num) + str(pid)
    ex_form_data = 'ex_form_data_' + str(num) + str(pid)
    form_data2 = request.provisional.get_form_data(wd)

    if request.method == 'POST':
        form = BodyPartForm(request.POST, bp_objects=form_data2)
        if form.is_valid():
            # 既に登録済みのデータを変更する場合、セッションから'ex_form_data_'を削除して
            # 'update_form_data_'として新しくセッションデータを作ります。
            if ex_form_data == form_data:
                del request.provisional.ex_form_data[ex_form_data]
                form_data = update_form_data
                form_num = 2
            # 画像のパスなどを整えたうえでセッションprovisionalに変更データを格納する。
            arrange_form_data = request.provisional.arrange_form_data(form, pid, form_num)
            request.provisional.add_form_data({form_data: arrange_form_data})

            return redirect('routine:list')
    else:
        form = BodyPartForm(initial=request.provisional.get_form_data_dict()[form_data], bp_objects=form_data2)

    return render(request, 'routine_update.html', {
        'wd': wd,
        'form': form,
        'page_title': 'ルーティン設定',
        'breadcrumb_name': '部位変更',
    })


@require_POST
def routine_delete(request, num=15):
    """ 指定された曜日のチェックされた特定のトレーニング部位を削除。またはすべてのトレーニング部位を削除 """

    if request.POST.get('delete_all'):  # すべて削除する場合
        request.provisional.delete_form_data()
    else:  # 選択削除の場合
        # del_numsはデータの特定番号　（update_form_data　、　ex_form_data　の場合は削除するid）の値が入っているリスト
        del_nums = request.POST.getlist('delete')
        for pid in del_nums:
            request.provisional.delete_form_data(pid)

    return redirect('routine:list')


@require_POST
def routine_decision(request):
    """トレーニングルーティン決定後の処理になります。

    削除をした場合、DBにデータがあればそれを削除します。
    新規で作成したセッション（provisional）データがある場合（新規作成セッションデータを更新したデータも含まれます）、それをDBに保存します。
    変更したセッションデータがある場合、それをDBに更新します。
    ルーティン期間を設定（変更）した場合、それをDBに更新します。

    セッションデータを取り出すときは空にしたいのでpopメソッドを使います。
    """
    user = request.user
    term_date = TermDecision.objects.get(user__pk=user.pk)
    form_week = []

    if request.provisional.delete_data:  # 削除データがある場合
        if 'all_delete_data' in request.provisional.delete_data.keys():  # 全て削除する場合
            BodyPart.objects.filter(week__contains='曜日', user=user).delete()
        else:  # 選択削除の場合
            for v in request.provisional.delete_data.values():
                BodyPart.objects.get(pk=v).delete()
    if request.provisional.create_form_data:  # 新規作成データがある場合、バリデーションしてＤＢに保存します。
        for create_form_data in request.provisional.create_form_data.values():
            form = BodyPartForm(create_form_data)
            if form.is_valid():
                body_part = form.save(commit=False)
                body_part.user = user
                body_part.save()
                form_week.append(body_part.week)
    if request.provisional.update_form_data:  # 変更データがある場合、バリデーションしてＤＢを更新します。
        for update_form_data in request.provisional.update_form_data.values():
            bp_object = BodyPart.objects.get(pk=update_form_data['pid'], user=user)
            form = BodyPartForm(update_form_data, instance=bp_object)
            if form.is_valid():
                body_part = form.save(commit=False)
                form.save()
                form_week.append(body_part.week)
    if request.provisional.ex_form_data:  # 既に設定済みのデータがある場合
        for ex_form_data in request.provisional.ex_form_data.values():
            body_part = BodyPart.objects.get(pk=ex_form_data['pid'], user=user)
            form_week.append(body_part.week)
    if request.provisional.term_form_data:  # ルーティン期間データがある場合、バリデーションしてＤＢを更新します。
        form = TermDecisionForm(request.provisional.term_form_data['term_form_data'], instance=term_date)
        if form.is_valid():
            term = form.save(commit=False)
            term.user = request.user
            term.save()

    # partがNoneでない日付指定クエリセットの中で、
    # ルーティン期間でかつ、作成したオブジェクトと同じ曜日となる日付指定オブジェクトでかつ、
    # その日付にpartがNoneの日付指定オブジェクトがなければ、部位が空の日付指定オブジェクトをDBに作成します。
    dt_bp_objects = BodyPart.objects.filter(date__isnull=False, user=user).exclude(part=None)
    if dt_bp_objects:
        for dt_bp_object in dt_bp_objects:
            none_bp_objects = BodyPart.objects.filter(part=None, date=dt_bp_object.date, user=user)
            judge_term_date = term_date.judge_term_date(date=dt_bp_object.date)
            week = settings.WEEK[dt_bp_object.date.weekday()]
            if judge_term_date and week in form_week:
                # ルーティンで上書きする場合
                if request.POST.get('overwrite'):
                    dt_bp_object.delete()
                    none_bp_objects.delete()
                # session_create_form_data があれば（ルーチンオブジェクトを新規作成してれば）
                elif request.provisional.create_form_data and not none_bp_objects:
                    BodyPart.objects.create(date=dt_bp_object.date, user=user)

    if 'provisional' in request.session.keys():  # 最後にセッションから'provisional'を削除
        del request.session['provisional']

    return redirect('home:home')

