# Generated by Django 3.2.18 on 2023-04-12 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0006_auto_20230316_1931'),
    ]

    operations = [
        migrations.AddField(
            model_name='retailaccount',
            name='cancel_subscription',
            field=models.BooleanField(default=False),
        ),
    ]
