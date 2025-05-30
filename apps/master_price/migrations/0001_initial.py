# Generated by Django 5.1 on 2025-03-14 01:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="MainProducts",
            fields=[
                (
                    "id_variantShopi",
                    models.CharField(max_length=300, primary_key=True, serialize=False),
                ),
                ("id_product", models.CharField(max_length=300)),
                ("sku", models.CharField(blank=True, max_length=100, null=True)),
                ("utility", models.FloatField(blank=True, default=0, null=True)),
                ("items_number", models.IntegerField(default=0)),
                (
                    "commission_seller",
                    models.FloatField(blank=True, default=0, null=True),
                ),
                ("publicity", models.FloatField(blank=True, default=0, null=True)),
                ("aditional", models.FloatField(blank=True, default=0, null=True)),
                (
                    "packaging_cost",
                    models.IntegerField(blank=True, default=0, null=True),
                ),
                ("image_link", models.CharField(blank=True, max_length=500, null=True)),
                ("title", models.CharField(blank=True, max_length=300, null=True)),
                ("stock", models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name="OAuthToken",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("access_token", models.TextField()),
                ("refresh_token", models.TextField()),
                ("expires_at", models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name="StatusProcess",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=20, unique=True)),
                ("status", models.CharField(max_length=50)),
                ("progress", models.IntegerField(default=0)),
                ("init", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="melonn",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "publication",
                    models.CharField(blank=True, max_length=50, null=True, unique=True),
                ),
                ("stock", models.IntegerField(blank=True, default=0, null=True)),
                ("commission", models.SmallIntegerField(default=0)),
                ("shipment_cost", models.FloatField(blank=True, default=0, null=True)),
                (
                    "url_publication",
                    models.CharField(blank=True, max_length=200, null=True),
                ),
                ("status", models.CharField(blank=True, max_length=50, null=True)),
                ("Price", models.FloatField(blank=True, default=0, null=True)),
                (
                    "main_product",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="master_price.mainproducts",
                        verbose_name="main_product",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ProductsFala",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "publication",
                    models.CharField(blank=True, max_length=50, null=True, unique=True),
                ),
                ("stock", models.IntegerField(blank=True, default=0, null=True)),
                ("commission", models.SmallIntegerField(default=0)),
                ("shipment_cost", models.FloatField(blank=True, default=0, null=True)),
                (
                    "url_publication",
                    models.CharField(blank=True, max_length=200, null=True),
                ),
                ("status", models.CharField(blank=True, max_length=50, null=True)),
                ("Price", models.FloatField(blank=True, default=0, null=True)),
                (
                    "main_product",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="master_price.mainproducts",
                        verbose_name="main_product",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ProductsMeli",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "publication",
                    models.CharField(blank=True, max_length=50, null=True, unique=True),
                ),
                ("stock", models.IntegerField(blank=True, default=0, null=True)),
                ("commission", models.SmallIntegerField(default=0)),
                ("shipment_cost", models.FloatField(blank=True, default=0, null=True)),
                (
                    "url_publication",
                    models.CharField(blank=True, max_length=200, null=True),
                ),
                ("status", models.CharField(blank=True, max_length=50, null=True)),
                ("Price", models.FloatField(blank=True, default=0, null=True)),
                (
                    "crossed_out_price",
                    models.FloatField(blank=True, default=0, null=True),
                ),
                (
                    "main_product",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="master_price.mainproducts",
                        verbose_name="main_product",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ProductsSodimac",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "publication",
                    models.CharField(blank=True, max_length=50, null=True, unique=True),
                ),
                ("stock", models.IntegerField(blank=True, default=0, null=True)),
                ("commission", models.SmallIntegerField(default=0)),
                ("shipment_cost", models.FloatField(blank=True, default=0, null=True)),
                (
                    "url_publication",
                    models.CharField(blank=True, max_length=200, null=True),
                ),
                ("status", models.CharField(blank=True, max_length=50, null=True)),
                ("Price", models.FloatField(blank=True, default=0, null=True)),
                (
                    "ean",
                    models.CharField(blank=True, max_length=15, null=True, unique=True),
                ),
                (
                    "main_product",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="master_price.mainproducts",
                        verbose_name="main_product",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="SopifyProducts",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("tags", models.CharField(blank=True, max_length=500, null=True)),
                ("vendor", models.CharField(blank=True, max_length=100, null=True)),
                ("status", models.CharField(blank=True, max_length=100, null=True)),
                (
                    "compare_at_price",
                    models.FloatField(blank=True, default=0, null=True),
                ),
                ("barcode", models.CharField(blank=True, max_length=100, null=True)),
                ("cursor", models.CharField(blank=True, max_length=80, null=True)),
                (
                    "margen_comparacion_db",
                    models.FloatField(blank=True, default=0, null=True),
                ),
                (
                    "commission_platform",
                    models.FloatField(blank=True, default=0, null=True),
                ),
                ("category", models.CharField(blank=True, max_length=500, null=True)),
                (
                    "MainProducts",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="master_price.mainproducts",
                        verbose_name="main_product",
                    ),
                ),
            ],
        ),
    ]
