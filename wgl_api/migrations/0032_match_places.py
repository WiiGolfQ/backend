# Generated by Django 5.0.1 on 2024-05-24 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wgl_api', '0031_alter_teamplayer_mu_after_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='places',
            field=models.JSONField(blank=True, editable=False, null=True),
        ),
    ]