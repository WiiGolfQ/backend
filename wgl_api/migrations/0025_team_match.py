# Generated by Django 5.0.1 on 2024-05-23 22:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wgl_api', '0024_remove_team_player_ids'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='match',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='wgl_api.match'),
        ),
    ]
