from django.contrib.auth.decorators import login_required
from django.http import  HttpResponseRedirect
from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse_lazy,reverse
from django.views.generic import CreateView, DeleteView, UpdateView, ListView
from gui.models import Ville, Adresse, Role, Personne, Fournisseur, Editeur, Auteur, Livre, Ecrire, Commander, Notifier, Achat, Reserver
from .decorators import unauthenticated_user_required
from .forms import PersonneForm, AdresseForm, LivreForm, ISBNForm, AuteurForm, VilleForm, EditeurForm, NomEditeurForm, IDAuteurForm

""" NotificationForm"""
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, View
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q, Prefetch
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

"""########################################################"""

@unauthenticated_user_required
def loginPage(request):

    if request.method == 'POST':

        user = authenticate(request, email=request.POST.get('email'), password=request.POST.get('password'))

        if user is not None:
            login(request, user)
            return redirect('homepage')
        else:
            messages.info(request, "L'email ou le mot de passe est incorrect")


    context = {}
    return render(request, 'gui/login.html', context)

@login_required(login_url='login')
def logoutUser(request):
    logout(request)

    return redirect('login')

"""########################################################"""
@login_required(login_url='login')
def home(request):
    return render(request, 'gui/homepage.html')

"""########################################################"""
#Super classe définissant les permissions

class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = 'login'  # URL de redirection si l'utilisateur n'est pas connecté

    def test_func(self):
        # Vérifie que l'utilisateur a le statut is_staff
        return self.request.user.is_staff


# 3. Classe Role

class RoleList(StaffRequiredMixin,ListView):
    model = Role
    template_name = 'gui/lister_roles.html'



class RoleCreate(StaffRequiredMixin,CreateView):
    model = Role
    fields = ['type']
    template_name = 'gui/ajouter_role.html'
    success_url = reverse_lazy('roles_list')



"""########################################################"""

class VilleList(StaffRequiredMixin,ListView):
    model = Ville
    template_name = 'gui/lister_villes.html'



class VilleCreate(StaffRequiredMixin,CreateView):
    model = Ville
    fields = ['nom', 'code_postal', 'pays']
    template_name = 'gui/ajouter_ville.html'
    success_url = reverse_lazy('villes_list')

def ville_create(request):
    if request.method == 'POST':

        form_ville = VilleForm(request.POST)

        if form_ville.is_valid():
            nom_ville = form_ville.cleaned_data['nom_ville']
            code_postal = form_ville.cleaned_data['code_postal']
            pays = form_ville.cleaned_data['pays']

            # Vérifier si la ville existe déjà
            ville_existante = Ville.objects.filter(nom_ville=nom_ville, code_postal=code_postal).first()

            if not ville_existante:
                # Si la ville n'existe pas, créer une nouvelle ville
                ville = form_ville.save()
            else:
                # Utiliser la ville existante
                ville = ville_existante
            return redirect('villes_list')  # Assurez-vous que l'URL existe

    else:
        form_ville = VilleForm()



    return render(request, 'gui/ajouter_ville.html', {
        'form_ville': form_ville
    })
class AdresseList(StaffRequiredMixin,ListView):
    model = Adresse
    template_name = 'gui/lister_adresses.html'


class AdresseCreate(StaffRequiredMixin,CreateView):
    model = Adresse
    fields = ['rue', 'n_rue', 'ville']
    template_name = 'gui/ajouter_adresse.html'
    success_url = reverse_lazy('adresses_list')

@login_required(login_url='login')
def adresse_create(request):
    form_adresse = AdresseForm()
    form_ville = VilleForm()

    if request.method == 'POST':
        form_ville = VilleForm(request.POST)
        form_adresse = AdresseForm(request.POST)

        if form_adresse.is_valid()and form_ville.is_valid():
            # Récupérer les champs de la ville depuis le formulaire VilleForm
            nom_ville = form_ville.cleaned_data['nom_ville']
            code_postal = form_ville.cleaned_data['code_postal']
            pays = form_ville.cleaned_data['pays']

            # Vérifier si la ville existe déjà
            ville_existante = Ville.objects.filter(nom_ville=nom_ville, code_postal=code_postal).first()

            if not ville_existante:
                # Si la ville n'existe pas, créer une nouvelle ville
                ville = form_ville.save()
            else:
                # Utiliser la ville existante
                ville = ville_existante

            # Utiliser commit=False pour différer l'enregistrement de l'adresse
            adresse = form_adresse.save(commit=False)

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
                adresse = form_adresse.save(commit=False)
                adresse.ville = ville  # Lier la ville à l'adresse
                adresse.save()
            # Une fois l'utilisateur créé, rediriger vers la liste des personnes
            return redirect('adresse_list')  # Redirection vers une autre vue

    else:
        form_adresse = AdresseForm()
        form_ville = VilleForm()

    return render(request, 'gui/ajouter_adresse.html', {
        'form_adresse': form_adresse,
        'form_ville': form_ville
    })
