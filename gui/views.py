from django.http import  HttpResponseRedirect
from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse_lazy,reverse
from django.views.generic import CreateView, DeleteView, UpdateView, ListView
from gui.models import Ville, Adresse, Role, Personne, Fournisseur, Editeur, Auteur, Livre, Ecrire, Commander, Notifier, Achat, Reserver
from .forms import PersonneForm, AdresseForm, LivreForm, ISBNForm, AuteurForm, VilleForm, EditeurForm
""" NotificationForm"""
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, View
from django.contrib.auth.forms import UserCreationForm


"""########################################################"""
def registerPage(request):
    form = UserCreationForm

    if request.method == 'POST':
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            form.save()
    context = {'form': form}
    return render(request, 'gui/register.html', context)

def loginPage(request):
    context = {}
    return render(request, 'gui/login.html', context)

"""########################################################"""

def home(request):
    return render(request, 'gui/homepage.html')

"""########################################################"""

# 3. Classe Role
class RoleList(ListView):
    model = Role
    template_name = 'gui/lister_roles.html'

class RoleCreate(CreateView):
    model = Role
    fields = ['type']
    template_name = 'gui/ajouter_role.html'
    success_url = reverse_lazy('roles_list')


"""########################################################"""

class VilleList(ListView):
    model = Ville
    template_name = 'gui/lister_villes.html'

class VilleCreate(CreateView):
    model = Ville
    fields = ['nom', 'code_postal', 'pays']
    template_name = 'gui/ajouter_ville.html'
    success_url = reverse_lazy('villes_list')


class AdresseList(ListView):
    model = Adresse
    template_name = 'gui/lister_adresses.html'

class AdresseCreate(CreateView):
    model = Adresse
    fields = ['rue', 'n_rue', 'ville']
    template_name = 'gui/ajouter_adresse.html'
    success_url = reverse_lazy('adresses_list')

def adresse_create(request):
    if request.method == 'POST':
        form = AdresseForm(request.POST)
        if form.is_valid():
            adresse = form.save()
            # Rediriger vers une vue de confirmation ou vers la création de la personne
            return redirect('personne_create')  # Redirection vers la création de personne
    else:
        form = AdresseForm()

    return render(request, 'gui/ajouter_adresse.html', {'form': form})

"""########################################################"""

class PersonneList(ListView):
    model = Personne
    template_name = 'gui/lister_personnes.html'

def personne_create(request):
    # Initialiser les formulaires
    form_personne = PersonneForm()
    form_adresse = AdresseForm()
    form_ville = VilleForm()

    if request.method == 'POST':
        form_personne = PersonneForm(request.POST)
        form_adresse = AdresseForm(request.POST)
        form_ville = VilleForm(request.POST)

        if form_personne.is_valid() and form_adresse.is_valid() and form_ville.is_valid():
            # Récupérer les champs de la ville depuis le formulaire VilleForm
            nom_ville = form_ville.cleaned_data['nom_ville']
            code_postal = form_ville.cleaned_data['code_postal']
            pays = form_ville.cleaned_data['pays']

            # Vérifier si la ville existe déjà
            ville_existante = Ville.objects.filter(nom=nom_ville, code_postal=code_postal).first()

            if not ville_existante:
                # Si la ville n'existe pas, créer une nouvelle ville
                ville = form_ville.save()
            else:
                # Utiliser la ville existante
                ville = ville_existante

            # Récupérer les champs de l'adresse depuis le formulaire AdresseForm
            rue = form_adresse.cleaned_data['rue']
            n_rue = form_adresse.cleaned_data['n_rue']


            # Vérifier si l'adresse existe déjà
            adresse_existante = Adresse.objects.filter(rue=rue, n_rue=n_rue, ville=ville).first()

            if adresse_existante:
                # Si l'adresse existe déjà, l'utiliser
                adresse = adresse_existante
            else:
                # Sinon, créer une nouvelle adresse
                adresse = form_adresse.save()

            role = form_personne.cleaned_data.get('role')
            email = form_personne.cleaned_data['email']
            password = form_personne.cleaned_data['password']

            # Vérifier si l'email existe déjà
            if Personne.objects.filter(email=email).exists():
                form_personne.add_error('email', 'Cet email est déjà utilisé.')
                return render(request, 'gui/ajouter_personne.html', {
                    'form': form_personne,
                    'form_adresse': form_adresse,
                    'form_ville': form_ville
                })

            # Créer l'utilisateur en fonction du rôle
            nom = form_personne.cleaned_data['nom']
            prenom = form_personne.cleaned_data['prenom']
            date_naissance = form_personne.cleaned_data['date_naissance']
            telephone = form_personne.cleaned_data['telephone']
            solde = form_personne.cleaned_data['solde']



            # Créer l'utilisateur
            if str(role) == 'admin':
                personne = Personne.objects.create_superuser(
                    email=email,
                    password=password,
                    nom=nom,
                    prenom=prenom,
                    date_naissance=date_naissance,
                    telephone=telephone,
                    adresse=adresse,
                    solde=solde,
                    role=role
                )
            elif str(role) == "employe":
                personne = Personne.objects.create_user(
                    email=email,
                    password=password,
                    nom=nom,
                    prenom=prenom,
                    date_naissance=date_naissance,
                    telephone=telephone,
                    adresse=adresse,
                    solde=solde,
                    role=role,
                    is_staff=True
                )
            else:
                personne = Personne.objects.create_user(
                    email=email,
                    password=password,
                    nom=nom,
                    prenom=prenom,
                    date_naissance=date_naissance,
                    telephone=telephone,
                    adresse=adresse,
                    solde=solde,
                    role=role
                )

            # Une fois l'utilisateur créé, rediriger vers la liste des personnes
            return redirect('personnes_list')  # Redirection vers une autre vue

    else:
        form_personne = PersonneForm()
        form_adresse = AdresseForm()
        form_ville = VilleForm()

    return render(request, 'gui/ajouter_personne.html',  {
        'form_personne': form_personne,
        'form_adresse': form_adresse,
        'form_ville': form_ville
    })

