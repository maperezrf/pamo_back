# Generated by Django 5.1 on 2024-10-10 04:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("master_price", "0007_rename_price_sopifyproducts_real_price_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="sopifyproducts",
            name="shipment_cost",
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]
