from django import forms
from django.forms import modelformset_factory, inlineformset_factory

from .models import Ville, Adresse, Personne, Fournisseur, FournisseurAdresse, Editeur, Contributeur, Livre, \
    Achat, Commander, Reserver


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
            self.instance = ville
        except Ville.DoesNotExist:
            pass

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
)
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

        self.user = kwargs.pop('user', None)
        super(PersonneForm, self).__init__(*args, **kwargs)


        if self.user and not self.user.is_superuser:
            self.fields.pop('role', None)
class ContributeurForm(forms.ModelForm):
    class Meta:
        model = Contributeur
        fields = ['type', 'nom', 'prenom', 'date_naissance']
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
        }
class IDContributeurForm(forms.Form):
    contributeur_id = forms.IntegerField(label="ID du contributeur")
class LivreForm(forms.ModelForm):
    editeur_nom = forms.CharField(max_length=255, required=False, label="Nom de l'éditeur")

    class Meta:
        model = Livre
        fields = [
            'isbn13', 'titre', 'type', 'genre_litteraire', 'sous_genre', 'langue',
            'format', 'nombre_pages', 'dimensions', 'date_parution', 'localisation', 'synopsis',
            'prix', 'url_reference', 'quantite_disponible', 'quantite_minimale', 'editeur_nom'
        ]
        widgets = {
            'date_parution': forms.DateInput(attrs={'type': 'date'}),
        }

    def save(self, commit=True):
        livre = super().save(commit=False)
        editeur_nom = self.cleaned_data['editeur_nom']
        if editeur_nom:
            editeur, created = Editeur.objects.get_or_create(nom=editeur_nom)
            livre.editeur = editeur
        if commit:
            livre.save()
        return livre
class ISBNForm(forms.Form):
    isbn13 = forms.CharField(label='ISBN13 du livre', max_length=13)
class EditeurForm(forms.ModelForm):
    class Meta:
        model = Editeur
        fields = ['nom']
class IDEditeurForm(forms.Form):
    id = forms.IntegerField(label="ID de l'éditeur")
class CommanderForm(forms.ModelForm):
    class Meta:
        model = Commander
        fields = ['personne', 'date_commande', 'fournisseur', 'statut']
        widgets = {
            'date_commande': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['personne'].queryset = Personne.objects.filter(
            role__type__in=['employé', 'admin']
        )

class CommanderUpdateForm(forms.ModelForm):
    class Meta:
        model = Commander
        fields = ['personne', 'livre', 'date_commande', 'quantite', 'fournisseur', 'statut']
        widgets = {
            'date_commande': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['personne'].queryset = Personne.objects.filter(
            role__type__in=['employé', 'admin']
        )


class IDCommandeForm(forms.Form):
    commande_id = forms.IntegerField(label="ID de la commande")
class ReserverForm(forms.ModelForm):
    class Meta:
        model = Reserver
        fields = ['personne', 'statut', 'date_reservation']

        widgets = {
            'date_reservation': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['personne'].queryset = Personne.objects.filter(role__type='client')

class ReserverUpdateForm(forms.ModelForm):
    class Meta:
        model = Reserver
        fields = ['personne', 'livre', 'quantite', 'statut', 'date_reservation']

        widgets = {
            'date_reservation': forms.DateInput(attrs={'type': 'date'}),
            'quantite': forms.NumberInput(attrs={'min': 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['personne'].queryset = Personne.objects.filter(role__type='client')

class IDReservationForm(forms.Form):
    reservation_id = forms.IntegerField(label="ID de la reservation")
class FournisseurForm(forms.ModelForm):
    class Meta:
        model = Fournisseur
        fields = ['nom_fournisseur']
class IDFournisseurForm(forms.Form):
    nom_fournisseur = forms.CharField(label="Nom du Fournisseur", max_length=100)
class FournisseurAdresseForm(forms.ModelForm):
    class Meta:
        model = FournisseurAdresse
        fields = ['adresse']


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
        fields = ['personne', 'date_achat']
        widgets = {
            'date_achat': forms.DateInput(attrs={'type': 'date'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['personne'].queryset = Personne.objects.filter(
            role__type__in=['client']
        )
class IDAchatForm(forms.Form):
    achat_id = forms.IntegerField(label="ID de l'achat'")

class AchatUpdateForm(forms.ModelForm):
    class Meta:
        model = Achat
        fields = ['personne', 'date_achat', 'livre', 'quantite']
        widgets = {
            'date_achat': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['personne'].queryset = Personne.objects.filter(role__type='client')