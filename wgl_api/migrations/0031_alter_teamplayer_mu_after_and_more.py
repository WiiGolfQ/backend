# Generated by Django 5.0.1 on 2024-05-24 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wgl_api', '0030_alter_team_score_formatted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teamplayer',
            name='mu_after',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='teamplayer',
            name='score_formatted',
            field=models.CharField(editable=False, max_length=12, null=True),
        ),
    ]