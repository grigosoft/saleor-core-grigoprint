# Generated by Django 3.2.16 on 2023-02-09 08:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accountExtra', '0005_auto_20230206_1142'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userextra',
            name='cell',
        ),
        migrations.RemoveField(
            model_name='userextra',
            name='tel',
        ),
        migrations.AddField(
            model_name='userextra',
            name='is_rappresentante',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='contatto',
            name='uso',
            field=models.CharField(choices=[('G', 'Generico'), ('F', 'Fatturazione'), ('N', 'Notifiche')], default='G', max_length=1),
        ),
    ]
