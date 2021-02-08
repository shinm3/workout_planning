from django.conf import settings


class Provisional:
    def __init__(self, ex=None, create=None, update=None, delete=None, term=None):
        """ ルーティン設定において決定する前に仮としてセッションに値を保存するための処理になります。


        各変数のキーについて　

        ・左部分の文字部

        self.ex_form_data
            ex_form_data_　:　すでに設定済みのオブジェクトを抽出したものを表します。
        self.create_form_data
            create_form_data_ :　新規作成したデータを表します。
        self.update_form_data
            update_form_data_ :　変更したex_form_dataまたはupdate_form_dataのデータを表します。　
        self.delete_data
            delete_data :　削除するデータを表します。
            all_delete_data :　削除する全てのデータを表します。
        self.term_form_data
            term_form_data : ルーティンの開始日時～終了日時のデータを表します。

        ・右部分の数字(ex_form_data_、　create_form_data_、　update_form_data_　のみ)
        最初の一桁 : 0～6までの数字でweekが月曜日～日曜日を表します。
        それ以降の数字 : 左部分が　ex_form_data_　の場合はオブジェクトのidを表します。

        例：
    　　  ex_form_data_015　→　これはすでに設定済みでidが15、weekが'月曜日'のbody_partオブジェクトを抽出したもの
        """
        self.ex_form_data = ex or {}
        self.create_form_data = create or {}
        self.update_form_data = update or {}
        self.delete_data = delete or {}
        self.term_form_data = term or {}
        self.edited = False  # インスタンス化後に編集があったかのフラグ。セッションに保存するかどうかの判定に使う

    def as_json(self):
        ret = {}
        if self.ex_form_data:
            ret.update(self.ex_form_data)
        if self.create_form_data:
            ret.update(self.create_form_data)
        if self.update_form_data:
            ret.update(self.update_form_data)
        if self.delete_data:
            ret.update(self.delete_data)
        if self.term_form_data:
            ret.update(self.term_form_data)
        return ret

    @classmethod
    def from_json(cls, data):
        """セッションからルーティン設定値を取り出してクラス変数に格納したものをインスタンス化

        dataはセッション'provisional'の値が入ります。
        """
        ex_items = None or {}
        create_items = None or {}
        update_items = None or {}
        delete_items = None or {}
        term_items = None or {}

        for key, item in data.items():
            if 'ex' in key:
                ex_items[key] = item
            if 'create' in key:
                create_items[key] = item
            if 'update' in key:
                update_items[key] = item
            if 'delete' in key:
                delete_items[key] = item
            if 'term' in key:
                term_items[key] = item
        return cls(ex_items, create_items, update_items, delete_items, term_items)

    def add_form_data(self, form_data):
        """ 仮の部位情報、ルーティン期間を追加する

         例：
         ex_form_data_015: {'week': '月曜日',
         　'part': '大胸筋',
         　'detail_part': '上部',
         　'image2': ex_data.image.url,
         　'pid': 15}
         ※'pid'の値は　ex_form_dataとupdate_form_data（既に設定済みまたは変更データ）であればDBに登録されている部位オブジェクトのｉｄの値になります。
         ※create_form_data（新規作成データ）であればその曜日の何個目のデータ（実際には-1した値）かを表す値になります。　
         ※例　1個目ならpidの値は0
        """
        self.edited = True

        if 'ex' in list(form_data.keys())[0]:
            self.ex_form_data.update(form_data)
        if 'create' in list(form_data.keys())[0]:
            self.create_form_data.update(form_data)
        if 'update' in list(form_data.keys())[0]:
            self.update_form_data.update(form_data)
        if 'term' in list(form_data.keys())[0]:
            self.term_form_data.update(form_data)

    def judge_have_id_data(self, pk):
        """ 指定のID(pk)を持つデータがあるかどうかを判定

        指定のIDを持つデータとは元が既にＤＢに設定済みの　ex_form_data、　
        またはそれを変更した　update_form_data、　
        またはそれを削除した　delete_data　
        となります。

        これらが一つでもなければ　True　、　あればＦａｌｓｅ　を返します
        """

        judge_data = {}
        judge_data.update(self.ex_form_data)
        judge_data.update(self.update_form_data)
        judge_data.update(self.delete_data)
        for key in judge_data.keys():
            if str(pk) in key or 'all_delete_data' in key:
                return False
        return True

    def get_form_data_dict(self):
        """ 各データを辞書に格納して返します """
        form_data_dict = {}
        form_data_dict.update(self.ex_form_data)
        form_data_dict.update(self.create_form_data)
        form_data_dict.update(self.update_form_data)

        return form_data_dict

    def get_form_data(self, week):
        """ 指定の曜日の各データをリストに格納して返します """

        form_data_dict = self.get_form_data_dict()
        return [item for key, item in form_data_dict.items() if week in item['week']]

    def delete_form_data(self, pk='all'):
        """ データを削除します

        　すべて削除の場合：　

         変更前のデータ,既に設定済みのデータはＤＢに存在するため、決定後にＤＢから削除します。
         そのために　self.delete_data　に　全削除を表す　'all'　を一時保存します。
         self.ex_form_data, self.update_form_data, self.create_form_data　をすべて削除します。

         選択削除の場合：

         変更前のデータ,既に設定済みのデータはＤＢに存在するため、決定後にＤＢから削除します。
         そのために　self.delete_data　に　Id　を一時保存します。
         """
        self.edited = True

        if pk == 'all':
            if self.ex_form_data or self.update_form_data:
                self.delete_data['all_delete_data'] = pk
            self.ex_form_data.clear()
            self.update_form_data.clear()
            self.create_form_data.clear()
        else:
            delete_data = 'delete_data_' + str(pk)
            delete_ex_form_data = [k for k, v in self.ex_form_data.items() if v['pid'] == int(pk)]
            delete_update_form_data = [k for k, v in self.update_form_data.items() if v['pid'] == int(pk)]
            delete_create_form_data = [k for k, v in self.create_form_data.items() if v['pid'] == int(pk)]

            if delete_ex_form_data:
                data = self.ex_form_data.pop(delete_ex_form_data[0])
                self.delete_data[delete_data] = data['pid']
            elif delete_update_form_data:
                data = self.update_form_data.pop(delete_update_form_data[0])
                self.delete_data[delete_data] = data['pid']
            elif delete_create_form_data:
                del self.create_form_data[delete_create_form_data[0]]

    def arrange_form_data(self, form, pk, form_num=1):
        """ ヴァリデーションした form_data を 整えます　"""
        week = form.cleaned_data['week']
        part = form.cleaned_data['part']
        detail_part = form.cleaned_data['detail_part']
        if detail_part:
            file_name = settings.IMAGES[part + detail_part]
        else:
            file_name = settings.IMAGES[part]
        image = f"media/{file_name}.png"

        return {
            'week': week,
            'part': part,
            'detail_part': detail_part,
            'image': image,
            'pid': pk,
            'form_num': form_num,
        }

