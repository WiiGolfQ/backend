# Generated by Django 5.0.1 on 2024-06-06 23:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wgl_api', '0054_alter_player_currently_playing_match'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='player',
            name='currently_playing_match',
        ),
    ]
