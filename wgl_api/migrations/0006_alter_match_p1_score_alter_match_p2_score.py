# Generated by Django 5.0.1 on 2024-01-31 01:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wgl_api', '0005_alter_match_p2_sigma_after'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='p1_score',
            field=models.CharField(editable=False, max_length=12, null=True),
        ),
        migrations.AlterField(
            model_name='match',
            name='p2_score',
            field=models.CharField(editable=False, max_length=12, null=True),
        ),
    ]