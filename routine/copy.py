from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import BodyPart, TermDecision
from .forms import BodyPartForm, TermDecisionForm


WEEK = ['月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日', '日曜日']

IMAGES = {
    "胸": "chest", "胸上部": "upperchest", "胸下部": "underchest", "胸中部": "middlechest", "腹": "abs",
    "背中": "back", "背中広背筋": "latissimusdorsi", "背中僧帽筋中部": "centraltrapezius", "肩": "shoulder",
    "肩前部": "frontshoulder", "肩側部": "sideshoulder", "肩後部": "rearshoulder", "肩僧帽筋上部": "trapezius",
    "腕": "arm", "腕二頭": "biceps", "腕三頭": "triceps", "腕前腕": "forearm", "脚": "leg", "脚四頭": "quads",
    "脚ハム": "hamstring", "脚臀部": "buttocks", "脚カーフ": "calf", "全身": "wholebody", "上半身": "upperbody",
}

FORM_TYPE = ['ex_form_data_', 'create_form_data_', 'update_form_data_']


@login_required
def term_decision(request):
    """ ルーティン期間を設定します """
    user = request.user
    term_object = TermDecision.objects.get(user__pk=user.pk)
    if request.method == 'POST':
        form = TermDecisionForm(request.POST)
        if form.is_valid():
            request.session['term_form_data'] = request.POST
            return redirect('routine:list')
    else:
        if 'term_form_data' in request.session.keys():
            form = TermDecisionForm(request.session.get('term_form_data'))
        else:
            form = TermDecisionForm(instance=term_object)
    return render(request, 'term_decision.html', {'form': form, 'page_title': 'ルーティン設定'})


