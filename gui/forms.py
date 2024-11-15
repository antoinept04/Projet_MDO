# forms.py
from django import forms
from .models import Personne, Livre, Auteur, Editeur, Adresse, Commander, Ville, Notifier

"""-------------------AJOUTER-PERSONNE--------------------"""

class VilleForm(forms.ModelForm):
    class Meta:
        model = Ville
        fields = ['nom_ville', 'code_postal', 'pays']

class PersonneForm(forms.ModelForm):
    class Meta:
        model = Personne

        fields = ['nom', 'prenom', 'date_naissance', 'telephone', 'email', 'password', 'solde', 'role']

    def __init__(self, *args, **kwargs):
        # Extraire l'utilisateur passé via les kwargs
        self.user = kwargs.pop('user', None)
        super(PersonneForm, self).__init__(*args, **kwargs)

        # Si l'utilisateur n'est pas un superutilisateur, retirer le champ 'role'
        if self.user and not self.user.is_superuser:
            self.fields.pop('role', None)

class AdresseForm(forms.ModelForm):
    class Meta:
        model = Adresse
        fields = ['rue', 'n_rue']

"""########################################################"""

"""
class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notifier
        fields = ['personne', 'livre', 'quantite', 'type', 'commentaire', 'termine']"""

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
                    'type': 'date'
                }),
        }


class LivreForm(forms.ModelForm):
    editeur_nom = forms.CharField(max_length=255, required=False, label="Nom de l'éditeur")
    class Meta:
        model = Livre
        fields = ['isbn13', 'titre', 'type', 'genre_litteraire', 'sous_genre', 'illustrateur', 'langue',
                  'format', 'nombre_pages', 'dimensions', 'date_parution', 'localisation', 'synopsis',
                  'prix', 'url_reference', 'traducteur', 'quantite_disponible', 'quantite_totale',
                  'quantite_minimale', 'editeur_nom']
        labels = {
            'isbn13' : "ISBN13",
            'titre' : "Titre",
            'type' : "Type (roman, BD, manga, comics)",
            'genre_litteraire' : "Genre littéraire",
            'sous_genre' : "Sous-genre littéraire",
            'illustrateur' : "Illustrateur",
            'langue' : "Langue",
            'format' : "Format",
            'nombre_pages' : "Nombre de pages",
            'dimensions' : "Dimensions",
            'date_parution' : "Date de parution",
            'localisation' : "Localisation dans le magasin",
            'synopsis' : "Synopsis",
            'prix' : "Prix",
            'url_reference' : "URL de reference",
            'traducteur' : "Traducteur",
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

class NomEditeurForm(forms.Form):
    nom = forms.CharField(label="Nom de l'éditeur", max_length=255)

class IDAuteurForm(forms.Form):
    auteur_id = forms.IntegerField(label="ID d'auteur")

class EditeurForm(forms.ModelForm):
    class Meta:
        model = Editeur
        fields = ['nom']