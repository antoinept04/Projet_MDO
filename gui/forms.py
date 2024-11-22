# forms.py
from django import forms
from .models import Personne, Livre, Auteur, Editeur, Adresse, Commander, Ville, Notifier, Illustrateur, Traducteur, Reserver


class VilleForm(forms.ModelForm):
    class Meta:
        model = Ville
        fields = ['nom_ville', 'code_postal', 'pays']

class AdresseForm(forms.ModelForm):
    class Meta:
        model = Adresse
        fields = ['rue', 'n_rue']

class PersonneForm(forms.ModelForm):
    class Meta:
        model = Personne
        fields = ['nom', 'prenom', 'date_naissance', 'telephone', 'email', 'password', 'solde', 'role']
        labels = {
            'nom': 'Nom',
            'prenom': 'Prénom',
            'date_naissance': 'Date de naissance',
            'telephone': 'Téléphone',
            'email': 'Email',
            'password': 'Mot de passe',
            'solde': 'Solde',
            'role': 'Rôle'
        }
        widgets = {
            'date_naissance': forms.DateInput(
                attrs={
                    'placeholder': 'JJ/MM/AAAA',
                    'type': 'date'
                }),
        }

    def __init__(self, *args, **kwargs):
        # Extraire l'utilisateur passé via les kwargs
        self.user = kwargs.pop('user', None)
        super(PersonneForm, self).__init__(*args, **kwargs)

        # Si l'utilisateur n'est pas un superutilisateur, retirer le champ 'role'
        if self.user and not self.user.is_superuser:
            self.fields.pop('role', None)

class LivreForm(forms.ModelForm):
    editeur_nom = forms.CharField(max_length=255, required=False, label="Nom de l'éditeur")
    class Meta:
        model = Livre
        fields = ['isbn13', 'titre', 'type', 'genre_litteraire', 'sous_genre', 'langue',
                  'format', 'nombre_pages', 'dimensions', 'date_parution', 'localisation', 'synopsis',
                  'prix', 'url_reference', 'quantite_disponible', 'quantite_totale',
                  'quantite_minimale', 'editeur_nom']
        labels = {
            'isbn13' : "ISBN13",
            'titre' : "Titre",
            'type' : "Type (roman, BD, manga, comics)",
            'genre_litteraire' : "Genre littéraire",
            'sous_genre' : "Sous-genre littéraire",
            'langue' : "Langue",
            'format' : "Format",
            'nombre_pages' : "Nombre de pages",
            'dimensions' : "Dimensions",
            'date_parution' : "Date de parution",
            'localisation' : "Localisation dans le magasin",
            'synopsis' : "Synopsis",
            'prix' : "Prix",
            'url_reference' : "URL de reference",
            'quantite_disponible' : "Quantité disponible",
            'quantite_totale' : "Quantité totale",
            'quantite_minimale' : "Quantité minimale",
            'editeur_nom' : "Nom de l'editeur"
        }
        widgets ={
            'date_parution' : forms.DateInput(
                attrs={
                    'placeholder': 'JJ/MM/AAAA',
                    'type' : 'date'
                    }),
        }

    def save(self, commit=True):
        # Sauvegarde du livre
        livre = super().save(commit=False)

        # Gestion de l'éditeur
        editeur_nom = self.cleaned_data['editeur_nom']
        if editeur_nom:  # Création de l'éditeur si nécessaire
            editeur, created = Editeur.objects.get_or_create(nom=editeur_nom)
            livre.editeur = editeur

        if commit:
            livre.save()

        return livre
class ISBNForm(forms.Form):
    isbn13 = forms.CharField(label='ISBN13 du livre', max_length=13)

class AuteurForm(forms.ModelForm):
    class Meta:
        model = Auteur
        fields = ['nom','prenom','date_naissance']
        labels = {
            'nom' : "Nom de l'auteur",
            'prenom' : "Prenom de l'auteur",
            'date_naissance' : "Date de naissance"
        }
        widgets = {
            'date_naissance': forms.DateInput(
                attrs={
                    'placeholder': 'JJ/MM/AAAA',
                    'type': 'date',
                }),
        }
class IDAuteurForm(forms.Form):
    auteur_id = forms.IntegerField(label="ID d'auteur")

class EditeurForm(forms.ModelForm):
    class Meta:
        model = Editeur
        fields = ['nom']
class IDEditeurForm(forms.Form):
    id = forms.IntegerField(label="ID de l'éditeur")

class IllustrateurForm(forms.ModelForm):
    class Meta:
        model = Illustrateur  # Remplacez par le nom correct du modèle si ce n'est pas "Illustrateur"
        fields = ['nom', 'prenom', 'date_naissance']
        labels = {
            'nom': "Nom de l'illustrateur",
            'prenom': "Prénom de l'illustrateur",
            'date_naissance': "Date de naissance",
        }
        widgets = {
            'date_naissance': forms.DateInput(
                attrs={
                    'placeholder': 'JJ/MM/AAAA',
                    'type': 'date',
                }),
        }
class IDIllustrateurForm(forms.Form):
    illustrateur_id = forms.IntegerField(label="ID d'illustrateur")

class TraducteurForm(forms.ModelForm):
    class Meta:
        model = Traducteur  # Remplacez par le nom correct du modèle si ce n'est pas "Traducteur"
        fields = ['nom', 'prenom', 'date_naissance']
        labels = {
            'nom': "Nom du traducteur",
            'prenom': "Prénom du traducteur",
            'date_naissance': "Date de naissance",
        }
        widgets = {
            'date_naissance': forms.DateInput(
                attrs={
                    'placeholder': 'JJ/MM/AAAA',
                    'type': 'date',
                }),
        }
class IDTraducteurForm(forms.Form):
    traducteur_id = forms.IntegerField(label="ID du traducteur")

class CommanderForm(forms.ModelForm):
    class Meta:
        model = Commander
        fields = ['personne', 'livre', 'date_commande', 'quantite', 'fournisseur', 'statut']  # Ajout du fournisseur 'fournisseur',
        widgets = {
            'date_commande': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer les personnes ayant le rôle "Employé" ou "Admin"
        self.fields['personne'].queryset = Personne.objects.filter(
            role__type__in=['employé', 'admin']  # Filtrage par 'role__type'
        )
        # Ajouter un queryset pour le champ fournisseur (si nécessaire)
        #self.fields['fournisseur'].queryset = Fournisseur.objects.all()  # Toutes les valeurs de Fournisseur

class ReserverForm(forms.ModelForm):
    class Meta:
        model = Reserver
        fields = ['personne', 'livre', 'quantite', 'statut', 'date_reservation']

        widgets = {
            'date_reservation': forms.DateInput(attrs={'type': 'date'}),
            'quantite': forms.NumberInput(attrs={'min': 1}),
        }

    def __init__(self, *args, **kwargs):
        super(ReserverForm, self).__init__(*args, **kwargs)
        # Filtrer les personnes ayant le rôle "client"
        self.fields['personne'].queryset = Personne.objects.filter(role__type='Client')

        # Ajoutez des labels personnalisés si nécessaire
        self.fields['personne'].label = "Personne"
        self.fields['livre'].label = "Livre"
        self.fields['quantite'].label = "Quantité"
        self.fields['statut'].label = "Statut"
        self.fields['date_reservation'].label = "Date de réservation"