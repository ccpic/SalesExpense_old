# Generated by Django 3.0 on 2020-03-24 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientfile', '0006_auto_20200324_1115'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='pub_date',
            field=models.DateTimeField(auto_now=True, verbose_name='上传日期'),
        ),
        migrations.DeleteModel(
            name='HistoricalClient',
        ),
    ]