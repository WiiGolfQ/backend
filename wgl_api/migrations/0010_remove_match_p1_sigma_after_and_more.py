# Generated by Django 5.0.1 on 2024-02-06 05:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wgl_api', '0009_alter_match_result'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='match',
            name='p1_sigma_after',
        ),
        migrations.RemoveField(
            model_name='match',
            name='p2_sigma_after',
        ),
        migrations.RemoveField(
            model_name='score',
            name='video_url',
        ),
        migrations.AlterField(
            model_name='score',
            name='score',
            field=models.IntegerField(db_index=True),
        ),
    ]
