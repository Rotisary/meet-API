# Generated by Django 4.2.4 on 2024-09-24 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0020_alter_complaint_patient'),
    ]

    operations = [
        migrations.AlterField(
            model_name='complaint',
            name='sex',
            field=models.CharField(choices=[('male', 'male'), ('female', 'female')]),
        ),
        migrations.AlterField(
            model_name='complaint',
            name='year_of_birth',
            field=models.IntegerField(),
        ),
    ]