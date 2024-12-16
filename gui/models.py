from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from django.core.mail import send_mail
from django.utils import timezone
import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum
from decimal import Decimal

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

    """class Meta:
        db_table = 'Adresse'"""

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

        # Méthode pour calculer le total des livres achetés

    def calculer_total_livres_achetes(self):
        total = Achat.objects.filter(personne=self).aggregate(Sum('quantite'))['quantite__sum']
        return total if total else 0

        # Méthode pour mettre à jour le solde

    from decimal import Decimal  # Import pour des calculs précis

    def mise_a_jour_solde(self):
        # Calcul du nouveau total des livres après le dernier achat
        nouveau_total_livres = self.calculer_total_livres_achetes()

        # Récupérer le dernier achat
        dernier_achat = Achat.objects.filter(personne=self).order_by('-id').first()

        if dernier_achat:
            # Calcul de l'ancien total en soustrayant la quantité du dernier achat
            ancien_total_livres = nouveau_total_livres - dernier_achat.quantite
        else:
            # Si aucun achat précédent, ancien total est simplement 0
            ancien_total_livres = 0

        # Calcul du nombre de multiples de 10 atteints entre l'ancien et le nouveau total
        multiples_atteints = (nouveau_total_livres // 10) - (ancien_total_livres // 10)

        if multiples_atteints > 0:  # Si un ou plusieurs multiples de 10 ont été atteints
            achats = Achat.objects.filter(personne=self).order_by('-id')  # Trier par id décroissant
            livres_consideres = []
            livres_total = 0
            prix_total = Decimal('0.0')

            # Parcourir les achats dans l'ordre des plus récents
            for achat in achats:
                for _ in range(achat.quantite):  # Ajouter chaque exemplaire du livre
                    if achat.livre.prix is None:
                        continue  # Ignorer si le prix est None
                    livres_consideres.append(achat.livre)
                    livres_total += 1
                    prix_total += achat.livre.prix

                    # Arrêter quand on atteint les livres nécessaires pour les multiples atteints
                    if livres_total == multiples_atteints * 10:
                        break
                if livres_total == multiples_atteints * 10:
                    break

            # Calcul de la remise sur les livres nécessaires
            remise = prix_total * Decimal('0.05')  # 5% de remise
            self.solde += remise
            self.save()
class Fournisseur(models.Model):
    nom_fournisseur = models.CharField(max_length=100)
    adresses = models.ManyToManyField(
        'Adresse',
        through='FournisseurAdresse',
        related_name='fournisseurs'
    )

    class Meta:
        db_table = 'Fournisseur'

    def __str__(self):
        return self.nom_fournisseur
class FournisseurAdresse(models.Model):
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE)
    adresse = models.ForeignKey(Adresse, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('fournisseur', 'adresse')

    def __str__(self):
        return f"{self.fournisseur.nom_fournisseur} - {self.adresse}"
class Editeur(models.Model):
    nom = models.CharField(max_length=100)

    class Meta:
        db_table = 'Editeur'

    def __str__(self):
        return self.nom

class Contributeur(models.Model):
    TYPE_CHOICES = [
        ('Auteur', 'Auteur'),
        ('Traducteur', 'Traducteur'),
        ('Illustrateur', 'Illustrateur'),
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField(blank=True, null=True)
    class Meta:
        db_table = 'Contributeur'
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
    prix = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    url_reference = models.URLField(blank=True, null=True)
    quantite_disponible = models.PositiveIntegerField()
    quantite_minimale = models.PositiveIntegerField(default=1)
    editeur = models.ForeignKey(Editeur, on_delete=models.CASCADE)
    contributeurs = models.ManyToManyField(Contributeur)

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


class Achat(models.Model):
    personne = models.ForeignKey(Personne, on_delete=models.CASCADE)
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE)
    date_achat = models.DateField(default=datetime.date.today)
    quantite = models.PositiveIntegerField()

    class Meta:
        db_table = 'Achat'

    def __str__(self):
        return f"Achat de {self.quantite} exemplaire(s) de {self.livre.titre} par {self.personne.nom}"

    def save(self, *args, **kwargs):
        # Vérification si l'objet est nouveau
        is_new = self.pk is None

        # Validation de la quantité
        if self.quantite > self.livre.quantite_disponible:
            raise ValueError(
                f"Stock insuffisant pour le livre '{self.livre.titre}'. "
                f"Disponible : {self.livre.quantite_disponible}, demandé : {self.quantite}."
            )

        super().save(*args, **kwargs)  # Enregistrement de l'achat

        # Mise à jour du stock du livre (uniquement si l'achat est nouveau)
        if is_new:
            self.livre.quantite_disponible -= self.quantite
            self.livre.save()


@receiver(post_save, sender=Achat)
def verifier_fidelite(sender, instance, created, **kwargs):
    if created:  # Vérifie si un achat vient d'être créé
        instance.personne.mise_a_jour_solde()
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
    TYPE_CHOICES = [
        ('commande', 'Commande'),
        ('reservation', 'Reservation'),
        ('quantite_min', 'Quantite min'),
    ]
    personne = models.ForeignKey(Personne, on_delete=models.CASCADE, null=True, blank=True)  # Autorise les valeurs NULL
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE)
    quantite = models.IntegerField()
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    commentaire = models.TextField()
    date_creation = models.DateTimeField(default=timezone.now)
    termine = models.BooleanField(default=False)

    class Meta:
        db_table = 'Notifier'

    def __str__(self):
        return f"Notification pour {self.livre.titre} ({self.type})"

# Signal pour envoyer un mail lors de la création d'une notification
@receiver(post_save, sender=Notifier)
def send_notification_email(sender, instance, created, **kwargs):
    if created:  # Si l'objet a été créé
        subject = f"Nouvelle notification pour le livre {instance.livre.titre}"
        message = f"Une nouvelle notification a été créée pour le livre '{instance.livre.titre}'.\n\n" \
                  f"Type : {instance.get_type_display()}\n" \
                  f"Quantité : {instance.quantite}\n" \
                  f"Commentaire : {instance.commentaire}\n" \
                  f"Date : {instance.date_creation.strftime('%d/%m/%Y %H:%M:%S')}"
        recipient_list = ['sachamalray2000@gmail.com']  # Remplace par l'email cible

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            fail_silently=False,  # Pour ne pas échouer silencieusement en cas d'erreur d'envoi
        )