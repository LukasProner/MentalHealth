# Generated by Django 5.1 on 2025-01-17 13:40

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MentalHealthApp', '0012_user_is_admin_user_is_staff'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='question_type',
            field=models.CharField(choices=[('boolean', 'Yes/No'), ('choice', 'Multiple Choice'), ('text', 'Text Response'), ('drawing', 'Drawing')], default='boolean', max_length=50),
        ),
        migrations.CreateModel(
            name='Drawing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='drawings/')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='drawing_answears', to='MentalHealthApp.question')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
