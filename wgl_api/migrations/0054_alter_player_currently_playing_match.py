# Generated by Django 5.0.1 on 2024-06-06 23:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wgl_api', '0053_player_currently_playing_match'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='currently_playing_match',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, to='wgl_api.match'),
        ),
    ]