"""########################################################"""

# 5. Classe Fournisseur
class FournisseurList(ListView):
    model = Fournisseur
    template_name = 'gui/lister_fournisseurs.html'

class FournisseurCreate(CreateView):
    model = Fournisseur
    fields = ['nom']
    template_name = 'gui/ajouter_fournisseur.html'
    success_url = reverse_lazy('fournisseurs_list')

"""########################################################"""

class EditeurList(ListView):
    model = Editeur
    template_name = 'gui/lister_editeurs.html'

class EditeurCreate(CreateView):
    model = Editeur
    fields = ['nom']
    template_name = 'gui/ajouter_editeur.html'
    success_url = reverse_lazy('editeurs_list')

class EditeurUpdate(View):
    template_name = 'gui/modifier_editeurs.html'

    def get(self, request, nom):
        editeur = get_object_or_404(Editeur, nom=nom)
        form = EditeurForm(instance=editeur)
        return render(request, self.template_name, {'form': form, 'editeur': editeur})

    def post(self, request, nom):
        editeur = get_object_or_404(Editeur, nom=nom)
        form = EditeurForm(request.POST, instance=editeur)

        if form.is_valid():
            form.save()
            return redirect('editeurs_list')  # Rediriger vers la liste des livres après modification

        return render(request, self.template_name, {'form': form, 'editeur': editeur})

class EditeurDelete(View):
    template_name = 'gui/supprimer_editeur.html'

    def get(self, request):
        # Afficher le formulaire où l'utilisateur entre l'ID du livre
        return render(request, self.template_name)

    def post(self, request):
        # Récupérer l'ID du livre soumis dans le formulaire
        editeur_nom = request.POST.get('editeur_nom')
        if editeur_nom:
            # Obtenir l'objet Livre avec l'ID fourni
            editeur = get_object_or_404(Editeur, pk=editeur_nom)
            # Supprimer le livre
            editeur.delete()
            # Rediriger vers la liste des livres après la suppression
            return redirect(reverse_lazy('editeurs_list'))
        return render(request, self.template_name, {'error': "Nom de l'éditeur invalide."})

def saisir_nom_editeur(request):
    if request.method == 'POST':
        form = EditeurForm(request.POST)
        if form.is_valid():
            editeur_nom = form.cleaned_data['nom']
            # Vérifier si le livre existe
            if Editeur.objects.filter(nom=editeur_nom).exists():
                return redirect(reverse('editeurs_update', kwargs={'nom': editeur_nom}))
            else:
                # Si le livre n'existe pas, afficher un message d'erreur
                return render(request, 'gui/saisir_editeur_nom.html', {'form': form, 'error': 'Editeur non trouvé.'})
    else:
        form = EditeurForm()
    return render(request, 'gui/saisir_editeur_nom.html', {'form': form})

"""########################################################"""

class AuteurList(ListView):
    model = Auteur
    template_name = 'gui/lister_auteurs.html'

class AuteurCreate(CreateView):
    model = Auteur
    fields = ['nom', 'prenom', 'date_naissance']
    template_name = 'gui/ajouter_auteur.html'
    success_url = reverse_lazy('auteurs_list')

"""########################################################"""

class LivreList(ListView):
    model = Livre
    template_name = 'gui/lister_livres.html'


