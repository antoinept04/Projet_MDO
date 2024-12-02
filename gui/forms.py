# forms.py
from django import forms
from .models import Personne, Livre, Auteur, Editeur, Adresse, Commander, Ville, Notifier, Illustrateur, Traducteur, \
    Reserver, Fournisseur, Achat, FournisseurAdresse
from django.forms import modelformset_factory, inlineformset_factory

class EmailInputForm(forms.Form):
    email = forms.EmailField(
        label='Email de la personne à modifier',
        max_length=50,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez l\'email ici'
        })
    )

class VilleForm(forms.ModelForm):
    class Meta:
        model = Ville
        fields = ['nom_ville', 'code_postal', 'pays']
        labels = {
            'nom_ville': 'Ville',
            'code_postal': 'Code Postal',
            'pays': 'Pays'
        }

    def clean(self):
        cleaned_data = super().clean()
        nom_ville = cleaned_data.get('nom_ville')
        code_postal = cleaned_data.get('code_postal')
        pays = cleaned_data.get('pays')

        try:
            ville = Ville.objects.get(nom_ville=nom_ville, code_postal=code_postal, pays=pays)
            self.instance = ville  # Utiliser l'instance existante
        except Ville.DoesNotExist:
            pass  # La ville n'existe pas, le formulaire créera une nouvelle ville

        return cleaned_data

class AdresseForm(forms.ModelForm):
    class Meta:
        model = Adresse
        fields = ['rue', 'n_rue']
        labels = {
            'rue': 'Rue',
            'n_rue': 'Numéro',
        }

AdresseFormSet = modelformset_factory(
    Adresse,
    form=AdresseForm,
    extra=1,
    can_delete=True
) #formset pour la création de fournisseurs

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
            'password': 'Mot de passe (sauf pour un client)',
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
class IDCommandeForm(forms.Form):
    commande_id = forms.IntegerField(label="ID de la commande")

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
        self.fields['personne'].queryset = Personne.objects.filter(role__type='client')

        # Ajoutez des labels personnalisés si nécessaire
        self.fields['personne'].label = "Personne"
        self.fields['livre'].label = "Livre"
        self.fields['quantite'].label = "Quantité"
        self.fields['statut'].label = "Statut"
        self.fields['date_reservation'].label = "Date de réservation"
class IDReservationForm(forms.Form):
    reservation_id = forms.IntegerField(label="ID de la reservation")

class FournisseurForm(forms.ModelForm):
    class Meta:
        model = Fournisseur
        fields = ['nom_fournisseur']  # 'adresses' n'est plus inclus


class IDFournisseurForm(forms.Form):
    nom_fournisseur = forms.CharField(label="Nom du Fournisseur", max_length=100)

class FournisseurAdresseForm(forms.ModelForm):
    class Meta:
        model = FournisseurAdresse
        fields = ['adresse']

# Formset pour gérer plusieurs adresses
FournisseurAdresseFormSet = inlineformset_factory(
    Fournisseur,
    FournisseurAdresse,
    form=FournisseurAdresseForm,
    extra=1,
    can_delete=True
)

class AchatForm(forms.ModelForm):
    class Meta:
        model = Achat
        fields = ['personne', 'livre', 'date_achat', 'quantite']
        widgets = {
            'date_achat': forms.DateInput(attrs={'type': 'date'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer les personnes ayant le rôle "client"
        self.fields['personne'].queryset = Personne.objects.filter(
            role__type__in=['client']  # Filtrage par 'role__type'
        )
class IDAchatForm(forms.Form):
    achat_id = forms.IntegerField(label="ID de l'achat'")