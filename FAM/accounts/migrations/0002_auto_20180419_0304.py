# Generated by Django 2.0.4 on 2018-04-19 03:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cryptoinvestment',
            old_name='purchase_date',
            new_name='date',
        ),
        migrations.RenameField(
            model_name='optioninvestment',
            old_name='purchase_date',
            new_name='date',
        ),
        migrations.RenameField(
            model_name='stockinvestment',
            old_name='purchase_date',
            new_name='date',
        ),
    ]
