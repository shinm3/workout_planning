from django.db import models
from django.conf import settings

PARTS = (
    ('胸', '胸'), ('背中', '背中'), ('肩', '肩'),
    ('腕', '腕'), ('脚', '脚'), ('腹', '腹'),
    ('全身', '全身'), ('上半身', '上半身')
)

IMAGES = settings.IMAGES


def check_part(value):
    return value


class TermDecision(models.Model):
    start_date = models.DateField('開始時期', null=True, blank=True)
    end_date = models.DateField('終了時期', null=True, blank=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def judge_term_date(self, date):
        """ dateの日付の指定部位（self.part）に種目が設定されているかを判定します。 """
        if self.start_date <= date <= self.end_date:
            return True
        return False


class BodyPart(models.Model):
    week = models.CharField(max_length=50, null=True, blank=True)
    date = models.DateField('日付', null=True, blank=True)
    part = models.CharField(
        verbose_name='部位',
        max_length=50,
        choices=PARTS,
        null=True,
        blank=True,
    )
    detail_part = models.CharField(
        verbose_name='部位詳細',
        max_length=50,
        null=True,
        blank=True,
    )
    # カレンダーからルーティンで設定された値が個別に削除された際に
    # 作られるオブジェクトの何個目かを表すフィールド
    routine_delete_count = models.IntegerField(
        verbose_name='個別削除数',
        blank=True,
        null=True,
        default=0,)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        if self.part:
            return self.part
        else:
            return 'None'

    def get_image_url(self):
        """ 画像ファイルのｕｒｌを作成して取得します。 """
        part = self.part
        detail_part = self.detail_part
        if detail_part:
            file_name = IMAGES[part + detail_part]
        else:
            file_name = IMAGES[part]
        image = f"media/{file_name}.png"
        return image

    def judge_discipline(self, date):
        """ dateの日付の指定部位（self.part）に種目が設定されているかを判定します。 """
        discipline_set = self.discipline_set.filter(date=date)
        if discipline_set:
            return True
        return False

    def page_title(self):
        """ discipline関連のｈｔｍｌにて表示するページタイトルを作成します。 """
        if self.detail_part:
            return self.part + ' : ' + self.detail_part
        return self.part



