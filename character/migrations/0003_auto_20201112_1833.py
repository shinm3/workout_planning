# Generated by Django 3.0.7 on 2020-11-12 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0002_character_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='character',
            name='image',
        ),
        migrations.AddField(
            model_name='character',
            name='number',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
