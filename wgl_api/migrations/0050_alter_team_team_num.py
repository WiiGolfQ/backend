# Generated by Django 5.0.1 on 2024-05-30 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wgl_api', '0049_team_game_teamplayer_game'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='team_num',
            field=models.CharField(default='?', max_length=1),
        ),
    ]
