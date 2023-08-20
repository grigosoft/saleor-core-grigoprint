# Generated by Django 3.2.20 on 2023-08-03 10:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accountExtra', '0011_auto_20230407_0928'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userextra',
            name='split_payment',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='userextra',
            name='tipo_utente',
            field=models.CharField(choices=[('A', 'Azienda'), ('P', 'Privato'), ('PA', 'Pubblica Amministrazione'), ('R', 'Agenzia Pubblicitaria')], default='A', max_length=9),
        ),
    ]
