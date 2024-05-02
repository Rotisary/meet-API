# Generated by Django 5.0.3 on 2024-04-20 11:55

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0009_illness_delete_illnessdetail'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('patient', models.CharField()),
                ('date_of_appointment', models.DateField()),
                ('time_of_appointment', models.TimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created_name')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
