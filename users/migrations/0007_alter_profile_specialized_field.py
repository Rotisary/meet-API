# Generated by Django 5.0.3 on 2024-04-20 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_alter_profile_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='specialized_field',
            field=models.TextField(choices=[('EY', 'opthamologist'), ('ENT', 'otolaryngologist'), ('SK', 'dermatologist'), ('DT', 'dentist'), ('BN', 'physiotherapist'), ('PN', 'physician'), ('UTI', 'urologist'), ('SOI', 'gynecologist')]),
        ),
    ]