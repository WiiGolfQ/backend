# Generated by Django 5.0.1 on 2024-05-24 22:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wgl_api', '0036_team_place'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='team',
            name='place',
        ),
    ]