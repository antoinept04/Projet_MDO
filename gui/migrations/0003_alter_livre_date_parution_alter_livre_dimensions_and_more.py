# Generated by Django 4.2.16 on 2024-11-16 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gui', '0002_alter_auteur_date_naissance_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='livre',
            name='date_parution',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='livre',
            name='dimensions',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='livre',
            name='format',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='livre',
            name='genre_litteraire',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='livre',
            name='langue',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='livre',
            name='localisation',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='livre',
            name='nombre_pages',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='livre',
            name='prix',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='livre',
            name='sous_genre',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='livre',
            name='synopsis',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='livre',
            name='type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