def create_livre(request):
    if request.method == 'POST':
        livre_form = LivreForm(request.POST)
        auteur_form = AuteurForm(request.POST)

        if livre_form.is_valid() and auteur_form.is_valid():
            # Sauvegarder l'auteur en premier
            auteur = auteur_form.save()

            # Sauvegarder le livre et associer l'éditeur
            livre = livre_form.save(commit=False)
            livre.save()

            # Créer la relation entre le livre et l'auteur dans 'Ecrire'
            Ecrire.objects.create(livre=livre, auteur=auteur)

            return redirect('livres_list')  # Redirige vers une page de succès
    else:
        livre_form = LivreForm()
        auteur_form = AuteurForm()

    return render(request, 'gui/ajouter_livre.html', {
        'livre_form': livre_form,
        'auteur_form': auteur_form,
    })

class LivreDelete(View):
    template_name = 'gui/supprimer_livre.html'

    def get(self, request):
        # Afficher le formulaire où l'utilisateur entre l'ID du livre
        return render(request, self.template_name)

    def post(self, request):
        # Récupérer l'ID du livre soumis dans le formulaire
        livre_id = request.POST.get('livre_id')
        if livre_id:
            # Obtenir l'objet Livre avec l'ID fourni
            livre = get_object_or_404(Livre, pk=livre_id)
            # Supprimer le livre
            livre.delete()
            # Rediriger vers la liste des livres après la suppression
            return redirect(reverse_lazy('livres_list'))
        return render(request, self.template_name, {'error': 'ID du livre invalide.'})

class LivreUpdate(View):
    template_name = 'gui/modifier_livres.html'

    def get(self, request, isbn13):
        livre = get_object_or_404(Livre, isbn13=isbn13)
        form = LivreForm(instance=livre)
        return render(request, self.template_name, {'form': form, 'livre': livre})

    def post(self, request, isbn13):
        livre = get_object_or_404(Livre, isbn13=isbn13)
        form = LivreForm(request.POST, instance=livre)

        if form.is_valid():
            form.save()
            return redirect('livres_list')  # Rediriger vers la liste des livres après modification

        return render(request, self.template_name, {'form': form, 'livre': livre})

class LivreResearch(ListView):
    model = Livre
    template_name = 'gui/lister_livres.html'
    def get_queryset(self):
        search_query = self.request.GET.get('search', '')
        if search_query:
            return Livre.objects.filter(titre__icontains=search_query)
        return Livre.objects.all()

def saisir_isbn(request):
    if request.method == 'POST':
        form = ISBNForm(request.POST)
        if form.is_valid():
            isbn13 = form.cleaned_data['isbn13']
            # Vérifier si le livre existe
            if Livre.objects.filter(isbn13=isbn13).exists():
                return redirect(reverse('livre_update', kwargs={'isbn13': isbn13}))
            else:
                # Si le livre n'existe pas, afficher un message d'erreur
                return render(request, 'gui/saisir_isbn.html', {'form': form, 'error': 'Livre non trouvé.'})
    else:
        form = ISBNForm()
    return render(request, 'gui/saisir_isbn.html', {'form': form})

"""########################################################"""

class EcrireList(ListView):
    model = Ecrire
    template_name = 'gui/lister_ecrits.html'

class EcrireCreate(CreateView):
    model = Ecrire
    fields = ['livre', 'auteur']
    template_name = 'gui/ajouter_ecrire.html'
    success_url = reverse_lazy('ecrits_list')

"""########################################################"""

class CommanderList(ListView):
    model = Commander
    template_name = 'gui/lister_commandes.html'

class CommanderCreate(CreateView):
    model = Commander
    fields =['personne', 'livre', 'quantite', 'date_commande', 'quantite', 'statut']
    template_name = 'gui/ajouter_commande.html'
    success_url = reverse_lazy('commandes_list')

"""########################################################"""

# 13. Classe Reserver
class ReserverList(ListView):
    model = Reserver
    template_name = 'gui/lister_reservations.html'

class ReserverCreate(CreateView):
    model = Reserver
    fields = ['personne', 'livre', 'quantite', 'statut', 'date_reservation']
    template_name = 'gui/ajouter_reservation.html'
    success_url = reverse_lazy('reservations_list')

"""########################################################"""
class AchatList(ListView):
    model = Achat
    template_name = 'gui/lister_achats.html'

class AchatCreate(CreateView):
    model = Achat
    fields = ['personne', 'livre', 'quantite', 'date_achat']
    template_name = 'gui/ajouter_achat.html'
    success_url = reverse_lazy('achats_list')

"""########################################################"""

class NotifierList(ListView):
    model = Notifier
    template_name = 'gui/lister_notifications.html'

class NotifierCreate(CreateView):
    model = Notifier
    fields = ['personne', 'livre', 'quantite', 'type', 'commentaire']
    template_name = 'gui/ajouter_notification.html'
    success_url = reverse_lazy('notifications_list')