@login_required
def week_list(request):
    """
    テンプレートでは各曜日ごとに設定した種目を表示させます。
    ここではまだ種目を決定してないので、セッションに入れてある「body_part」オブジェクトに即した辞書形式のもの
    を使用します。
    例：　ex_form_data_015: {'week': '月曜日',
         'part': '大胸筋',
         'detail_part': '上部',
         'image2': ex_data.image.url,
         'num2': 15}
         ※'num2'の値は　ex_form_data（既に設定済みのデータ）であればデータベースに登録済みのためｉｄの値になります。
         ※create_form_dataとupdate_form_data（新規作成と変更データ）であれば
         ※その曜日の何個目のデータ（実際には-1した値）かを表す値になります。　例　1個目ならnum2の値は0

    これを曜日ごとのリストに入れて、そのリストを　body_parts というリストに格納します。
    順番は　[月曜日のリスト, 火曜日のリスト, 水曜日のリスト,　.....日曜日のリスト]となります。

    すでに設定されている各曜日のbody_partオブジェクトと新規作成、変更したセッションデータで処理を分けます。

    セッションのキーについて　

    ・左部分の文字部
    term_form_data : ルーティンの開始日時～終了日時のッションデータを表します。
    ex_form_data_　:　すでに設定済みのオブジェクトをセッションデータ化したものを表します。
    create_form_data_ :　新規作成したセッションデータを表します。
    update_form_data_ :　変更したex_form_dataまたはupdate_form_dataのセッションデータを表します。　
    delete_data :　削除するセッションデータを表します。
    all_delete_data :　削除する全てのセッションデータを表します。

    ・右部分の数字(ex_form_data_、　create_form_data_、　update_form_data_　のみ)
    最初の一桁 : 0～6までの数字でweekが月曜日～日曜日を表します。
    それ以降の数字 : 左部分が　ex_form_data_　の場合はオブジェクトのidを表します。

    例：
    　　ex_form_data_015　→　これはすでに設定済みでidが15、weekが'月曜日'のbody_partオブジェクトをセッションデータに置き換えたもの

    max_countは最も多いセッションデータを持っている曜日のデータ数です。
    body_part_i_set では曜日ごとにｎ個目のセッションデータ（なければ空のリスト）が格納されているリストを　max_count　個格納します

    例：
      [[月１,火空, 水１, 木１, 金1, 土空, 日1][月2,火空, 水空, 木空, 金2, 土空, 日2]......]

    term_object　ではルーティン期間のオブジェクトまたは辞書データが格納されます
    """
    user = request.user

    body_parts = []  # 各曜日のsession_dataのリストが入ります。　例　[月曜日のリスト, 火曜日のリスト, 水曜日のリスト,　.....]

    # 例　[[月曜日の最初のセッションデータ, .... 日曜日の最初のセッションデータ],
    # [月曜日の二つ目のセッションデータ, .... 日曜日の二つ目のセッションデータ]......]
    body_part_i_set = []

    count_list = []  # 各曜日のsession_dataの個数が入ります。　例　[月曜日のデータ個数, 火曜日のデータ個数, 水曜日のデータ個数,　...]

    # 月~日の各曜日ごとにbody_partオブジェクトがあればその各フィールドの値を辞書に置き換えてセッションに渡して
    # それをsession_dataリストにまとめたものを「body_parts」リストに入れます。
    # 例　for文の一巡目：　i = 0 , day = '月曜日'
    for i, day in enumerate(WEEK):

        # 該当の曜日のセッションデータ（辞書形式）が入ります。
        # 例 月曜日の場合: [ex_form_data_015:{'week': '月曜日', 'part': '大胸筋', 'detail_part': '上部',
        # 'image2': ex_data.image.url, 'num2': 10}, ex_form_data_016:{'week': '月曜日', 'part': .......}]
        session_data = []

        # 該当する曜日のフィールドを持つすでに設定済みのbody_partオブジェクト（ルーティンオブジェクト）があれば取得する。
        ex_many_data = BodyPart.objects.filter(week=day, user=user)

        # ex_many_dataからルーティンオブジェクトを一つずつ取得
        for ex_data in ex_many_data:
            update_form_data = 'update_form_data_' + str(i) + str(ex_data.pk)  # 例  update_form_data_015
            ex_form_data = 'ex_form_data_' + str(i) + str(ex_data.pk)  # 例  ex_form_data_015
            delete_data = 'delete_data_' + str(ex_data.pk)  # 例  delete_data_15
            data_set = {ex_form_data, update_form_data, 'all_delete_data', delete_data, }

            # sessionのキーに集合にした「data_set」の各要素がなければ
            # sessionに変数「ex_form_data」をキーにして「ex_data」オブジェクトの値を入れます
            # ※week_listに最初にアクセスされた時の処理になります。
            if set(list(request.session.keys())).isdisjoint(data_set):
                image = ex_data.get_image_url()
                request.session[ex_form_data] = {
                    'week': ex_data.week,
                    'part': ex_data.part,
                    'detail_part': ex_data.detail_part,
                    'image': image,
                    'num2': ex_data.pk,
                    'form_num': 0,  # これはex_form_dataであることを示します。　※定数FORM_TYPEのインデックス番号0
                }
                request.provisional.add_form_data({ex_form_data: {
                    'week': ex_data.week,
                    'part': ex_data.part,
                    'detail_part': ex_data.detail_part,
                    'image': image,
                    'num2': ex_data.pk,
                    'form_num': 0,  # これはex_form_dataであることを示します。　※定数FORM_TYPEのインデックス番号0
                }})
                session_data.append(request.session[ex_form_data])  # session_dataのリストに追加

            # request.session[ex_form_data]はすでに作成済みであれば、そのままsession_dataのリストに追加
            # ※week_list.htmlにて決定ボタンを押す前に2回目以降アクセスされた場合の処理になります。
            elif ex_form_data in request.session:
                session_data.append(request.session[ex_form_data])

        # セッションからキーを一つずつ取り出します。
        for k in request.session.keys():
            # 取り出したキーに'delete_data'が含まれてなく、'create_form_data_該当の曜日番号'または
            # 'update_form_data_該当の曜日番号'が含まれていれば、その値をsession_dataのリストに追加
            # つまり、ここで新規作成された該当曜日のセッションデータか変更された該当曜日のセッションデータが
            # あればそれをsession_dataのリストに追加します。
            if 'delete_data' not in k:
                if 'create_form_data_' + str(i) in k or 'update_form_data_' + str(i) in k:
                    session_data.append(request.session[k])

        body_parts.append(session_data)  # 該当曜日のセッションデータが存在しない場合空のリストが追加される
        count_list.append(len(session_data))  # 該当曜日のセッションデータの個数をcount_listに追加

    body_parts_count = body_parts.count([])  # 各曜日の空のリストの個数
    max_count = max(count_list)  # 最もセッションデータが多い曜日の個数

    # 月曜日～日曜日の各曜日のセッションデータを一つずつ（なければ空を）　i_list　に追加
    # 日曜日まで追加した　i_list　を　body_part_i_set　に追加して、これをmax_count回繰り返します
    for i in range(max_count):
        i_list = []
        for body_part in body_parts:
            # 該当の曜日のセッションデータ数が現在の繰り返し数以上であれば繰り返し数と一致するセッションデータを追加します。
            if len(body_part) >= i + 1:
                i_list.append(body_part[i])
            else:
                i_list.append([])  # 現在の繰り返し数より少なければ空のリストを追加しましす。
        body_part_i_set.append(i_list)

    # テンプレートで表示するルーティンの期間をとります。
    # sessionに　'term_form_data'　があれば（term_decisionにて変更をしてれば）formからバリデーションしてterm_objectを取得します。
    # なければ設定済み、または初期設定のterm_objectを取得します。
    if 'term_form_data' in request.session.keys():
        form = TermDecisionForm(request.session['term_form_data'])
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            term_object = {
                'start_date': start_date,
                'end_date': end_date,
            }
        else:
            term_object = TermDecision.objects.get(user__pk=user.pk)
    else:
        term_object = TermDecision.objects.get(user__pk=user.pk)

    return render(request, 'week_list.html', {
        'body_parts': body_parts,
        'body_parts_count': body_parts_count,
        'body_part_i_set': body_part_i_set,
        'term_object': term_object,
        'page_title': 'ルーティン設定',
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
    num2　は指定した曜日のデータの何個目かを表す数値になります。　※-1した値になります。　2個目のデータなら値は1になります。

    """
    wd = WEEK[num]  # 曜日を取得
    error = None
    data_count = 0
    form_data = [None]
    num2 = 0  # 指定した曜日のデータの何個目かを表す数値になります。　※-1した値になります。　2個目のデータなら値は1になります。

    # sessionからキーを一つずつ取り出して、指定した曜日の「すでに設定済み」、「新規作成」、「更新」したデータ
    # であれば、　data_count に1をプラスする。　
    # そして、指定した曜日の「新規作成」したデータであれば、　num2 に1プラスする。
    # ※該当するデータが3つあればdata_count、num2は3になります。
    # ※該当するデータが何もない（その曜日の最初の一つを作成する場合）data_count、num2は0になります。
    for k in request.session.keys():
        if 'form_data' in k and 'term' not in k:
            if request.session[k]['week'] == wd:
                data_count += 1
                if None in form_data:
                    form_data.remove(None)
                form_data.append(request.session[k])

        if 'create_form_data_' + str(num) in k:
            num2 += 1

    # sessionに格納するときのキー値になります。（num番目の曜日のnum2個目の新規作成データという意味です）
    create_form_data = 'create_form_data_' + str(num) + str(num2)

    if request.method == 'POST':
        if data_count != 5:  # データ数が5以下の場合
            form = BodyPartForm(request.POST, bp_objects=form_data)
            if form.is_valid():
                # セッションに入力データを格納する。
                week = form.cleaned_data['week']
                part = form.cleaned_data['part']
                detail_part = form.cleaned_data['detail_part']
                if detail_part:
                    file_name = IMAGES[part+detail_part]
                else:
                    file_name = IMAGES[part]
                image = f"media/media/{file_name}.png"
                request.session[create_form_data] = {
                    'week': week,
                    'part': part,
                    'detail_part': detail_part,
                    'image': image,
                    'num2': num2,
                    'form_num': 1,  # これはcreate_form_dataであることを示します。　※定数FORM_TYPEのインデックス番号1
                }
                if request.POST.get('continue'):  # 登録を続けて行う場合
                    return redirect('routine:create', num=num)
                return redirect('routine:list')
        else:  # データ数が5個既にある場合
            error = '※これ以上の登録はできません'
            form = BodyPartForm(bp_objects=form_data)
    else:  # GETの場合
        form = BodyPartForm(bp_objects=form_data)

    # 指定した曜日のセッションデータの「部位」「詳細部位」「ｉｄ　or　データ番号」を辞書形式で取り出し、リストに格納する
    # これはテンプレートにて削除、変更を行うために取得
    bp_objects = []
    for k in request.session.keys():
        bp_object = {}
        if 'form' in k and 'term' not in k and request.session[k]['week'] == wd:
            bp_object['part'] = request.session[k]['part']
            bp_object['detail_part'] = request.session[k]['detail_part']
            bp_object['num2'] = request.session[k]['num2']
            bp_object['form_num'] = request.session[k]['form_num']
            bp_objects.append(bp_object)

    return render(request, 'routine_create.html', {
            'wd': wd,
            'form': form,
            'num': num,
            'num2': num2,
            'bp_objects': bp_objects,
            'page_title': 'ルーティン設定',
            'error': error,
    })


@login_required
def routine_update(request, num, num2, form_num):
    """ 指定された曜日の特定のトレーニング部位を変更。
    'ex_form_data_'つまり既に登録済みのデータを変更する場合、セッションから'ex_form_data_'
    を削除して'update_form_data_'として新しくセッションデータを作ります。
    'update_form_data_'つまり'ex_form_data_'を一回以上変更しているデータをさらに変更する場合
    'update_form_data_'のままセッションデータを更新します。
    'create_form_data_'は変更しても'create_form_data_'のままセッションデータを更新します。
    """
    wd = WEEK[num]
    form_data = FORM_TYPE[form_num] + str(num) + str(num2)  # 変更対象のセッションデータキー
    update_form_data = 'update_form_data_' + str(num) + str(num2)
    ex_form_data = 'ex_form_data_' + str(num) + str(num2)
    form_data2 = [None]

    for k in request.session.keys():
        if 'form_data' in k and 'term' not in k:
            if request.session[k]['week'] == wd:
                if None in form_data2:
                    form_data2.remove(None)
                form_data2.append(request.session[k])

    if request.method == 'POST':
        form = BodyPartForm(request.POST, bp_objects=form_data2)
        if form.is_valid():
            week = form.cleaned_data['week']
            part = form.cleaned_data['part']
            detail_part = form.cleaned_data['detail_part']
            if detail_part:
                file_name = IMAGES[part + detail_part]
            else:
                file_name = IMAGES[part]
            image = f"media/media/{file_name}.png"

            # 既に登録済みのデータを変更する場合、セッションから'ex_form_data_'を削除して
            # 'update_form_data_'として新しくセッションデータを作ります。
            if ex_form_data == form_data:
                del request.session[ex_form_data]
                form_data = update_form_data
                form_num = 2

            # セッションに入力データを格納する。
            request.session[form_data] = {
                'week': week,
                'part': part,
                'detail_part': detail_part,
                'image': image,
                'num2': num2,
                'form_num': form_num,
            }
            return redirect('routine:list')
    else:
        form = BodyPartForm(initial=request.session[form_data], bp_objects=form_data2)

    return render(request, 'routine_update.html', {
        'wd': wd,
        'form': form,
        'page_title': 'ルーティン設定',
    })


@require_POST
def routine_delete(request, num=15):
    """ 指定された曜日のチェックされた特定のトレーニング部位を削除。
        またはすべてのトレーニング部位を削除

    """
    if request.POST.get('delete_all'):  # すべて削除する場合
        for k in list(request.session.keys()):
            # 変更前のデータ,既に設定済みのデータはＤＢに存在するため、決定後にＤＢから削除します。
            # そのため一旦'all_delete_data'としてセッションに保存します
            if 'update_form_data' in k or 'ex_form_data' in k:
                request.session['all_delete_data'] = 'all_data'
            if 'form_data' in k and 'term' not in k:
                del request.session[k]  # セッションデータを削除します。
    else:  # 選択削除の場合
        # del_numsはデータの特定番号　（update_form_data　、　ex_form_data　の場合は削除するid）の値が入っているリスト
        del_nums = request.POST.getlist('delete')
        form_nums = request.POST.getlist('form_num')
        for num2, form_num in zip(del_nums, form_nums):
            form_data = FORM_TYPE[int(form_num)] + str(num) + str(num2)  # 削除対象のセッションデータキー
            delete_data = 'delete_data_' + str(num2)
            update_form_data = 'update_form_data_' + str(num) + str(num2)
            ex_form_data = 'ex_form_data_' + str(num) + str(num2)

            # 変更前のデータ,既に設定済みのデータはＤＢに存在するため、決定後にＤＢから削除します。そのため一旦セッションにidを保存します。
            if update_form_data == form_data or ex_form_data == form_data:
                request.session[delete_data] = num2
            del request.session[form_data]  # セッションから削除

    return redirect('routine:list')


@require_POST
def routine_decision(request):
    """トレーニングルーティン決定後の処理になります。

    削除をした場合、DBにデータがあればそれを削除します。
    新規で作成したセッションデータがある場合（新規作成セッションデータを更新したデータも含まれます）、それをDBに保存します。
    変更したセッションデータがある場合、それをDBに更新します。
    ルーティン期間を設定（変更）した場合、それをDBに更新します。

    セッションデータを取り出すときは空にしたいのでpopメソッドを使います。
    """
    user = request.user
    term_date = TermDecision.objects.get(user__pk=user.pk)
    session_create_form_data = None
    form_week = []

    for k in list(request.session.keys()):
        # セッションに'all_delete_data'がある場合はそのユーザーのDBに保存されているBodyPartデータを全て削除します。
        if 'all_delete_data' in k:
            del request.session[k]
            del_objects = BodyPart.objects.filter(week__contains='曜日', user=user)
            del_objects.delete()

        # セッションに'delete_data'がある場合はそのユーザーのDBに保存されている指定のｉｄのBodyPartデータを削除します。
        elif 'delete_data' in k:
            del_pk = request.session.pop(k, None)
            if BodyPart.objects.filter(pk=del_pk):
                del_object = BodyPart.objects.get(pk=del_pk)
                del_object.delete()

        # セッションに'create_form_data'がある場合はBodyPartFormでバリデーションしてＤＢに保存します。
        elif 'create_form_data' in k:
            session_create_form_data = request.session.pop(k, None)
            form = BodyPartForm(session_create_form_data, bp_objects=[None])
            if form.is_valid():
                body_part = form.save(commit=False)
                body_part.user = user
                body_part.save()
                form_week.append(body_part.week)

        # セッションに'update_form_data'がある場合はBodyPartFormでバリデーションしてＤＢを更新します。
        elif 'update_form_data' in k:
            session_update_form_data = request.session.pop(k, None)
            pk = session_update_form_data['num2']
            bp_object = BodyPart.objects.get(pk=pk, user=user)
            form = BodyPartForm(session_update_form_data, instance=bp_object, bp_objects=[None])
            if form.is_valid():
                body_part = form.save(commit=False)
                form.save()
                form_week.append(body_part.week)

        elif 'ex_form_data' in k:
            session_ex_form_data = request.session.pop(k, None)
            pk = session_ex_form_data['num2']
            body_part = BodyPart.objects.get(pk=pk, user=user)
            form_week.append(body_part.week)

        # セッションに'term_form_data'がある場合はTermDecisionFormでバリデーションしてＤＢを更新します。
        elif 'term_form_data' in k:
            session_term_form_data = request.session.pop(k, None)
            form = TermDecisionForm(session_term_form_data, instance=term_date)
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
            week = WEEK[dt_bp_object.date.weekday()]
            if judge_term_date and week in form_week:
                # ルーティンで上書きする場合
                if request.POST.get('overwrite'):
                    dt_bp_object.delete()
                    none_bp_objects.delete()
                # session_create_form_data があれば（ルーチンオブジェクトを新規作成してれば）
                elif session_create_form_data and not none_bp_objects:
                    BodyPart.objects.create(date=dt_bp_object.date, user=user)

    return redirect('home:home')

