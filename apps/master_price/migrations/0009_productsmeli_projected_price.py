# Generated by Django 5.1 on 2024-10-10 05:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("master_price", "0008_sopifyproducts_shipment_cost"),
    ]

    operations = [
        migrations.AddField(
            model_name="productsmeli",
            name="projected_price",
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]
