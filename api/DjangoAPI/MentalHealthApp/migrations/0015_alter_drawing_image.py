# Generated by Django 5.1 on 2025-01-17 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MentalHealthApp', '0014_remove_drawing_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='drawing',
            name='image',
            field=models.TextField(),
        ),
    ]
