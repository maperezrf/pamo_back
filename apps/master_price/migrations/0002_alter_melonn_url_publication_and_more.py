# Generated by Django 5.1 on 2025-03-14 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("master_price", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="melonn",
            name="url_publication",
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name="productsfala",
            name="url_publication",
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name="productsmeli",
            name="url_publication",
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name="productssodimac",
            name="url_publication",
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]
