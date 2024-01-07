# Generated by Django 4.2.6 on 2023-12-31 08:09

from django.db import migrations, models
import django_enum_choices.choice_builders
import django_enum_choices.fields
import src.other.enums


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0002_product_unload_service"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="image",
            field=models.ImageField(
                blank=True,
                max_length=255,
                null=True,
                upload_to="products/",
                verbose_name="Изображение",
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="rim_type",
            field=models.IntegerField(
                blank=True,
                choices=[("0", "0"), ("1", "1"), ("2", "2"), ("3", "3")],
                default=0,
                max_length=1,
                null=True,
                verbose_name="Тип дисков",
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="unload_service",
            field=django_enum_choices.fields.EnumChoiceField(
                blank=True,
                choice_builder=django_enum_choices.choice_builders.value_value,
                choices=[
                    ("None", "None"),
                    ("", ""),
                    ("FORTOCHKI", "FORTOCHKI"),
                    ("STARCO", "STARCO"),
                ],
                enum_class=src.other.enums.UnloadServiceType,
                max_length=9,
                null=True,
            ),
        ),
    ]
