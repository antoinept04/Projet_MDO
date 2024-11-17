# Generated by Django 5.1.3 on 2024-11-17 18:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gui', '0002_alter_notifier_personne'),
    ]

    operations = [
        migrations.RenameField(
            model_name='fournisseur',
            old_name='nom',
            new_name='nom_fournisseur',
        ),
        migrations.AddField(
            model_name='commander',
            name='fournisseur',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='gui.fournisseur'),
        ),
        migrations.AlterField(
            model_name='commander',
            name='quantite',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='commander',
            name='statut',
            field=models.CharField(choices=[('en cours', 'En cours'), ('terminé', 'Terminé')], max_length=50),
        ),
    ]
