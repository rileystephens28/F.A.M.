# Generated by Django 2.0.4 on 2018-11-28 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('currencies', '0002_currencypair_symbol'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currencypair',
            name='ask',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='currencypair',
            name='base_volume',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='currencypair',
            name='bid',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='currencypair',
            name='last',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='currencypair',
            name='quote_volume',
            field=models.FloatField(default=0),
        ),
    ]