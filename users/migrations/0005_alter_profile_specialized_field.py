# Generated by Django 5.0.3 on 2024-04-12 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='specialized_field',
            field=models.TextField(choices=[('OP', 'opthamologist'), ('ENT', 'otolaryngologist'), ('DY', 'dermatologist'), ('DT', 'dentist'), ('PY', 'physiotherapist'), ('PN', 'physician'), ('UT', 'urologist'), ('GY', 'gynecologist')]),
        ),
    ]
