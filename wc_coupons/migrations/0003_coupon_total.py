# Generated by Django 2.0.13 on 2019-03-04 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wc_coupons', '0002_auto_20190304_1343'),
    ]

    operations = [
        migrations.AddField(
            model_name='coupon',
            name='total',
            field=models.FloatField(default=0.0, verbose_name='Total'),
        ),
    ]
