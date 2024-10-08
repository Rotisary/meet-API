# Generated by Django 4.2.4 on 2024-09-20 02:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0016_alter_illness_treated_by'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='illness',
            name='age',
        ),
        migrations.AddField(
            model_name='illness',
            name='age_group',
            field=models.CharField(choices=[('PT', 'Preteen'), ('TN', 'Teenager'), ('AD', 'Adult'), ('OAD', 'Old Adult')], default='PT'),
        ),
        migrations.AlterField(
            model_name='illness',
            name='body_part',
            field=models.CharField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='illness',
            name='specific_illness',
            field=models.CharField(blank=True, null=True),
        ),
    ]
