# Generated by Django 4.2.8 on 2024-02-29 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mon_dem', '0006_alter_event_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dispo',
            name='description',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
