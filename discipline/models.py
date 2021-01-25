from django.db import models
from routine.models import BodyPart


class Discipline(models.Model):
    discipline = models.CharField(max_length=30, null=True, blank=True)
    date = models.DateField('実行日', null=True, blank=True)
    weight_1 = models.FloatField(
        verbose_name='重量1',
        blank=True,
        null=True, )
    weight_2 = models.FloatField(
        verbose_name='重量2',
        blank=True,
        null=True, )
    weight_3 = models.FloatField(
        verbose_name='重量3',
        blank=True,
        null=True, )
    weight_4 = models.FloatField(
        verbose_name='重量4',
        blank=True,
        null=True, )
    weight_5 = models.FloatField(
        verbose_name='重量5',
        blank=True,
        null=True, )
    weight_6 = models.FloatField(
        verbose_name='重量6',
        blank=True,
        null=True, )
    weight_7 = models.FloatField(
        verbose_name='重量7',
        blank=True,
        null=True, )
    weight_8 = models.FloatField(
        verbose_name='重量8',
        blank=True,
        null=True, )
    weight_9 = models.FloatField(
        verbose_name='重量9',
        blank=True,
        null=True, )
    weight_10 = models.FloatField(
        verbose_name='重量10',
        blank=True,
        null=True, )
    times_1 = models.IntegerField(
        verbose_name='回数1',
        blank=True,
        null=True, )
    times_2 = models.IntegerField(
        verbose_name='回数2',
        blank=True,
        null=True, )
    times_3 = models.IntegerField(
        verbose_name='回数3',
        blank=True,
        null=True, )
    times_4 = models.IntegerField(
        verbose_name='回数4',
        blank=True,
        null=True, )
    times_5 = models.IntegerField(
        verbose_name='回数5',
        blank=True,
        null=True, )
    times_6 = models.IntegerField(
        verbose_name='回数6',
        blank=True,
        null=True, )
    times_7 = models.IntegerField(
        verbose_name='回数7',
        blank=True,
        null=True, )
    times_8 = models.IntegerField(
        verbose_name='回数8',
        blank=True,
        null=True, )
    times_9 = models.IntegerField(
        verbose_name='回数9',
        blank=True,
        null=True, )
    times_10 = models.IntegerField(
        verbose_name='回数10',
        blank=True,
        null=True, )
    body_part = models.ForeignKey(BodyPart, on_delete=models.CASCADE)
    remarks = models.TextField(
        verbose_name='備考',
        blank=True,
        null=True,
        max_length=1000,
    )

    def __str__(self):
        return self.discipline
