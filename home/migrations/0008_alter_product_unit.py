# Generated by Django 3.2.8 on 2022-01-28 13:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0007_auto_20220128_1722'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='unit',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]