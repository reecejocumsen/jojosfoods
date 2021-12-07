# Generated by Django 3.2.6 on 2021-10-24 08:25

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20211024_1824'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='category',
            field=models.CharField(choices=[('E', 'Eggs'), ('M', 'Meat'), ('F', 'Fruit'), ('O', 'Other'), ('L', 'Legumes and Nuts'), ('V', 'Vegetables'), ('H', 'Herbs'), ('D', 'Dairy')], default='O', max_length=1),
        ),
        migrations.AlterField(
            model_name='item',
            name='quality',
            field=models.CharField(choices=[('B', 'B'), ('U', 'Unrated'), ('A', 'A'), ('A+', 'A+'), ('C', 'C')], default='U', max_length=2),
        ),
        migrations.AlterField(
            model_name='item',
            name='unit',
            field=models.CharField(choices=[('L', 'litres'), ('dozen', 'dozen'), ('kg', 'kilograms'), ('mL', 'millilitres'), ('g', 'grams')], default='kg', max_length=5),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.IntegerField(choices=[(3, 'Delivered'), (-1, 'Cancelled'), (2, 'In transit'), (1, 'Confirmed by seller'), (0, 'Placed')], default=0),
        ),
        migrations.AlterField(
            model_name='userhistory',
            name='last_viewed',
            field=models.DateTimeField(default=datetime.datetime(2021, 10, 24, 18, 25, 54, 191497)),
        ),
    ]