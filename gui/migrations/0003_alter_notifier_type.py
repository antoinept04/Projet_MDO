# Generated by Django 4.2 on 2024-12-06 12:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gui', '0002_alter_fournisseuradresse_table'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notifier',
            name='type',
            field=models.CharField(choices=[('commande', 'Commande'), ('reservation', 'Reservation'), ('quantite_min', 'Quantite min')], max_length=50),
        ),
    ]