# Generated by Django 5.1.7 on 2025-04-13 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('complaints', '0009_alter_complaint_complaint_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='complaint',
            name='complaint_type',
            field=models.CharField(choices=[('Transport', 'Transport'), ('Mess', 'Mess'), ('Maintenance', 'Maintenance'), ('Other', 'Other')], default='Other', max_length=30),
        ),
    ]
