# Generated by Django 4.2 on 2024-11-12 08:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gui', '0004_personne_is_active_personne_is_staff_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ecrire',
            name='livre',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ecrire_set', to='gui.livre'),
        ),
    ]
