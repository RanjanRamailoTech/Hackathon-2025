# Generated by Django 5.1.6 on 2025-03-04 11:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Job_opening', '0001_initial'),
        ('client_auth', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobopening',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='client_auth.company'),
        ),
        migrations.DeleteModel(
            name='Company',
        ),
    ]
