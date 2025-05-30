# Generated by Django 5.0.8 on 2025-04-27 13:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_bid_auction_end_time_bid_payment_processed'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('transaction_id', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('error_message', models.TextField(blank=True, null=True)),
                ('bid', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='payment', to='products.bid')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
