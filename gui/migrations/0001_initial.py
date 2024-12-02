# Generated by Django 4.2 on 2024-12-02 10:51

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Personne',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('nom', models.CharField(max_length=100)),
                ('prenom', models.CharField(max_length=100)),
                ('date_naissance', models.DateField()),
                ('telephone', models.CharField(max_length=15)),
                ('email', models.EmailField(max_length=50, primary_key=True, serialize=False)),
                ('date_creation', models.DateField(auto_now_add=True)),
                ('solde', models.DecimalField(decimal_places=2, max_digits=10)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'Personne',
            },
        ),
        migrations.CreateModel(
            name='Adresse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rue', models.CharField(max_length=255)),
                ('n_rue', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Auteur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
                ('prenom', models.CharField(max_length=100)),
                ('date_naissance', models.DateField(blank=True, null=True)),
            ],
            options={
                'db_table': 'Auteur',
            },
        ),
        migrations.CreateModel(
            name='Editeur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'Editeur',
            },
        ),
        migrations.CreateModel(
            name='Fournisseur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom_fournisseur', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'Fournisseur',
            },
        ),
        migrations.CreateModel(
            name='Illustrateur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
                ('prenom', models.CharField(max_length=100)),
                ('date_naissance', models.DateField(blank=True, null=True)),
            ],
            options={
                'db_table': 'Illustrateur',
            },
        ),
        migrations.CreateModel(
            name='Livre',
            fields=[
                ('isbn13', models.CharField(max_length=13, primary_key=True, serialize=False)),
                ('titre', models.CharField(max_length=255)),
                ('type', models.CharField(blank=True, max_length=50, null=True)),
                ('genre_litteraire', models.CharField(blank=True, max_length=100, null=True)),
                ('sous_genre', models.CharField(blank=True, max_length=100, null=True)),
                ('langue', models.CharField(blank=True, max_length=50, null=True)),
                ('format', models.CharField(blank=True, max_length=50, null=True)),
                ('nombre_pages', models.IntegerField(blank=True, null=True)),
                ('dimensions', models.CharField(blank=True, max_length=50, null=True)),
                ('date_parution', models.DateField(blank=True, null=True)),
                ('localisation', models.CharField(blank=True, max_length=100, null=True)),
                ('synopsis', models.TextField(blank=True, null=True)),
                ('prix', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('url_reference', models.URLField(blank=True, null=True)),
                ('quantite_disponible', models.IntegerField()),
                ('quantite_totale', models.IntegerField()),
                ('quantite_minimale', models.IntegerField()),
                ('editeur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gui.editeur')),
            ],
            options={
                'db_table': 'Livre',
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'Role',
            },
        ),
        migrations.CreateModel(
            name='Traducteur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
                ('prenom', models.CharField(max_length=100)),
                ('date_naissance', models.DateField(blank=True, null=True)),
            ],
            options={
                'db_table': 'Traducteur',
            },
        ),
        migrations.CreateModel(
            name='Ville',
            fields=[
                ('nom_ville', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('code_postal', models.CharField(max_length=10)),
                ('pays', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'Ville',
            },
        ),
        migrations.CreateModel(
            name='Traduire',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('livre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='traduire_set', to='gui.livre')),
                ('traducteur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gui.traducteur')),
            ],
            options={
                'db_table': 'Traduire',
            },
        ),
        migrations.CreateModel(
            name='Reserver',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_reservation', models.DateField(default=datetime.date.today)),
                ('quantite', models.PositiveIntegerField()),
                ('statut', models.CharField(choices=[('en cours', 'En cours'), ('terminé', 'Terminé')], default='en cours', max_length=50)),
                ('livre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gui.livre')),
                ('personne', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'Reserver',
            },
        ),
        migrations.CreateModel(
            name='Notifier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantite', models.IntegerField()),
                ('type', models.CharField(max_length=50)),
                ('commentaire', models.TextField()),
                ('date_creation', models.DateTimeField(default=django.utils.timezone.now)),
                ('termine', models.BooleanField(default=False)),
                ('livre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gui.livre')),
                ('personne', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'Notifier',
            },
        ),
        migrations.CreateModel(
            name='Illustrer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('illustrateur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gui.illustrateur')),
                ('livre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='illustrer_set', to='gui.livre')),
            ],
            options={
                'db_table': 'Illustrer',
            },
        ),
        migrations.CreateModel(
            name='FournisseurAdresse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('adresse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gui.adresse')),
                ('fournisseur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gui.fournisseur')),
            ],
            options={
                'db_table': 'Fournisseur_adresses',
                'unique_together': {('fournisseur', 'adresse')},
            },
        ),
        migrations.AddField(
            model_name='fournisseur',
            name='adresses',
            field=models.ManyToManyField(related_name='fournisseurs', through='gui.FournisseurAdresse', to='gui.adresse'),
        ),
        migrations.CreateModel(
            name='Ecrire',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('auteur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gui.auteur')),
                ('livre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ecrire_set', to='gui.livre')),
            ],
            options={
                'db_table': 'Ecrire',
            },
        ),
        migrations.CreateModel(
            name='Commander',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_commande', models.DateField(default=datetime.date.today)),
                ('quantite', models.PositiveIntegerField()),
                ('statut', models.CharField(choices=[('en cours', 'En cours'), ('terminé', 'Terminé')], default='en cours', max_length=50)),
                ('fournisseur', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='gui.fournisseur')),
                ('livre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gui.livre')),
                ('personne', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'Commander',
            },
        ),
        migrations.AddField(
            model_name='adresse',
            name='ville',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gui.ville'),
        ),
        migrations.CreateModel(
            name='Achat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_achat', models.DateField(default=datetime.date.today)),
                ('quantite', models.PositiveIntegerField()),
                ('livre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gui.livre')),
                ('personne', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'Achat',
            },
        ),
        migrations.AddField(
            model_name='personne',
            name='adresse',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gui.adresse'),
        ),
        migrations.AddField(
            model_name='personne',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='personne',
            name='role',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gui.role'),
        ),
        migrations.AddField(
            model_name='personne',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions'),
        ),
    ]
