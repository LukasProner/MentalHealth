# Generated by Django 5.1 on 2024-11-26 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MentalHealthApp', '0006_remove_testsubmission_user_testsubmission_test_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='test_code',
            field=models.CharField(blank=True, max_length=10, unique=True),
        ),
    ]
