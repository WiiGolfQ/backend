# Generated by Django 5.0.1 on 2024-01-31 01:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wgl_api', '0002_alter_elo_mu_alter_elo_sigma'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='p1_mu_after',
            field=models.FloatField(blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='match',
            name='p2_mu_after',
            field=models.FloatField(blank=True, editable=False, null=True),
        ),
    ]
