# Generated by Django 5.0.3 on 2024-04-12 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0006_alter_illnessdetail_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='illnessdetail',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='created_at'),
        ),
    ]
