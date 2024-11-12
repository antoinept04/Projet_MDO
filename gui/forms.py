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

class LivreForm(forms.ModelForm):
    editeur_nom = forms.CharField(max_length=255, required=False, label="Nom de l'éditeur")
    class Meta:
        model = Livre
        fields = ['isbn13', 'titre', 'type', 'genre_litteraire', 'sous_genre', 'illustrateur', 'langue',
                  'format', 'nombre_pages', 'dimensions', 'date_parution', 'localisation', 'synopsis',
                  'prix', 'url_reference', 'traducteur', 'quantite_disponible', 'quantite_totale',
                  'quantite_minimale', 'editeur_nom']

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