# Generated by Django 5.0.3 on 2024-04-12 13:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_user_phone_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('specialized_field', models.TextField(choices=[('OP', 'opthamologist'), ('ENT', 'otolaryngologist'), ('DY', 'dermatologist'), ('DT', 'dentist'), ('PY', 'physiotherapist'), ('PN', 'physician'), ('UT', 'urologist'), ('GY', 'gynecologist')], default=None)),
                ('doctor_type', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_at')),
                ('meet', models.ManyToManyField(blank=True, related_name='meets', to=settings.AUTH_USER_MODEL)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
