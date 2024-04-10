# Generated by Django 4.2.8 on 2024-02-26 12:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mon_dem', '0004_remove_event_description_remove_event_end_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='calendar',
            name='company',
        ),
        migrations.AddField(
            model_name='movingcompany',
            name='calendar',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='mon_dem.calendar'),
        ),
    ]
