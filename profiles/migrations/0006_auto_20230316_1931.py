# Generated by Django 3.2.18 on 2023-03-16 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0005_useraccount_retailer_requested'),
    ]

    operations = [
        migrations.AddField(
            model_name='retailaccount',
            name='subscribed',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='retailaccount',
            name='first_name',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='retailaccount',
            name='last_name',
            field=models.CharField(default='', max_length=50),
        ),
    ]
