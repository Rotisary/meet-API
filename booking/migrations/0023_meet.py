# Generated by Django 4.2.4 on 2025-03-24 14:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0019_alter_profile_slug'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('booking', '0022_alter_complaint_treated_by_alter_symptom_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Meet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ID', models.CharField(max_length=6)),
                ('has_ended', models.BooleanField(default=False)),
                ('is_confirmed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField()),
                ('complaint', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, related_name='meet_in', to='booking.complaint')),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='meets_booked_for', to='users.profile')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='meets_booked', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
