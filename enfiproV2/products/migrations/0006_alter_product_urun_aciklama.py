# Generated by Django 4.1.5 on 2024-12-27 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_product_urun_aciklama_product_urun_adet_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='urun_aciklama',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
