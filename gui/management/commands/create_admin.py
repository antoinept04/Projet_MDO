# gestion/commands/create_admin.py

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from gui.models import Personne, Adresse, Ville, Role

class Command(BaseCommand):
    help = 'Créer un superutilisateur (admin) avec des valeurs prédéfinies.'

    def handle(self, *args, **options):
        # Informations prédéfinies pour le superutilisateur
        email = "admin@gmail.com"
        password = "test1234"
        nom = "Admin"
        prenom = "Super"
        date_naissance = timezone.now().date()
        telephone = "0123456789"
        solde = 1000.00  # Solde initial arbitraire

        # Informations prédéfinies pour la ville
        nom_ville = "Paris"
        code_postal = "75000"
        pays = "France"

        # Informations prédéfinies pour l'adresse
        rue = "Rue de Exemple"
        n_rue = "123"

        # Création ou récupération de la ville
        ville, created = Ville.objects.get_or_create(
            nom_ville=nom_ville,
            code_postal=code_postal,
            defaults={'pays': pays}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Ville '{nom_ville}' créée."))
        else:
            self.stdout.write(self.style.WARNING(f"Ville '{nom_ville}' existante utilisée."))

        # Création ou récupération de l'adresse
        adresse, created = Adresse.objects.get_or_create(
            rue=rue,
            n_rue=n_rue,
            ville=ville
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Adresse '{rue} {n_rue}' créée."))
        else:
            self.stdout.write(self.style.WARNING(f"Adresse '{rue} {n_rue}' existante utilisée."))

        # Création ou récupération du rôle 'admin'
        role_admin, created = Role.objects.get_or_create(
            type='admin'
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Rôle 'admin' créé."))
        else:
            self.stdout.write(self.style.WARNING(f"Rôle 'admin' existant utilisé."))

        # Vérifier si l'utilisateur existe déjà
        if Personne.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f"Un utilisateur avec l'email '{email}' existe déjà."))
            return

        # Création du superutilisateur
        superuser = Personne.objects.create_superuser(
            email=email,
            password=password,
            nom=nom,
            prenom=prenom,
            date_naissance=date_naissance,
            telephone=telephone,
            adresse=adresse,
            solde=solde,
            role=role_admin
        )

        self.stdout.write(self.style.SUCCESS(f"Superutilisateur créé : {superuser.email}"))
