from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from gui.models import (
    Ville, Adresse, Role, Personne, Editeur, Contributeur, Livre, Fournisseur,
    FournisseurAdresse, Achat, Commander, Reserver, Notifier
)
import datetime

class Command(BaseCommand):
    help = 'Créer un scénario complet avec des données cohérentes pour une présentation technique.'

    def handle(self, *args, **options):
        # ------------------------------------------------------------
        # Création des rôles
        # ------------------------------------------------------------
        roles_data = ['client', 'employe', 'admin']
        roles = {}
        for r in roles_data:
            role_obj, created = Role.objects.get_or_create(type=r)
            roles[r] = role_obj
            if created:
                self.stdout.write(self.style.SUCCESS(f"Rôle '{r}' créé."))
            else:
                self.stdout.write(self.style.WARNING(f"Rôle '{r}' déjà existant."))

        # ------------------------------------------------------------
        # Création des Villes
        # ------------------------------------------------------------
        villes_data = [
            {"nom_ville": "Paris", "code_postal": "75000", "pays": "France"},
            {"nom_ville": "Lyon", "code_postal": "69000", "pays": "France"},
            {"nom_ville": "Marseille", "code_postal": "13000", "pays": "France"},
        ]
        villes = {}
        for v_data in villes_data:
            v, created = Ville.objects.get_or_create(
                nom_ville=v_data["nom_ville"],
                defaults={"code_postal": v_data["code_postal"], "pays": v_data["pays"]}
            )
            villes[v_data["nom_ville"]] = v
            if created:
                self.stdout.write(self.style.SUCCESS(f"Ville '{v_data['nom_ville']}' créée."))
            else:
                self.stdout.write(self.style.WARNING(f"Ville '{v_data['nom_ville']}' déjà existante."))

        # ------------------------------------------------------------
        # Création des Adresses
        # ------------------------------------------------------------
        adresses_data = [
            {"rue": "Rue de la Paix", "n_rue": 10, "ville": villes["Paris"]},
            {"rue": "Avenue des Lumières", "n_rue": 25, "ville": villes["Lyon"]},
            {"rue": "Boulevard du Vieux Port", "n_rue": 5, "ville": villes["Marseille"]},
            {"rue": "Rue de Exemple", "n_rue": 123, "ville": villes["Paris"]}, # utilisée par l'admin
        ]
        adresses = []
        for a_data in adresses_data:
            a, created = Adresse.objects.get_or_create(
                rue=a_data["rue"],
                n_rue=a_data["n_rue"],
                ville=a_data["ville"]
            )
            adresses.append(a)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Adresse '{a.rue} {a.n_rue}, {a.ville.nom_ville}' créée."))
            else:
                self.stdout.write(self.style.WARNING(f"Adresse '{a.rue} {a.n_rue}, {a.ville.nom_ville}' déjà existante."))

        # ------------------------------------------------------------
        # Création de quelques personnes
        # ------------------------------------------------------------
        # On suppose déjà un super admin créé via la commande create_admin (admin@gmail.com)
        # On en crée d'autres pour le scénario
        personnes_data = [
            {
                "email": "client1@gmail.com",
                "password": "test123",
                "nom": "Durand",
                "prenom": "Jean",
                "date_naissance": datetime.date(1985, 5, 20),
                "telephone": "0102030405",
                "adresse": adresses[0],
                "solde": 50.00,
                "role": roles["client"],
                "is_superuser": False,
                "is_staff": False
            },
            {
                "email": "employe1@gmail.com",
                "password": "test123",
                "nom": "Martin",
                "prenom": "Sophie",
                "date_naissance": datetime.date(1990, 3, 15),
                "telephone": "0607080910",
                "adresse": adresses[1],
                "solde": 200.00,
                "role": roles["employe"],
                "is_superuser": False,
                "is_staff": True
            },
            {
                "email": "admin2@gmail.com",
                "password": "test123",
                "nom": "Legrand",
                "prenom": "Camille",
                "date_naissance": datetime.date(1975, 10, 5),
                "telephone": "0505050505",
                "adresse": adresses[2],
                "solde": 500.00,
                "role": roles["admin"],
                "is_superuser": True,
                "is_staff": True
            }
        ]

        personnes = []
        for p_data in personnes_data:
            if Personne.objects.filter(email=p_data["email"]).exists():
                self.stdout.write(self.style.WARNING(f"La personne avec email {p_data['email']} existe déjà."))
                personne = Personne.objects.get(email=p_data["email"])
            else:
                personne = Personne.objects.create_user(
                    email=p_data["email"],
                    password=p_data["password"],
                    nom=p_data["nom"],
                    prenom=p_data["prenom"],
                    date_naissance=p_data["date_naissance"],
                    telephone=p_data["telephone"],
                    adresse=p_data["adresse"],
                    solde=p_data["solde"],
                    role=p_data["role"]
                )
                # on met à jour is_superuser/is_staff si nécessaire
                personne.is_superuser = p_data["is_superuser"]
                personne.is_staff = p_data["is_staff"]
                personne.save()
                self.stdout.write(self.style.SUCCESS(f"Personne '{p_data['email']}' créée."))
            personnes.append(personne)

        # ------------------------------------------------------------
        # Création d'un éditeur
        # ------------------------------------------------------------
        editeur, created = Editeur.objects.get_or_create(nom="Editions du Test")
        if created:
            self.stdout.write(self.style.SUCCESS("Éditeur 'Editions du Test' créé."))
        else:
            self.stdout.write(self.style.WARNING("Éditeur 'Editions du Test' déjà existant."))

        # ------------------------------------------------------------
        # Création de contributeurs
        # ------------------------------------------------------------
        contributeurs_data = [
            {"type": "Auteur", "nom": "Hugo", "prenom": "Victor", "date_naissance": datetime.date(1802, 2, 26)},
            {"type": "Auteur", "nom": "Zola", "prenom": "Emile", "date_naissance": datetime.date(1840, 4, 2)},
            {"type": "Illustrateur", "nom": "Dupont", "prenom": "Marie", "date_naissance": datetime.date(1970, 7, 10)},
        ]
        contributeurs = []
        for c_data in contributeurs_data:
            c, created = Contributeur.objects.get_or_create(
                nom=c_data["nom"],
                prenom=c_data["prenom"],
                type=c_data["type"],
                defaults={"date_naissance": c_data["date_naissance"]}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Contributeur {c.nom} {c.prenom} créé."))
            else:
                self.stdout.write(self.style.WARNING(f"Contributeur {c.nom} {c.prenom} déjà existant."))
            contributeurs.append(c)

        # ------------------------------------------------------------
        # Création de livres
        # ------------------------------------------------------------
        livres_data = [
            {
                "isbn13": "9781234567897",
                "titre": "Les Misérables",
                "type": "Roman",
                "genre_litteraire": "Littérature classique",
                "sous_genre": "Roman historique",
                "langue": "Français",
                "format": "Broché",
                "nombre_pages": 1200,
                "dimensions": "15x22 cm",
                "date_parution": datetime.date(1862, 1, 1),
                "localisation": "Rayon Classiques",
                "synopsis": "Une fresque épique sur la France du XIXe siècle.",
                "prix": Decimal("29.90"),
                "url_reference": "http://example.com/lesmiserables",
                "quantite_disponible": 15,
                "quantite_minimale": 5,
                "editeur": editeur,
                "contributeurs": [contributeurs[0]]
            },
            {
                "isbn13": "9780987654321",
                "titre": "Au Bonheur des Dames",
                "type": "Roman",
                "genre_litteraire": "Littérature classique",
                "sous_genre": "Roman réaliste",
                "langue": "Français",
                "format": "Broché",
                "nombre_pages": 500,
                "dimensions": "14x20 cm",
                "date_parution": datetime.date(1883, 1, 1),
                "localisation": "Rayon Classiques",
                "synopsis": "La vie d'un grand magasin parisien au XIXe siècle.",
                "prix": Decimal("19.90"),
                "url_reference": "http://example.com/aubonheurdesdames",
                "quantite_disponible": 8,
                "quantite_minimale": 5,
                "editeur": editeur,
                "contributeurs": [contributeurs[1]]
            },
            {
                "isbn13": "9781111111111",
                "titre": "Livre Illustré pour Enfants",
                "type": "Album",
                "genre_litteraire": "Jeunesse",
                "sous_genre": "Album illustré",
                "langue": "Français",
                "format": "Relié",
                "nombre_pages": 40,
                "dimensions": "20x20 cm",
                "date_parution": datetime.date(2020, 5, 1),
                "localisation": "Rayon Enfants",
                "synopsis": "Un livre avec de belles illustrations.",
                "prix": Decimal("9.90"),
                "url_reference": "http://example.com/livreillus",
                "quantite_disponible": 3,  # volontairement bas
                "quantite_minimale": 5,
                "editeur": editeur,
                "contributeurs": [contributeurs[2]]
            }
        ]

        livres = []
        for l_data in livres_data:
            # On supprime contributeurs de l_data avant create
            contribs = l_data.pop("contributeurs")
            l, created = Livre.objects.get_or_create(**l_data)
            if created:
                l.contributeurs.set(contribs)
                l.save()
                self.stdout.write(self.style.SUCCESS(f"Livre '{l.titre}' créé."))
            else:
                self.stdout.write(self.style.WARNING(f"Livre '{l.titre}' déjà existant."))
            livres.append(l)

        # ------------------------------------------------------------
        # Création de fournisseurs
        # ------------------------------------------------------------
        fournisseurs_data = [
            {
                "nom_fournisseur": "Fournisseur General",
                "adresses": [
                    {"rue": "Rue Fournisseur", "n_rue": 99, "ville": villes["Paris"]}
                ]
            }
        ]

        for f_data in fournisseurs_data:
            f, created = Fournisseur.objects.get_or_create(nom_fournisseur=f_data["nom_fournisseur"])
            if created:
                self.stdout.write(self.style.SUCCESS(f"Fournisseur '{f.nom_fournisseur}' créé."))
            else:
                self.stdout.write(self.style.WARNING(f"Fournisseur '{f.nom_fournisseur}' déjà existant."))

            # Ajout des adresses du fournisseur
            for addr_data in f_data["adresses"]:
                addr_f, _ = Adresse.objects.get_or_create(rue=addr_data["rue"], n_rue=addr_data["n_rue"], ville=addr_data["ville"])
                FournisseurAdresse.objects.get_or_create(fournisseur=f, adresse=addr_f)

        # ------------------------------------------------------------
        # Création d'achats (pour tester le système de fidélité)
        # ------------------------------------------------------------
        # On fait acheter à un client plusieurs livres
        client = Personne.objects.get(email="client1@gmail.com")
        achats_data = [
            {"personne": client, "livre": livres[0], "quantite": 1},  # Les Misérables
            {"personne": client, "livre": livres[1], "quantite": 2},  # Au Bonheur des Dames
            {"personne": client, "livre": livres[1], "quantite": 3},  # Au Bonheur des Dames encore
            {"personne": client, "livre": livres[0], "quantite": 4},  # Les Misérables encore
        ]

        for a_data in achats_data:
            a = Achat.objects.create(**a_data)
            self.stdout.write(self.style.SUCCESS(
                f"Achat créé: {a.personne.nom} a acheté {a.quantite}x {a.livre.titre}"
            ))

        # ------------------------------------------------------------
        # Création de commandes (Commander) par l'employé (simulation de réapprovisionnement)
        # ------------------------------------------------------------
        employe = Personne.objects.get(email="employe1@gmail.com")
        fournisseur = Fournisseur.objects.get(nom_fournisseur="Fournisseur General")
        commandes_data = [
            {"personne": employe, "livre": livres[2], "quantite": 10, "fournisseur": fournisseur, "statut": "en cours"},
            {"personne": employe, "livre": livres[1], "quantite": 5, "fournisseur": fournisseur, "statut": "en cours"},
        ]

        for c_data in commandes_data:
            c = Commander.objects.create(**c_data)
            self.stdout.write(self.style.SUCCESS(
                f"Commande créée: {c.personne.nom} commande {c.quantite}x {c.livre.titre}"
            ))

        # ------------------------------------------------------------
        # Création de réservations (Reserver) par le client
        # ------------------------------------------------------------
        reservations_data = [
            {"personne": client, "livre": livres[0], "quantite": 2, "statut": "en cours"},
            {"personne": client, "livre": livres[2], "quantite": 1, "statut": "en cours"},
        ]

        for r_data in reservations_data:
            r = Reserver.objects.create(**r_data)
            self.stdout.write(self.style.SUCCESS(
                f"Réservation créée: {r.personne.nom} réserve {r.quantite}x {r.livre.titre}"
            ))

        # ------------------------------------------------------------
        # Affichage final
        # ------------------------------------------------------------
        self.stdout.write(self.style.SUCCESS("Scénario créé avec succès !"))