"""########################################################"""


class PersonneList(StaffRequiredMixin, ListView):
    model = Personne
    template_name = 'gui/lister_personnes.html'


def personne_create(request):
    # Initialiser les formulaires
    #form_personne = PersonneForm(user = request.user)
    #form_adresse = AdresseForm()
    #form_ville = VilleForm()

    if request.method == 'POST':
        form_personne = PersonneForm(request.POST, user = request.user)
        form_adresse = AdresseForm(request.POST)
        form_ville = VilleForm(request.POST)

        if form_personne.is_valid() and form_adresse.is_valid() and form_ville.is_valid():
            # Récupérer les champs de la ville depuis le formulaire VilleForm
            nom_ville = form_ville.cleaned_data['nom_ville']
            code_postal = form_ville.cleaned_data['code_postal']
            pays = form_ville.cleaned_data['pays']

            # Vérifier si la ville existe déjà
            ville_existante = Ville.objects.filter(nom_ville=nom_ville, code_postal=code_postal).first()

            if not ville_existante:
                # Si la ville n'existe pas, créer une nouvelle ville
                ville = form_ville.save()
            else:
                # Utiliser la ville existante
                ville = ville_existante

            # Utiliser commit=False pour différer l'enregistrement de l'adresse
            adresse = form_adresse.save(commit=False)

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
                adresse = form_adresse.save(commit=False)
                adresse.ville = ville  # Lier la ville à l'adresse
                adresse.save()

            if request.user.is_superuser :
                role = form_personne.cleaned_data.get('role')
            else:
                try:
                    role = Role.objects.get(type='Client')  # Récupérer l'instance Role avec le nom 'client'
                except Role.DoesNotExist:
                    # Gérer le cas où le rôle 'client' n'existe pas
                    form_personne.add_error('role', 'Le rôle "client" n\'existe pas.')
                    return render(request, 'gui/ajouter_personne.html', {
                        'form_personne': form_personne,
                        'form_adresse': form_adresse,
                        'form_ville': form_ville
                    })

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
                    password="client",
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
        form_personne = PersonneForm(user=request.user)
        form_adresse = AdresseForm()
        form_ville = VilleForm()

    return render(request, 'gui/ajouter_personne.html',  {
        'form_personne': form_personne,
        'form_adresse': form_adresse,
        'form_ville': form_ville
    })

"""########################################################"""


# 5. Classe Fournisseur
class FournisseurList(StaffRequiredMixin,ListView):
    model = Fournisseur
    template_name = 'gui/lister_fournisseurs.html'


class FournisseurCreate(StaffRequiredMixin,CreateView):
    model = Fournisseur
    fields = ['nom']
    template_name = 'gui/ajouter_fournisseur.html'
    success_url = reverse_lazy('fournisseurs_list')

"""########################################################"""


class EditeurList(ListView):
    model = Editeur
    template_name = 'gui/lister_editeurs.html'

    def get_queryset(self):
        # Récupérer les paramètres GET
        sort_by = self.request.GET.get('sort_by', 'nom')  # Par défaut : tri par 'nom'
        order = self.request.GET.get('order', 'asc')  # Par défaut : ordre ascendant

        # Définir le préfixe pour la direction du tri
        sort_prefix = '' if order == 'asc' else '-'

        # Options de tri supportées
        sorting_options = {
            'nom': 'nom'
        }

        # Récupérer le queryset initial
        queryset = super().get_queryset()

        # Appliquer le tri si valide, sinon fallback au tri par 'nom'
        if sort_by in sorting_options:
            queryset = queryset.order_by(f"{sort_prefix}{sorting_options[sort_by]}")

        return queryset



class EditeurCreate(StaffRequiredMixin,CreateView):
    model = Editeur
    fields = ['nom']
    template_name = 'gui/ajouter_editeur.html'
    success_url = reverse_lazy('editeurs_list')


class EditeurDelete(StaffRequiredMixin,View):
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


class EditeurUpdate(StaffRequiredMixin,View):
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

class EditeurResearch(StaffRequiredMixin,ListView):
    model = Editeur  # Modèle pour les éditeurs
    template_name = 'gui/lister_editeurs.html'  # Template pour afficher les résultats

    def get_queryset(self):
        search_query = self.request.GET.get('search', '')

        if search_query:
            # Rechercher le terme dans le champ nom
            return Editeur.objects.filter(nom__icontains=search_query).distinct()

        # Si aucun terme de recherche, retourner tous les éditeurs
        return Editeur.objects.all()

