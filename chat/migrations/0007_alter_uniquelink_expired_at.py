# Generated by Django 5.1.2 on 2024-12-13 14:59

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0006_alter_uniquelink_expired_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uniquelink',
            name='expired_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 12, 13, 16, 59, 10, 912714, tzinfo=datetime.timezone.utc)),
        ),
    ]