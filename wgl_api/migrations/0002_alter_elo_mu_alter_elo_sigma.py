# Generated by Django 5.0.1 on 2024-01-31 00:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wgl_api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='elo',
            name='mu',
            field=models.FloatField(default=1500),
        ),
        migrations.AlterField(
            model_name='elo',
            name='sigma',
            field=models.FloatField(default=500.0),
        ),
    ]
