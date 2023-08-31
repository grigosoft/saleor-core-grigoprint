# Generated by Django 3.2.16 on 2023-04-25 19:19

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prodottoPersonalizzato', '0002_auto_20230424_1001'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dato',
            name='nome',
            field=models.CharField(max_length=256, unique=True),
        ),
        migrations.AlterField(
            model_name='macro',
            name='nome',
            field=models.CharField(max_length=256, unique=True),
        ),
        migrations.AlterField(
            model_name='particolare',
            name='descrizione',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='particolare',
            name='nome',
            field=models.CharField(max_length=256, unique=True),
        ),
        migrations.AlterField(
            model_name='tessuto',
            name='nome',
            field=models.CharField(max_length=256, unique=True),
        ),
        migrations.AlterField(
            model_name='tessutostampato',
            name='note',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='tessutostampato',
            name='velocita_calandra',
            field=models.DecimalField(blank=True, decimal_places=2, default=Decimal('0.0'), max_digits=5, null=True),
        ),
        migrations.AlterField(
            model_name='tessutostampato',
            name='velocita_stampa',
            field=models.DecimalField(blank=True, decimal_places=1, default=Decimal('0.0'), max_digits=5, null=True),
        ),
        migrations.AlterField(
            model_name='tipostampa',
            name='nome',
            field=models.CharField(max_length=256, unique=True),
        ),
    ]