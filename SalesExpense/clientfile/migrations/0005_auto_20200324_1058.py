# Generated by Django 3.0 on 2020-03-24 10:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientfile', '0004_auto_20200311_1427'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='historicalclient',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
