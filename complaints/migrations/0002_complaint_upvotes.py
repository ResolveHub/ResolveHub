# Generated by Django 5.1.7 on 2025-04-05 08:28

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('complaints', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='complaint',
            name='upvotes',
            field=models.ManyToManyField(blank=True, related_name='upvoted_complaints', to=settings.AUTH_USER_MODEL),
        ),
    ]
