# Generated by Django 3.2.5 on 2022-08-11 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0010_auto_20220810_1232'),
    ]

    operations = [
        migrations.AddField(
            model_name='bid',
            name='trx_ref',
            field=models.CharField(default=None, max_length=40),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='TransactionReference',
        ),
    ]
