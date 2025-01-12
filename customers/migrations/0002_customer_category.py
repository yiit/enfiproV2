# Generated by Django 4.1.5 on 2025-01-04 20:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_remove_product_prices_product_price_and_more'),
        ('customers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='category',
            field=models.ForeignKey(db_column='category', default=1, on_delete=django.db.models.deletion.CASCADE, related_query_name='customer_category', to='products.category'),
            preserve_default=False,
        ),
    ]