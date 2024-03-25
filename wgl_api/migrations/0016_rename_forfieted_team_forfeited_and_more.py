# Generated by Django 5.0.1 on 2024-03-25 23:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wgl_api', '0015_teamplayer_team_alter_team_players'),
    ]

    operations = [
        migrations.RenameField(
            model_name='team',
            old_name='forfieted',
            new_name='forfeited',
        ),
        migrations.AlterField(
            model_name='teamplayer',
            name='mu_before',
            field=models.FloatField(default=1),
        ),
        migrations.AlterField(
            model_name='teamplayer',
            name='sigma_before',
            field=models.FloatField(default=1),
        ),
    ]