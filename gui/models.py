from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from django.utils import timezone
import datetime


class Ville(models.Model):
    nom_ville = models.CharField(max_length=100, primary_key=True)
    code_postal = models.CharField(max_length=10)
    pays = models.CharField(max_length=50)

    class Meta:
        db_table = 'Ville'

    def __str__(self):
        return self.nom_ville

class Adresse(models.Model):
    rue = models.CharField(max_length=255)
    n_rue = models.IntegerField()
    ville = models.ForeignKey(Ville, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Adresse'

    def __str__(self):
        return f"{self.rue}, {self.n_rue}, {self.ville.nom_ville}"

class Role(models.Model):
    type = models.CharField(max_length=50)

    class Meta:
        db_table = 'Role'

    def __str__(self):
        return self.type

class PersonneManager(BaseUserManager):
    def get_by_natural_key(self, email):
        return self.get(email=email)

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('L\'adresse email doit être définie')
        email = self.normalize_email(email)
        extra_fields.pop('email', None)  # Supprimer email des extra_fields si elle existe
        print(f"Creating user with email: {email} and extra_fields: {extra_fields}")
        personne = self.model(email=email, **extra_fields)
        personne.set_password(password)
        personne.save(using=self._db)
        return personne

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class Personne(AbstractBaseUser, PermissionsMixin):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField()
    telephone = models.CharField(max_length=15)
    email = models.EmailField(max_length=50, primary_key=True)  # Champ unique pour l'identification
    date_creation = models.DateField(auto_now_add=True)
    solde = models.DecimalField(max_digits=10, decimal_places=2)
    adresse = models.ForeignKey('Adresse', on_delete=models.CASCADE)
    role = models.ForeignKey('Role', on_delete=models.CASCADE)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = PersonneManager()

    USERNAME_FIELD = 'email'  # Utiliser l'email comme identifiant unique
    REQUIRED_FIELDS = ['nom', 'prenom']

    class Meta:
        db_table = 'Personne'

    def __str__(self):
        return f"{self.nom} {self.prenom}"

class Fournisseur(models.Model):
    nom_fournisseur = models.CharField(max_length=100)
    adresse = models.ForeignKey('Adresse', on_delete=models.CASCADE, null = True)

    class Meta:
        db_table = 'Fournisseur'

    def __str__(self):
        return self.nom_fournisseur

class Editeur(models.Model):
    nom = models.CharField(max_length=100)

    class Meta:
        db_table = 'Editeur'

    def __str__(self):
        return self.nom

class Livre(models.Model):
    isbn13 = models.CharField(max_length=13, primary_key=True)
    titre = models.CharField(max_length=255)
    type = models.CharField(max_length=50, blank=True, null=True)
    genre_litteraire = models.CharField(max_length=100,blank=True, null=True)
    sous_genre = models.CharField(max_length=100,blank=True, null=True)
    langue = models.CharField(max_length=50,blank=True, null=True)
    format = models.CharField(max_length=50,blank=True, null=True)
    nombre_pages = models.IntegerField(blank=True,null=True)
    dimensions = models.CharField(max_length=50,blank=True,null=True)
    date_parution = models.DateField(blank=True,null=True)
    localisation = models.CharField(max_length=100,blank=True,null=True)
    synopsis = models.TextField(blank=True,null=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True)
    url_reference = models.URLField(blank=True, null=True)
    quantite_disponible = models.IntegerField()
    quantite_totale = models.IntegerField()
    quantite_minimale = models.IntegerField()
    editeur = models.ForeignKey(Editeur, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Livre'

    def __str__(self):
        return self.titre

    def save(self, *args, **kwargs):
        # Vérifie si la quantité disponible est en dessous du minimum requis
        notification_exists = Notifier.objects.filter(livre=self, type='quantite_min', termine=False).exists()

        # Si la quantité est en dessous du minimum et qu'aucune notification n'existe, en crée une
        if self.quantite_disponible < self.quantite_minimale:
            if not notification_exists:
                Notifier.objects.create(
                    personne=None,  # Pas de personne spécifique
                    livre=self,
                    quantite=self.quantite_disponible,
                    type='quantite_min',
                    commentaire=f"La quantité disponible de '{self.titre}' est en dessous du seuil minimum ({self.quantite_minimale})."
                )
        else:
            # Si la quantité est au-dessus du minimum et une notification existe, la supprimer
            if notification_exists:
                notification = Notifier.objects.filter(livre=self, type='quantite_min', termine=False).first()
                notification.delete()

        # Appelle la méthode save de la classe parente pour effectuer la sauvegarde réelle
        super().save(*args, **kwargs)

class Auteur(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField(blank=True,null=True)

    class Meta:
        db_table = 'Auteur'

    def __str__(self):
        return f"{self.nom} {self.prenom}"
class Ecrire(models.Model):
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE, related_name="ecrire_set")
    auteur = models.ForeignKey(Auteur, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Ecrire'

    def __str__(self):
        return f"{self.auteur.nom} a écrit {self.livre.titre}"

class Illustrateur(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField(blank=True,null=True)

    class Meta:
        db_table = 'Illustrateur'

    def __str__(self):
        return f"{self.nom} {self.prenom}"
class Illustrer(models.Model):
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE, related_name="illustrer_set")
    illustrateur = models.ForeignKey(Illustrateur, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Illustrer'

    def __str__(self):
        return f"{self.illustrateur.nom} a écrit {self.livre.titre}"

class Traducteur(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField(blank=True,null=True)

    class Meta:
        db_table = 'Traducteur'

    def __str__(self):
        return f"{self.nom} {self.prenom}"
class Traduire(models.Model):
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE, related_name="traduire_set")
    traducteur = models.ForeignKey(Traducteur, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Traduire'

    def __str__(self):
        return f"{self.traducteur.nom} a écrit {self.livre.titre}"

class Achat(models.Model):
    personne = models.ForeignKey(Personne, on_delete=models.CASCADE)
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE)
    date_achat = models.DateField(default=datetime.date.today)
    quantite = models.PositiveIntegerField()


    class Meta:
        db_table = 'Achat'

    def __str__(self):
        return f"Achat de {self.quantite} exemplaire(s) de {self.livre.titre} par {self.personne.nom}"


    def __str__(self):
        return f"Achat de {self.quantite} exemplaire(s) de {self.livre.titre} par {self.personne.nom}"

class Commander(models.Model):
    STATUT_CHOICES = [
        ('en cours', 'En cours'),
        ('terminé', 'Terminé'),
    ]

    personne = models.ForeignKey(Personne, on_delete=models.CASCADE)
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE)
    date_commande = models.DateField(default=datetime.date.today)
    quantite = models.PositiveIntegerField()
    fournisseur = models.ForeignKey(Fournisseur, null=True, blank=True, on_delete=models.SET_NULL)  # Replace 1 with the actual Fournisseur ID
    statut = models.CharField(max_length=50, choices=STATUT_CHOICES, default='en cours')


    class Meta:
        db_table = 'Commander'

    def __str__(self):
        return f"Commande de {self.quantite} exemplaire(s) de {self.livre.titre} par {self.personne.nom}"


class Reserver(models.Model):
    STATUT_CHOICES = [
        ('en cours', 'En cours'),
        ('terminé', 'Terminé'),
    ]
    personne = models.ForeignKey(Personne, on_delete=models.CASCADE)
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE)
    date_reservation = models.DateField(default=datetime.date.today)
    quantite = models.PositiveIntegerField()
    statut = models.CharField(max_length=50,choices=STATUT_CHOICES, default='en cours')


    class Meta:
        db_table = 'Reserver'

    def __str__(self):
        return f"Réservation de {self.quantite} exemplaire(s) de {self.livre.titre} par {self.personne.nom}"

class Notifier(models.Model):
    personne = models.ForeignKey(Personne, on_delete=models.CASCADE, null=True, blank=True)  # Autorise les valeurs NULL
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE)
    quantite = models.IntegerField()
    type = models.CharField(max_length=50)
    commentaire = models.TextField()
    date_creation = models.DateTimeField(default=timezone.now)
    termine = models.BooleanField(default=False)

    class Meta:
        db_table = 'Notifier'

    def __str__(self):
        return f"Notification pour {self.livre.titre} ({self.type})"