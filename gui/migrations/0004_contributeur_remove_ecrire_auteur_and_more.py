# Generated by Django 5.1.3 on 2024-12-08 21:11

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gui', '0003_alter_notifier_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contributeur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('Auteur', 'Auteur'), ('Traducteur', 'Traducteur'), ('Illustrateur', 'Illustrateur')], max_length=20)),
                ('nom', models.CharField(max_length=100)),
                ('prenom', models.CharField(max_length=100)),
                ('date_naissance', models.DateField(blank=True, null=True)),
            ],
            options={
                'db_table': 'Contributeur',
            },
        ),
        migrations.RemoveField(
            model_name='ecrire',
            name='auteur',
        ),
        migrations.RemoveField(
            model_name='ecrire',
            name='livre',
        ),
        migrations.RemoveField(
            model_name='illustrer',
            name='illustrateur',
        ),
        migrations.RemoveField(
            model_name='illustrer',
            name='livre',
        ),
        migrations.RemoveField(
            model_name='traduire',
            name='traducteur',
        ),
        migrations.RemoveField(
            model_name='traduire',
            name='livre',
        ),
        migrations.RemoveField(
            model_name='livre',
            name='quantite_totale',
        ),
        migrations.AlterField(
            model_name='livre',
            name='prix',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10),
        ),
        migrations.AlterField(
            model_name='livre',
            name='quantite_disponible',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='livre',
            name='quantite_minimale',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='livre',
            name='contributeurs',
            field=models.ManyToManyField(to='gui.contributeur'),
        ),
        migrations.DeleteModel(
            name='Auteur',
        ),
        migrations.DeleteModel(
            name='Ecrire',
        ),
        migrations.DeleteModel(
            name='Illustrateur',
        ),
        migrations.DeleteModel(
            name='Illustrer',
        ),
        migrations.DeleteModel(
            name='Traducteur',
        ),
        migrations.DeleteModel(
            name='Traduire',
        ),
    ]
