# Generated by Django 5.0.8 on 2025-04-27 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_bid'),
    ]

    operations = [
        migrations.AddField(
            model_name='bid',
            name='auction_end_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='bid',
            name='payment_processed',
            field=models.BooleanField(default=False),
        ),
    ]