@login_required(login_url='login')
def saisir_nom_editeur(request):
    if request.method == 'POST':
        form = NomEditeurForm(request.POST)
        if form.is_valid():
            nom = form.cleaned_data['nom']

            if Editeur.objects.filter(nom=nom).exists():
                return redirect(reverse('editeurs_update', kwargs={'nom': nom}))
            else:
                return render(request, 'gui/saisir_editeur_nom.html', {'form': form, 'error': 'Editeur non trouvé.'})
    else:
        form = NomEditeurForm()
    return render(request, 'gui/saisir_editeur_nom.html', {'form': form})

"""########################################################"""


class AuteurList(StaffRequiredMixin,ListView):
    model = Auteur
    template_name = 'gui/lister_auteurs.html'

    def get_queryset(self):
        # Récupérer les paramètres GET
        sort_by = self.request.GET.get('sort_by', 'id')  # Par défaut : tri par 'nom'
        order = self.request.GET.get('order', 'asc')  # Par défaut : ordre ascendant

        # Définir le préfixe pour la direction du tri
        sort_prefix = '' if order == 'asc' else '-'

        # Options de tri supportées
        sorting_options = {
            'id':'id',
            'nom': 'nom',
            'prenom': 'prenom',
        }

        # Récupérer le queryset initial
        queryset = super().get_queryset()

        # Appliquer le tri si valide, sinon fallback au tri par 'nom'
        if sort_by in sorting_options:
            queryset = queryset.order_by(f"{sort_prefix}{sorting_options[sort_by]}")

        return queryset


class AuteurCreate(StaffRequiredMixin,CreateView):
    model = Auteur
    fields = ['nom', 'prenom', 'date_naissance']
    template_name = 'gui/ajouter_auteur.html'
    success_url = reverse_lazy('auteurs_list')


class AuteurDelete(StaffRequiredMixin,View):
    template_name = 'gui/supprimer_auteur.html'

    def get(self, request):
        # Afficher le formulaire où l'utilisateur entre l'ID du livre
        return render(request, self.template_name)

    def post(self, request):
        # Récupérer l'ID du livre soumis dans le formulaire
        auteur_id = request.POST.get('auteur_id')
        if auteur_id:
            # Obtenir l'objet Livre avec l'ID fourni
            auteur = get_object_or_404(Auteur, pk=auteur_id)
            # Supprimer le livre
            auteur.delete()
            # Rediriger vers la liste des livres après la suppression
            return redirect(reverse_lazy('auteurs_list'))
        return render(request, self.template_name, {'error': "ID de l'auteur invalide."})


class AuteurUpdate(StaffRequiredMixin,View):
    template_name = 'gui/modifier_auteur.html'

    def get(self, request, auteur_id):
        auteur = get_object_or_404(Auteur, id=auteur_id)
        form = AuteurForm(instance=auteur)
        return render(request, self.template_name, {'form': form, 'auteur': auteur})

    def post(self, request, auteur_id):
        auteur = get_object_or_404(Auteur, id=auteur_id)
        form = AuteurForm(request.POST, instance=auteur)

        if form.is_valid():
            form.save()
            return redirect('auteurs_list')  # Rediriger vers la liste des livres après modification

        return render(request, self.template_name, {'form': form, 'auteur': auteur})

class AuteurResearch(StaffRequiredMixin,ListView):
    model = Auteur
    template_name = 'gui/lister_auteurs.html'

    def get_queryset(self):
        search_query = self.request.GET.get('search', '')

        if search_query:
            # Diviser la chaîne de recherche en mots-clés
            keywords = search_query.split()
            query = Q()

            for keyword in keywords:
                # Ajouter chaque mot aux différents champs de recherche
                query |= Q(nom__icontains=keyword) | \
                         Q(prenom__icontains=keyword)|\
                        Q(id__icontains=keyword)

            # Retourner les livres correspondant aux critères
            return Auteur.objects.filter(query).distinct()

        # Si aucun terme de recherche, retourner tous les livres
        return Auteur.objects.all()

@login_required(login_url='login')
def saisir_ID_auteur(request):
    if request.method == 'POST':
        form = IDAuteurForm(request.POST)
        if form.is_valid():
            auteur_id = form.cleaned_data['auteur_id']

            if Auteur.objects.filter(id=auteur_id).exists():
                return redirect(reverse('auteurs_update', kwargs={'auteur_id': auteur_id}))
            else:
                return render(request, 'gui/saisir_auteur_ID.html', {'form': form, 'error': 'Auteur non trouvé.'})
    else:
        form = IDAuteurForm()
    return render(request, 'gui/saisir_auteur_ID.html', {'form': form})

"""########################################################"""


