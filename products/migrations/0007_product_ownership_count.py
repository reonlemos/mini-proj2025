# Generated by Django 5.0.8 on 2025-04-27 15:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_paymenttransaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='ownership_count',
            field=models.PositiveIntegerField(default=1, help_text='Number of times this product has been owned (1 = first owner, 2 = second hand, etc.)'),
        ),
    ]
