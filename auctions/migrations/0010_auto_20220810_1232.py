# Generated by Django 3.2.5 on 2022-08-10 11:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0009_transactionreference_bid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transactionreference',
            name='bid',
        ),
        migrations.AddField(
            model_name='transactionreference',
            name='auctionlistings',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='auctions.auctionlistings'),
            preserve_default=False,
        ),
    ]
