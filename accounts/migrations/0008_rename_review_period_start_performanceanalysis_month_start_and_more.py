# Generated by Django 5.1.4 on 2024-12-17 15:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_performanceanalysis'),
    ]

    operations = [
        migrations.RenameField(
            model_name='performanceanalysis',
            old_name='review_period_start',
            new_name='month_start',
        ),
        migrations.RemoveField(
            model_name='performanceanalysis',
            name='review_period_end',
        ),
    ]