# Generated by Django 4.0.5 on 2022-09-21 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_remove_orderitem_info_remove_orderitem_shop'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='billing_address',
            field=models.CharField(default='snsjshsh', max_length=30),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='profile',
            name='address',
            field=models.CharField(default='dyudydd', max_length=255),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='Address',
        ),
    ]
