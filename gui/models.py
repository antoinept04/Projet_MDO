from django.db import models


class Ville(models.Model):
    nom = models.CharField(max_length=100)
    code_postal = models.CharField(max_length=10)
    pays = models.CharField(max_length=50)

    class Meta:
        db_table = 'Ville'

    def __str__(self):
        return self.nom

class Adresse(models.Model):
    rue = models.CharField(max_length=255)
    n_rue = models.IntegerField()
    ville = models.ForeignKey(Ville, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Adresse'

    def __str__(self):
        return f"{self.rue}, {self.n_rue}, {self.ville.nom}"

class Role(models.Model):
    type = models.CharField(max_length=50)

    class Meta:
        db_table = 'Role'

    def __str__(self):
        return self.type

class Personne(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField()
    telephone = models.CharField(max_length=15)
    email = models.EmailField()
    date_creation = models.DateField(auto_now_add=True)
    mot_de_passe = models.CharField(max_length=128)
    solde = models.DecimalField(max_digits=10, decimal_places=2)
    adresse = models.ForeignKey(Adresse, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Personne'

    def __str__(self):
        return f"{self.nom} {self.prenom}"

class Fournisseur(models.Model):
    nom = models.CharField(max_length=100)

    class Meta:
        db_table = 'Fournisseur'

    def __str__(self):
        return self.nom

class Editeur(models.Model):
    nom = models.CharField(max_length=100)

    class Meta:
        db_table = 'Editeur'

    def __str__(self):
        return self.nom

class Auteur(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField()

    class Meta:
        db_table = 'Auteur'

    def __str__(self):
        return f"{self.nom} {self.prenom}"

class Livre(models.Model):
    isbn13 = models.CharField(max_length=13, primary_key=True)
    titre = models.CharField(max_length=255)
    type = models.CharField(max_length=50)
    genre_litteraire = models.CharField(max_length=100)
    sous_genre = models.CharField(max_length=100)
    illustrateur = models.CharField(max_length=100, blank=True, null=True)
    langue = models.CharField(max_length=50)
    format = models.CharField(max_length=50)
    nombre_pages = models.IntegerField()
    dimensions = models.CharField(max_length=50)
    date_parution = models.DateField()
    localisation = models.CharField(max_length=100)
    synopsis = models.TextField()
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    url_reference = models.URLField(blank=True, null=True)
    traducteur = models.CharField(max_length=100, blank=True, null=True)
    quantite_disponible = models.IntegerField()
    quantite_totale = models.IntegerField()
    quantite_minimale = models.IntegerField()
    editeur = models.ForeignKey(Editeur, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Livre'

    def __str__(self):
        return self.titre

class Ecrire(models.Model):
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE)
    auteur = models.ForeignKey(Auteur, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Ecrire'

    def __str__(self):
        return f"{self.auteur.nom} a écrit {self.livre.titre}"

class Commander(models.Model):
    personne = models.ForeignKey(Personne, on_delete=models.CASCADE)
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE)
    date_commande = models.DateField()
    quantite = models.IntegerField()
    statut = models.CharField(max_length=50)

    class Meta:
        db_table = 'Commander'

    def __str__(self):
        return f"Commande de {self.quantite} exemplaire(s) de {self.livre.titre} par {self.personne.nom}"

class Notifier(models.Model):
    personne = models.ForeignKey(Personne, on_delete=models.CASCADE)
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE)
    quantite = models.IntegerField()
    type = models.CharField(max_length=50)
    commentaire = models.TextField()

    class Meta:
        db_table = 'Notifier'

    def __str__(self):
        return f"Notification de {self.personne.nom} pour {self.livre.titre}"

class Achat(models.Model):
    personne = models.ForeignKey(Personne, on_delete=models.CASCADE)
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE)
    quantite = models.IntegerField()
    date_achat = models.DateField()

    class Meta:
        db_table = 'Achat'

    def __str__(self):
        return f"Achat de {self.quantite} exemplaire(s) de {self.livre.titre} par {self.personne.nom}"

class Reserver(models.Model):
    personne = models.ForeignKey(Personne, on_delete=models.CASCADE)
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE)
    quantite = models.IntegerField()
    statut = models.CharField(max_length=50)
    date_reservation = models.DateField()

    class Meta:
        db_table = 'Reserver'

    def __str__(self):
        return f"Réservation de {self.quantite} exemplaire(s) de {self.livre.titre} par {self.personne.nom}"

