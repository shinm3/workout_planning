from django.shortcuts import render, redirect
from .models import Character
from .forms import CharacterForm
# Create your views here.


def character_selection(request):
    """
    キャラクターを選択して決定します。

    GETで送られてきたら「CharacterForm」をコンテキストに入れてキャラクター選択
    のテンプレートを表示します。

    POSTで送られてきたらformの内容をバリデートして、これまで設定していたキャラクターオブジェクトが
    あればそれを削除して、新しいキャラクターオブジェクトを作成します。そして、ホームにリダイレクトします。
    """
    user = request.user
    if request.method == 'POST':
        form = CharacterForm(request.POST)
        if form.is_valid():
            # バリデーション成功後、削除するための現在設定中のキャラクターオブジェクトを取得
            del_objects = Character.objects.filter(user=user)
            if del_objects:
                # 現在設定中のキャラクターオブジェクトがあればそれを削除
                for del_object in del_objects:
                    del_object.delete()
            character = form.save(commit=False)
            character.user = user
            name = request.POST.get('name')
            character.name = name
            number = request.POST.get('character')  # キャラクターを表す番号
            character.number = number

            character.save()
            return redirect('home:home')
    else:
        # GETの場合
        form = CharacterForm()

    return render(request, 'character_selection.html', {
        'page_title': 'キャラクター選択',
        'form': form,
    })
