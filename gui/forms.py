# forms.py
from django import forms
from .models import Personne, Livre, Auteur, Ecrire, Editeur

class PersonneForm(forms.ModelForm):
    class Meta:
        model = Personne
        fields = ['nom', 'prenom', 'date_naissance', 'telephone', 'email', 'password', 'solde', 'adresse', 'role']

class AuteurForm(forms.ModelForm):
    class Meta:
        model = Auteur
        fields = ['nom','prenom','date_naissance']

class LivreForm(forms.ModelForm):
    editeur_nom = forms.CharField(max_length=255, required=False, label="Nom de l'éditeur")
    auteur_form = AuteurForm()
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

        livre.save()

        auteur_form = self.cleaned_data.get('auteur_form')
        if auteur_form and auteur_form.is_valid():
            auteur = auteur_form.save(commit=False)  # Créer ou récupérer l'auteur
            auteur.save()  # Sauvegarder l'auteur
            # Associer l'auteur au livre via la table 'Ecrire'
            Ecrire.objects.create(livre=livre, auteur=auteur)

        return livre

class ISBNForm(forms.Form):
    isbn13 = forms.CharField(label='ISBN13 du livre', max_length=13)