class LivreList(StaffRequiredMixin,ListView):
    model = Livre
    template_name = 'gui/lister_livres.html'

    def get_queryset(self):
        # Précharger les relations pour optimiser les requêtes
        queryset = Livre.objects.prefetch_related(
            Prefetch('ecrire_set', queryset=Ecrire.objects.select_related('auteur'))
        )

        # Récupérer les paramètres GET
        sort_by = self.request.GET.get('sort_by', 'titre')  # Par défaut : titre
        order = self.request.GET.get('order', 'asc')  # Par défaut : asc

        # Définir le préfixe pour la direction du tri
        sort_prefix = '' if order == 'asc' else '-'

        # Options de tri supportées
        sorting_options = {
            'isbn13': 'isbn13',
            'titre': 'titre',
            'auteur_nom': 'ecrire_set__auteur__nom',
            'type': 'type',
            'genre_litteraire': 'genre_litteraire',
            'sous_genre': 'sous_genre',
            'illustrateur': 'illustrateur',
            'langue': 'langue',
            'format': 'format',
            'date_parution': 'date_parution',
            'localisation': 'localisation',
            'prix': 'prix',
            'editeur': 'editeur',
        }

        # Appliquer le tri si valide, sinon fallback au tri par titre
        if sort_by in sorting_options:
            queryset = queryset.order_by(f"{sort_prefix}{sorting_options[sort_by]}")

        return queryset

@login_required(login_url='login')
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


class LivreDelete(StaffRequiredMixin,View):
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


class LivreUpdate(StaffRequiredMixin,View):
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


class LivreResearch(StaffRequiredMixin,ListView):
    model = Livre
    template_name = 'gui/lister_livres.html'

    def get_queryset(self):
        search_query = self.request.GET.get('search', '')

        if search_query:
            # Diviser la chaîne de recherche en mots-clés
            keywords = search_query.split()
            query = Q()

            for keyword in keywords:
                # Ajouter chaque mot aux différents champs de recherche
                query |= Q(titre__icontains=keyword) | \
                         Q(editeur__nom__icontains=keyword) | \
                         Q(ecrire_set__auteur__nom__icontains=keyword) | \
                         Q(isbn13__icontains=keyword) | \
                         Q(type__icontains=keyword) | \
                         Q(genre_litteraire__icontains=keyword) | \
                         Q(sous_genre__icontains=keyword) | \
                         Q(illustrateur__icontains=keyword) | \
                         Q(langue__icontains=keyword) | \
                         Q(ecrire_set__auteur__prenom__icontains=keyword)

            # Retourner les livres correspondant aux critères
            return Livre.objects.filter(query).distinct()

        # Si aucun terme de recherche, retourner tous les livres
        return Livre.objects.all()

@login_required(login_url='login')
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

class EcrireList(StaffRequiredMixin,ListView):
    model = Ecrire
    template_name = 'gui/lister_ecrits.html'


class EcrireCreate(StaffRequiredMixin,CreateView):
    model = Ecrire
    fields = ['livre', 'auteur']
    template_name = 'gui/ajouter_ecrire.html'
    success_url = reverse_lazy('ecrits_list')

"""########################################################"""


class CommanderList(StaffRequiredMixin,ListView):
    model = Commander
    template_name = 'gui/lister_commandes.html'


class CommanderCreate(StaffRequiredMixin,CreateView):
    model = Commander
    fields =['personne', 'livre', 'quantite', 'date_commande', 'quantite', 'statut']
    template_name = 'gui/ajouter_commande.html'
    success_url = reverse_lazy('commandes_list')

"""########################################################"""

# 13. Classe Reserver

class ReserverList(StaffRequiredMixin,ListView):
    model = Reserver
    template_name = 'gui/lister_reservations.html'


class ReserverCreate(StaffRequiredMixin,CreateView):
    model = Reserver
    fields = ['personne', 'livre', 'quantite', 'statut', 'date_reservation']
    template_name = 'gui/ajouter_reservation.html'
    success_url = reverse_lazy('reservations_list')

"""########################################################"""

class AchatList(StaffRequiredMixin,ListView):
    model = Achat
    template_name = 'gui/lister_achats.html'


class AchatCreate(StaffRequiredMixin,CreateView):
    model = Achat
    fields = ['personne', 'livre', 'quantite', 'date_achat']
    template_name = 'gui/ajouter_achat.html'
    success_url = reverse_lazy('achats_list')

"""########################################################"""


class NotifierList(StaffRequiredMixin,ListView):
    model = Notifier
    template_name = 'gui/lister_notifications.html'


class NotifierCreate(StaffRequiredMixin,CreateView):
    model = Notifier
    fields = ['personne', 'livre', 'quantite', 'type', 'commentaire']
    template_name = 'gui/ajouter_notification.html'
    success_url = reverse_lazy('notifications_list')







