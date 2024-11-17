# Generated by Django 5.1.3 on 2024-11-17 19:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gui', '0004_remove_commander_fournisseur'),
    ]

    operations = [
        migrations.AddField(
            model_name='commander',
            name='fournisseur',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='gui.fournisseur'),
        ),
    ]
