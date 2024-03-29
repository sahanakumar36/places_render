# Generated by Django 4.2.10 on 2024-02-19 00:01

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Locations",
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
                ("name", models.CharField(max_length=500)),
                ("zipcode", models.CharField(blank=True, max_length=200, null=True)),
                ("city", models.CharField(blank=True, max_length=200, null=True)),
                ("country", models.CharField(blank=True, max_length=200, null=True)),
                ("adress", models.CharField(blank=True, max_length=200, null=True)),
                (
                    "travel_type",
                    models.CharField(blank=True, max_length=500, null=True),
                ),
                ("user_id", models.CharField(blank=True, max_length=500, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("edited_at", models.DateTimeField(auto_now=True)),
                ("lat", models.CharField(blank=True, max_length=200, null=True)),
                ("lng", models.CharField(blank=True, max_length=200, null=True)),
                ("place_id", models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
    ]
