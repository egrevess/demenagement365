# Generated by Django 4.2.8 on 2024-02-29 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mon_dem', '0005_remove_calendar_company_movingcompany_calendar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='title',
            field=models.CharField(max_length=30),
        ),
    ]