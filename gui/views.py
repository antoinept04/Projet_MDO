from datetime import timedelta
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required #accès aux pages seulement si login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Prefetch
from django.http import HttpResponseRedirect, HttpResponseForbidden #rediriger vers une autre url, refuser l'accès à une url
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import ListView, CreateView, DeleteView, UpdateView, View, TemplateView
from gui.models import Ville, Adresse, Role, Personne, Fournisseur, Editeur, Auteur, Livre, Ecrire, Commander, Notifier, Illustrer, Traduire, \
    Achat, Reserver, Illustrateur, Traducteur, FournisseurAdresse
from .decorators import unauthenticated_user_required, staff_required
from .forms import (PersonneForm, AdresseForm, LivreForm, ISBNForm, AuteurForm, VilleForm, EditeurForm, IDEditeurForm, EmailInputForm, \
    IDAuteurForm, IllustrateurForm, IDIllustrateurForm, TraducteurForm, IDTraducteurForm, IDReservationForm, IDAchatForm, CommanderForm, IDCommandeForm, ReserverForm, AchatForm, FournisseurForm, IDFournisseurForm,
                    AdresseFormSet, FournisseurAdresseFormSet)
from django.db import transaction


#%%"""------------------------------LOGIN/LOGOUT------------------------------"""

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


#%%"""------------------------------HOMEPAGE------------------------------"""
@login_required(login_url='login')
def home(request):
    return render(request, 'gui/homepage.html')

@login_required(login_url='login')
def autres(request):
    return render(request, 'gui/autres.html')

#%%"""########################################################"""
#Super classe définissant les permissions
class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = 'login'  # URL de redirection si l'utilisateur n'est pas connecté

    def test_func(self):
        # Vérifie que l'utilisateur a le statut is_staff
        return self.request.user.is_staff


#%%------------------------------GERER-LES-ROLES------------------------------

class RoleList(StaffRequiredMixin,ListView):
    model = Role
    template_name = 'gui/lister_roles.html'

class RoleCreate(StaffRequiredMixin,CreateView):
    model = Role
    fields = ['type']
    template_name = 'gui/ajouter_role.html'
    success_url = reverse_lazy('roles_list')


#%%------------------------------GERER-LES-VILLES------------------------------

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


#%%------------------------------GERER-LES-ADRESSES----------------------------------

class AdresseList(StaffRequiredMixin,ListView):
    model = Adresse
    template_name = 'gui/lister_adresses.html'

    def get_queryset(self):
        # Récupérer les paramètres GET
        sort_by = self.request.GET.get('sort_by', 'id')  # Par défaut : titre
        order = self.request.GET.get('order', 'asc')  # Par défaut : asc

        # Définir le préfixe pour la direction du tri
        sort_prefix = '' if order == 'asc' else '-'

        # Options de tri supportées
        sorting_options = {
            'id':'id',
            'rue':'rue',
            'n_rue':'n_rue',
            'ville':'ville',
            'ville_code_postal':'ville__code_postal',
            'ville_pays':'ville__pays',
        }
        queryset = super().get_queryset()

        # Appliquer le tri si valide, sinon fallback au tri par titre
        if sort_by in sorting_options:
            queryset = queryset.order_by(f"{sort_prefix}{sorting_options[sort_by]}")

        return queryset


@login_required(login_url='login')
def create_adresse(request):
    if request.method == 'POST':
        adresse_form = AdresseForm(request.POST)

        if adresse_form.is_valid():
            # Récupérer les informations de l'adresse
            rue = adresse_form.cleaned_data['rue']
            n_rue = adresse_form.cleaned_data['n_rue']

            # Récupérer les informations de la ville depuis le formulaire
            nom_ville = request.POST.get('nom_ville')
            code_postal = request.POST.get('code_postal')
            pays = request.POST.get('pays')

            if nom_ville and code_postal and pays:
                # Créer ou récupérer la ville correspondante
                ville, created = Ville.objects.get_or_create(
                    nom_ville=nom_ville,
                    defaults={
                        'code_postal': code_postal,
                        'pays': pays
                    }
                )

                # Vérifier si une adresse identique existe déjà
                if Adresse.objects.filter(rue=rue, n_rue=n_rue, ville=ville).exists():
                    adresse_form.add_error(None, "Cette adresse existe déjà.")
                else:
                    # Créer et enregistrer l'adresse
                    adresse = adresse_form.save(commit=False)
                    adresse.ville = ville
                    adresse.save()

                    return redirect('adresses_list')  # Rediriger après la création
            else:
                # Gérer le cas où les informations de la ville sont incomplètes
                adresse_form.add_error(None, "Veuillez remplir les informations de la ville.")
    else:
        adresse_form = AdresseForm()

    return render(request, 'gui/ajouter_adresse.html', {
        'adresse_form': adresse_form,
    })

class AdresseResearch(StaffRequiredMixin,ListView):
    model = Adresse
    template_name = 'gui/lister_adresses.html'

    def get_queryset(self):
        search_query = self.request.GET.get('search', '')

        if search_query:
            # Diviser la chaîne de recherche en mots-clés
            keywords = search_query.split()
            query = Q()

            for keyword in keywords:
                # Ajouter chaque mot aux différents champs de recherche
                query |= Q(rue__icontains=keyword) | \
                         Q(n_rue__icontains=keyword)|\
                        Q(ville__nom_ville__icontains=keyword) |\
                        Q(ville__code_postal__icontains=keyword)|\
                        Q(ville__pays__icontains=keyword)

            # Retourner les livres correspondant aux critères
            return Adresse.objects.filter(query).distinct()

        # Si aucun terme de recherche, retourner tous les livres
        return Adresse.objects.all()

class AdresseDelete(StaffRequiredMixin, View):
    template_name = 'gui/supprimer_adresse.html'

    def get(self, request):
        # Afficher le formulaire où l'utilisateur entre l'email de la personne
        return render(request, self.template_name)

    def post(self, request):
        # Récupérer l'email de la personne soumis dans le formulaire
        adresse_id = request.POST.get('adresse_id')
        if adresse_id:
            # Obtenir l'objet Personne avec l'email fourni
            # Assurez-vous que le champ 'email' existe et est unique dans le modèle Personne
            adresse = get_object_or_404(Adresse, id=adresse_id)
            # Supprimer la personne
            adresse.delete()
            # Rediriger vers la liste des personnes après la suppression
            return redirect(reverse_lazy('adresses_list'))
        # Si l'email n'est pas fourni ou invalide, afficher une erreur
        return render(request, self.template_name, {'error': 'Adresse invalide.'})



#%%------------------------------GERER-LES-PERSONNES---------------------------------

class PersonneList(StaffRequiredMixin,ListView):
    model = Personne
    template_name = 'gui/lister_personnes.html'

    def get_queryset(self):
        # Récupérer les paramètres GET
        sort_by = self.request.GET.get('sort_by', 'nom')  # Par défaut : tri par 'nom'
        order = self.request.GET.get('order', 'asc')  # Par défaut : ordre ascendant

        # Définir le préfixe pour la direction du tri
        sort_prefix = '' if order == 'asc' else '-'

        # Options de tri supportées
        sorting_options = {
            'nom': 'nom',
            'prenom': 'prenom',
            'date_naissance': 'date_naissance',
            'email': 'email',
            'date_creation': 'date_creation',
            'solde': 'solde',
            'role': 'role',
            'adresse__ville__nom_ville': 'adresse__ville__nom_ville',
        }

        # Récupérer le queryset initial
        queryset = super().get_queryset()

        # Appliquer le tri si valide, sinon fallback au tri par 'nom'
        if sort_by in sorting_options:
            queryset = queryset.order_by(f"{sort_prefix}{sorting_options[sort_by]}")

        return queryset

@staff_required
def personne_create(request):
    if request.method == 'POST':
        form_personne = PersonneForm(request.POST, user=request.user)
        form_adresse = AdresseForm(request.POST)
        form_ville = VilleForm(request.POST)

        if form_personne.is_valid() and form_adresse.is_valid() and form_ville.is_valid():
            # Récupérer ou créer la ville
            nom_ville = form_ville.cleaned_data['nom_ville']
            code_postal = form_ville.cleaned_data['code_postal']
            pays = form_ville.cleaned_data['pays']

            ville, created = Ville.objects.get_or_create(
                nom_ville=nom_ville,
                code_postal=code_postal,
                pays=pays
            )

            # Récupérer ou créer l'adresse
            rue = form_adresse.cleaned_data['rue']
            n_rue = form_adresse.cleaned_data['n_rue']

            adresse, created = Adresse.objects.get_or_create(
                rue=rue,
                n_rue=n_rue,
                ville=ville
            )

            # Gestion du rôle
            if request.user.is_superuser:
                role = form_personne.cleaned_data.get('role')
            else:
                try:
                    role = Role.objects.get(type='Client')
                except Role.DoesNotExist:
                    form_personne.add_error('role', 'Le rôle "client" n\'existe pas.')
                    return render(request, 'gui/ajouter_personne.html', {
                        'form_personne': form_personne,
                        'form_adresse': form_adresse,
                        'form_ville': form_ville
                    })

            # Vérifier si l'email existe déjà
            email = form_personne.cleaned_data['email']
            password = form_personne.cleaned_data['password']

            if Personne.objects.filter(email=email).exists():
                form_personne.add_error('email', 'Cet email est déjà utilisé.')
                return render(request, 'gui/ajouter_personne.html', {
                    'form_personne': form_personne,
                    'form_adresse': form_adresse,
                    'form_ville': form_ville
                })

            # Récupérer les autres champs
            nom = form_personne.cleaned_data['nom']
            prenom = form_personne.cleaned_data['prenom']
            date_naissance = form_personne.cleaned_data['date_naissance']
            telephone = form_personne.cleaned_data['telephone']
            solde = form_personne.cleaned_data['solde']

            # Créer l'utilisateur en fonction du rôle
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

            # Redirection après succès
            return redirect('personnes_list')
    else:
        form_personne = PersonneForm(user=request.user)
        form_adresse = AdresseForm()
        form_ville = VilleForm()

    return render(request, 'gui/ajouter_personne.html',  {
        'form_personne': form_personne,
        'form_adresse': form_adresse,
        'form_ville': form_ville
    })



class PersonneResearch(StaffRequiredMixin,ListView):
    model = Personne
    template_name = 'gui/lister_personnes.html'

    def get_queryset(self):
        search_query = self.request.GET.get('search', '')

        if search_query:
            # Diviser la chaîne de recherche en mots-clés
            keywords = search_query.split()
            query = Q()

            for keyword in keywords:
                # Ajouter chaque mot aux différents champs de recherche
                query |= Q(nom__icontains=keyword) | \
                         Q(prenom__icontains=keyword) | \
                         Q(date_naissance__icontains=keyword) | \
                         Q(email__icontains=keyword) | \
                         Q(date_creation__icontains=keyword) | \
                         Q(adresse__ville__nom_ville__icontains=keyword)

            # Retourner les livres correspondant aux critères
            return Personne.objects.filter(query).distinct()

        # Si aucun terme de recherche, retourner tous les livres
        return Personne.objects.all()

class PersonneDelete(StaffRequiredMixin, View):
    template_name = 'gui/supprimer_personne.html'

    def get(self, request):
        # Afficher le formulaire où l'utilisateur entre l'email de la personne
        return render(request, self.template_name)

    def post(self, request):
        # Récupérer l'email de la personne soumis dans le formulaire
        personne_email = request.POST.get('personne_email')
        if personne_email:
            # Obtenir l'objet Personne avec l'email fourni
            personne = get_object_or_404(Personne, email=personne_email)

            # Vérifier les permissions
            if not request.user.is_superuser:  # Si l'utilisateur n'est pas un superuser
                roles_interdits = ['employe', 'admin']  # Rôles interdits
                if personne.role.type in roles_interdits:  # Vérifier le rôle de la personne
                    return HttpResponseForbidden(
                        "Vous n'êtes pas autorisé à supprimer cet utilisateur."
                    )

            # Supprimer la personne
            personne.delete()
            # Rediriger vers la liste des personnes après la suppression
            return redirect(reverse_lazy('personnes_list'))

        # Si l'email n'est pas fourni ou invalide, afficher une erreur
        return render(request, self.template_name, {'error': 'Email invalide.'})




class PersonneSelectView(StaffRequiredMixin, View):
    template_name = 'gui/select_personne.html'

    def get(self, request):
        form = EmailInputForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = EmailInputForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            # Vérifier si la personne existe
            personne = get_object_or_404(Personne, email=email)

            # Vérifier les permissions
            if not request.user.is_superuser:  # Si l'utilisateur n'est pas un superuser
                # Récupérer les rôles non autorisés
                roles_interdits = ['employe', 'admin']
                if personne.role.type in roles_interdits:
                    # Interdire l'accès si le rôle est employé ou admin
                    return HttpResponseForbidden("Vous n'êtes pas autorisé à modifier cet utilisateur.")

            # Rediriger vers la vue de modification avec l'email comme paramètre
            return redirect(reverse('personnes_update', args=[email]))
        else:
            messages.error(request, 'Veuillez saisir un email valide.')
            return render(request, self.template_name, {'form': form})

class PersonneUpdate(StaffRequiredMixin, View):
    template_name = 'gui/modifier_personnes.html'

    def get(self, request, email):
        """
        Affiche les formulaires pré-remplis avec les données de la personne, de son adresse et de sa ville.
        """
        personne = get_object_or_404(Personne, email=email)
        adresse = personne.adresse
        ville = adresse.ville if adresse.ville else None

        personne_form = PersonneForm(instance=personne, user=request.user)
        adresse_form = AdresseForm(instance=adresse)
        ville_form = VilleForm(instance=ville)

        return render(request, self.template_name, {
            'personne_form': personne_form,
            'adresse_form': adresse_form,
            'ville_form': ville_form,
            'personne': personne
        })

    def post(self, request, email):
        """
        Traite les données soumises et met à jour la personne, son adresse et sa ville si les données sont valides.
        """
        personne = get_object_or_404(Personne, email=email)
        adresse = personne.adresse
        ville = adresse.ville if adresse.ville else None

        personne_form = PersonneForm(request.POST, instance=personne, user=request.user)
        adresse_form = AdresseForm(request.POST, instance=adresse)
        ville_form = VilleForm(request.POST, instance=ville)

        if personne_form.is_valid() and adresse_form.is_valid() and ville_form.is_valid():
            with transaction.atomic():
                # Gérer la Ville
                cleaned_ville = ville_form.cleaned_data
                nom_ville = cleaned_ville.get('nom_ville')
                code_postal = cleaned_ville.get('code_postal')
                pays = cleaned_ville.get('pays')

                if nom_ville and code_postal and pays:
                    ville_obj, created = Ville.objects.get_or_create(
                        nom_ville=nom_ville,
                        code_postal=code_postal,
                        pays=pays
                    )
                else:
                    ville_obj = None  # Gérer les cas où les champs sont manquants

                # Gérer l'Adresse
                # Vérifier si l'adresse est partagée
                if Adresse.objects.filter(pk=adresse.pk).exclude(personne=personne).exists():
                    # L'adresse est partagée, créer une nouvelle adresse pour cette personne
                    nouvelle_adresse = Adresse.objects.create(
                        rue=adresse.rue,
                        n_rue=adresse.n_rue,
                        ville=ville_obj
                    )
                    personne.adresse = nouvelle_adresse
                else:
                    # L'adresse n'est pas partagée, la modifier directement
                    adresse_form.instance.ville = ville_obj
                    adresse_form.save()

                # Gérer la Personne
                personne_form.save()

            messages.success(request, 'La personne, son adresse et sa ville ont été mises à jour avec succès.')
            return redirect(reverse_lazy('personnes_list'))

        # Si l'un des formulaires n'est pas valide, réafficher les formulaires avec les erreurs
        messages.error(request, 'Certaines données sont invalides. Veuillez corriger les erreurs ci-dessous.')
        return render(request, self.template_name, {
            'personne_form': personne_form,
            'adresse_form': adresse_form,
            'ville_form': ville_form,
            'personne': personne
        })

#%%------------------------------GERER-LES-FOURNISSEURS------------------------------
class FournisseurList(StaffRequiredMixin, ListView):
    model = Fournisseur
    template_name = 'gui/lister_fournisseurs.html'
    context_object_name = 'fournisseurs'

    def get_queryset(self):
        sort_by = self.request.GET.get('sort_by', 'nom_fournisseur')
        order = self.request.GET.get('order', 'asc')
        search_query = self.request.GET.get('search', '')
        sort_prefix = '' if order == 'asc' else '-'
        sorting_options = {
            'nom_fournisseur': 'nom_fournisseur',
            # 'ville': 'adresses__ville__nom_ville',  # Décommentez si vous souhaitez trier par ville
        }

        queryset = super().get_queryset()

        # Filtre le queryset en fonction de la requête de recherche
        if search_query:
            queryset = queryset.filter(
                Q(nom_fournisseur__icontains=search_query) |
                Q(adresses__ville__nom_ville__icontains=search_query)
            ).distinct()

        # Trie le queryset en fonction des paramètres de tri
        if sort_by in sorting_options:
            queryset = queryset.order_by(f"{sort_prefix}{sorting_options[sort_by]}")
        else:
            queryset = queryset.order_by('nom_fournisseur')

        return queryset.prefetch_related('adresses', 'adresses__ville')


# views.py

# views.py

# gui/views.py

# gui/views.py

def fournisseur_create(request):
    if request.method == 'POST':
        form_fournisseur = FournisseurForm(request.POST)
        formset_adresse = FournisseurAdresseFormSet(request.POST)

        if form_fournisseur.is_valid() and formset_adresse.is_valid():
            fournisseur = form_fournisseur.save()

            # Sauvegarder chaque adresse dans le formset
            for form in formset_adresse:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    adresse = form.cleaned_data['adresse']
                    # Optionnel: Créez une nouvelle adresse si nécessaire
                    FournisseurAdresse.objects.create(fournisseur=fournisseur, adresse=adresse)

            return redirect('fournisseurs_list')
    else:
        form_fournisseur = FournisseurForm()
        formset_adresse = FournisseurAdresseFormSet()

    return render(request, 'gui/ajouter_fournisseur.html', {
        'form_fournisseur': form_fournisseur,
        'formset_adresse': formset_adresse
    })



class FournisseurDelete(DeleteView):
    model = Fournisseur
    template_name = 'gui/supprimer_fournisseur.html'
    success_url = reverse_lazy('fournisseurs_list')

    # Si vous surchargez la méthode get(), assurez-vous d'inclure *args et **kwargs
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    # De même pour la méthode post(), si nécessaire
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)




class FournisseurUpdate(StaffRequiredMixin, UpdateView):
    model = Fournisseur
    form_class = FournisseurForm
    template_name = 'gui/modifier_fournisseur.html'
    success_url = reverse_lazy('fournisseurs_list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['formset_adresse'] = FournisseurAdresseFormSet(self.request.POST, instance=self.object)
        else:
            data['formset_adresse'] = FournisseurAdresseFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset_adresse']
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return redirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))

class FournisseurResearch(StaffRequiredMixin, ListView):
    model = Fournisseur
    template_name = 'gui/lister_fournisseurs.html'
    context_object_name = 'fournisseurs'

    def get_queryset(self):
        search_query = self.request.GET.get('search', '')

        if search_query:
            keywords = search_query.split()
            query = Q()

            for keyword in keywords:
                query |= Q(nom_fournisseur__icontains=keyword) | \
                         Q(adresses__rue__icontains=keyword) | \
                         Q(adresses__ville__icontains=keyword) | \
                         Q(adresses__code_postal__icontains=keyword) | \
                         Q(adresses__pays__icontains=keyword)

            return Fournisseur.objects.filter(query).distinct().prefetch_related('adresses')

        return Fournisseur.objects.all().prefetch_related('adresses')



class SaisirIDFournisseurView(StaffRequiredMixin, View):
    template_name = 'gui/saisir_fournisseur_ID.html'

    def get(self, request):
        form = IDFournisseurForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = IDFournisseurForm(request.POST)
        if form.is_valid():
            nom_fournisseur = form.cleaned_data['nom_fournisseur']
            try:
                fournisseur = Fournisseur.objects.get(nom_fournisseur=nom_fournisseur)
                return redirect(reverse_lazy('fournisseurs_update', kwargs={'pk': fournisseur.pk}))
            except Fournisseur.DoesNotExist:
                return render(request, self.template_name, {'form': form, 'error': 'Fournisseur non trouvé.'})
        return render(request, self.template_name, {'form': form})



#%%------------------------------GERER-LES-EDITEURS----------------------------------

#%%
class EditeurList(ListView):
    model = Editeur
    template_name = 'gui/lister_editeurs.html'

    def get_queryset(self):
        # Récupérer les paramètres GET
        sort_by = self.request.GET.get('sort_by', 'id')  # Par défaut : tri par 'id'
        order = self.request.GET.get('order', 'asc')  # Par défaut : ordre ascendant

        # Définir le préfixe pour la direction du tri
        sort_prefix = '' if order == 'asc' else '-'

        # Options de tri supportées
        sorting_options = {
            'id' : 'id',
            'nom': 'nom'
        }

        # Récupérer le queryset initial
        queryset = super().get_queryset()

        # Appliquer le tri si valide, sinon fallback au tri par 'nom'
        if sort_by in sorting_options:
            queryset = queryset.order_by(f"{sort_prefix}{sorting_options[sort_by]}")

        return queryset
#%%
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
        editeur_id = request.POST.get('editeur_id')
        if editeur_id:
            # Obtenir l'objet Livre avec l'ID fourni
            editeur = get_object_or_404(Editeur, pk=editeur_id)
            # Supprimer le livre
            editeur.delete()
            # Rediriger vers la liste des livres après la suppression
            return redirect(reverse_lazy('editeurs_list'))
        return render(request, self.template_name, {'error': "ID de l'éditeur invalide."})

class EditeurUpdate(StaffRequiredMixin,View):
    template_name = 'gui/modifier_editeurs.html'

    def get(self, request, id):
        editeur = get_object_or_404(Editeur, id=id)
        form = EditeurForm(instance=editeur)
        return render(request, self.template_name, {'form': form, 'editeur': editeur})

    def post(self, request, id):
        editeur = get_object_or_404(Editeur, id=id)
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
def saisir_ID_editeur(request):
    if request.method == 'POST':
        form = IDEditeurForm(request.POST)
        if form.is_valid():
            id = form.cleaned_data['id']

            if Editeur.objects.filter(id=id).exists():
                return redirect(reverse('editeurs_update', kwargs={'id': id}))
            else:
                return render(request, 'gui/saisir_editeur_ID.html', {'form': form, 'error': 'Editeur non trouvé.'})
    else:
        form = IDEditeurForm()
    return render(request, 'gui/saisir_editeur_ID.html', {'form': form})

#%%------------------------------GERER-LES-AUTEURS-----------------------------------

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
    form_class = AuteurForm
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


#%%------------------------------GERER-LES-LIVRES------------------------------------
class LivreList(StaffRequiredMixin,ListView):
    model = Livre
    template_name = 'gui/lister_livres.html'

    def get_queryset(self):
        # Précharger les relations pour optimiser les requêtes
        queryset = Livre.objects.prefetch_related(
            Prefetch('ecrire_set', queryset=Ecrire.objects.select_related('auteur')),
            Prefetch('illustrer_set', queryset=Illustrer.objects.select_related('illustrateur')),
            Prefetch('traduire_set', queryset=Traduire.objects.select_related('traducteur')),
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
            'illustrateur_nom' : 'illustrer_set__illustrateur__nom',
            'traducteur_nom' : 'traduire_set__traducteur__nom',
            'type': 'type',
            'genre_litteraire': 'genre_litteraire',
            'sous_genre': 'sous_genre',
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

        if livre_form.is_valid():
            # Sauvegarder le livre
            livre = livre_form.save()

            # Récupérer les informations des auteurs depuis le formulaire
            noms_auteurs = request.POST.getlist('nom_auteur')  # Récupère tous les noms d'auteurs
            prenoms_auteurs = request.POST.getlist('prenom_auteur')  # Récupère tous les prénoms d'auteurs
            dates_naissance_auteurs = request.POST.getlist('date_naissance_auteur')  # Récupère toutes les dates de naissance

            for nom, prenom, date_naissance in zip(noms_auteurs, prenoms_auteurs, dates_naissance_auteurs):
                if nom and prenom:  # Vérifier que les informations sont présentes
                    auteur, created = Auteur.objects.get_or_create(
                        nom=nom,
                        prenom=prenom,
                        date_naissance=date_naissance if date_naissance else None
                    )
                    # Associer l'auteur au livre dans la table intermédiaire 'Ecrire'
                    Ecrire.objects.create(livre=livre, auteur=auteur)

            # Gérer les traducteurs
            noms_traducteurs = request.POST.getlist('nom_traducteur')
            prenoms_traducteurs = request.POST.getlist('prenom_traducteur')
            dates_naissance_traducteurs = request.POST.getlist('date_naissance_traducteur')

            for nom, prenom, date_naissance in zip(noms_traducteurs, prenoms_traducteurs, dates_naissance_traducteurs):
                if nom and prenom:
                    traducteur, created = Traducteur.objects.get_or_create(
                        nom=nom,
                        prenom=prenom,
                        date_naissance=date_naissance if date_naissance else None
                    )
                    # Associer le traducteur au livre
                    Traduire.objects.create(livre=livre, traducteur=traducteur)

            # Gérer les illustrateurs
            noms_illustrateurs = request.POST.getlist('nom_illustrateur')
            prenoms_illustrateurs = request.POST.getlist('prenom_illustrateur')
            dates_naissance_illustrateurs = request.POST.getlist('date_naissance_illustrateur')

            for nom, prenom, date_naissance in zip(noms_illustrateurs, prenoms_illustrateurs, dates_naissance_illustrateurs):
                if nom and prenom:
                    illustrateur, created = Illustrateur.objects.get_or_create(
                        nom=nom,
                        prenom=prenom,
                        date_naissance=date_naissance if date_naissance else None
                    )
                    # Associer l'illustrateur au livre
                    Illustrer.objects.create(livre=livre, illustrateur=illustrateur)

            return redirect('livres_list')  # Redirige vers la liste des livres ou une page de succès
    else:
        livre_form = LivreForm()

    return render(request, 'gui/ajouter_livre.html', {
        'livre_form': livre_form,
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

#%%------------------------------LIEN-LIVRE/AUTEUR-----------------------------------
class EcrireList(StaffRequiredMixin,ListView):
    model = Ecrire
    template_name = 'gui/lister_ecrits.html'
class EcrireCreate(StaffRequiredMixin,CreateView):
    model = Ecrire
    fields = ['livre', 'auteur']
    template_name = 'gui/ajouter_ecrire.html'
    success_url = reverse_lazy('ecrits_list')

#%%------------------------------GERER-LES-ILLUSTRATEURS-----------------------------
class IllustrateurList(StaffRequiredMixin,ListView):
    model = Illustrateur
    template_name = 'gui/lister_illustrateurs.html'

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
class IllustrateurCreate(StaffRequiredMixin, CreateView):
    model = Illustrateur
    form_class = IllustrateurForm
    template_name = 'gui/ajouter_illustrateur.html'
    success_url = reverse_lazy('illustrateurs_list')
class IllustrateurDelete(StaffRequiredMixin,View):
    template_name = 'gui/supprimer_illustrateur.html'

    def get(self, request):
        # Afficher le formulaire où l'utilisateur entre l'ID du livre
        return render(request, self.template_name)

    def post(self, request):
        # Récupérer l'ID du livre soumis dans le formulaire
        illustrateur_id = request.POST.get('illustrateur_id')
        if illustrateur_id:
            # Obtenir l'objet Livre avec l'ID fourni
            illustrateur = get_object_or_404(Illustrateur, pk=illustrateur_id)
            # Supprimer le livre
            illustrateur.delete()
            # Rediriger vers la liste des livres après la suppression
            return redirect(reverse_lazy('illustrateurs_list'))
        return render(request, self.template_name, {'error': "ID de l'illustrateur invalide."})
class IllustrateurUpdate(StaffRequiredMixin,View):
    template_name = 'gui/modifier_illustrateur.html'

    def get(self, request, illustrateur_id):
        illustrateur = get_object_or_404(Illustrateur, id=illustrateur_id)
        form = IllustrateurForm(instance=illustrateur)
        return render(request, self.template_name, {'form': form, 'illustrateur': illustrateur})

    def post(self, request, illustrateur_id):
        illustrateur = get_object_or_404(Illustrateur, id=illustrateur_id)
        form = IllustrateurForm(request.POST, instance=illustrateur)

        if form.is_valid():
            form.save()
            return redirect('illustrateurs_list')  # Rediriger vers la liste des livres après modification

        return render(request, self.template_name, {'form': form, 'illustrateur': illustrateur})
class IllustrateurResearch(StaffRequiredMixin,ListView):
    model = Illustrateur
    template_name = 'gui/lister_illustrateurs.html'

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
            return Illustrateur.objects.filter(query).distinct()

        # Si aucun terme de recherche, retourner tous les livres
        return Illustrateur.objects.all()
@login_required(login_url='login')
def saisir_ID_illustrateur(request):
    if request.method == 'POST':
        form = IDIllustrateurForm(request.POST)
        if form.is_valid():
            illustrateur_id = form.cleaned_data['illustrateur_id']

            if Illustrateur.objects.filter(id=illustrateur_id).exists():
                return redirect(reverse('illustrateurs_update', kwargs={'illustrateur_id': illustrateur_id}))
            else:
                return render(request, 'gui/saisir_illustrateur_ID.html', {'form': form, 'error': 'Illustrateur non trouvé.'})
    else:
        form = IDIllustrateurForm()
    return render(request, 'gui/saisir_illustrateur_ID.html', {'form': form})

#%%------------------------------GERER-LES-TRADUCTEURS-------------------------------
class TraducteurList(StaffRequiredMixin, ListView):
    model = Traducteur
    template_name = 'gui/lister_traducteurs.html'
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
class TraducteurCreate(StaffRequiredMixin, CreateView):
    model = Traducteur
    form_class = TraducteurForm
    template_name = 'gui/ajouter_traducteur.html'
    success_url = reverse_lazy('traducteurs_list')
class TraducteurDelete(StaffRequiredMixin, View):
    template_name = 'gui/supprimer_traducteur.html'

    def get(self, request):
        # Afficher le formulaire où l'utilisateur entre l'ID du traducteur
        return render(request, self.template_name)

    def post(self, request):
        # Récupérer l'ID du traducteur soumis dans le formulaire
        traducteur_id = request.POST.get('traducteur_id')
        if traducteur_id:
            # Obtenir l'objet Traducteur avec l'ID fourni
            traducteur = get_object_or_404(Traducteur, pk=traducteur_id)
            # Supprimer le traducteur
            traducteur.delete()
            # Rediriger vers la liste des traducteurs après la suppression
            return redirect(reverse_lazy('traducteurs_list'))
        return render(request, self.template_name, {'error': "ID du traducteur invalide."})
class TraducteurUpdate(StaffRequiredMixin, View):
    template_name = 'gui/modifier_traducteur.html'

    def get(self, request, traducteur_id):
        traducteur = get_object_or_404(Traducteur, id=traducteur_id)
        form = TraducteurForm(instance=traducteur)
        return render(request, self.template_name, {'form': form, 'traducteur': traducteur})

    def post(self, request, traducteur_id):
        traducteur = get_object_or_404(Traducteur, id=traducteur_id)
        form = TraducteurForm(request.POST, instance=traducteur)

        if form.is_valid():
            form.save()
            return redirect('traducteurs_list')  # Rediriger vers la liste des traducteurs après modification

        return render(request, self.template_name, {'form': form, 'traducteur': traducteur})
class TraducteurResearch(StaffRequiredMixin, ListView):
    model = Traducteur
    template_name = 'gui/lister_traducteurs.html'

    def get_queryset(self):
        search_query = self.request.GET.get('search', '')

        if search_query:
            # Diviser la chaîne de recherche en mots-clés
            keywords = search_query.split()
            query = Q()

            for keyword in keywords:
                # Ajouter chaque mot aux différents champs de recherche
                query |= Q(nom__icontains=keyword) | \
                         Q(prenom__icontains=keyword) | \
                         Q(id__icontains=keyword)

            # Retourner les traducteurs correspondant aux critères
            return Traducteur.objects.filter(query).distinct()

        # Si aucun terme de recherche, retourner tous les traducteurs
        return Traducteur.objects.all()
@login_required(login_url='login')
def saisir_ID_traducteur(request):
    if request.method == 'POST':
        form = IDTraducteurForm(request.POST)
        if form.is_valid():
            traducteur_id = form.cleaned_data['traducteur_id']

            if Traducteur.objects.filter(id=traducteur_id).exists():
                return redirect(reverse('traducteurs_update', kwargs={'traducteur_id': traducteur_id}))
            else:
                return render(request, 'gui/saisir_traducteur_ID.html', {'form': form, 'error': 'Traducteur non trouvé.'})
    else:
        form = IDTraducteurForm()
    return render(request, 'gui/saisir_traducteur_ID.html', {'form': form})

#%%------------------------------GERER-LES-ACHATS------------------------------------
class AchatList(StaffRequiredMixin,ListView):
    model = Achat
    template_name = 'gui/lister_achats.html'
    context_object_name = 'achats'
    def get_queryset(self):
        sort_by = self.request.GET.get('sort_by', 'date_achat')
        order = self.request.GET.get('order', 'asc')
        sort_prefix = '' if order == 'asc' else '-'
        sorting_options = {
            'date': 'date_achat',
            'quantite': 'quantite',
        }
        queryset = super().get_queryset()
        # Appliquer le tri si valide, sinon fallback au tri par 'nom'
        if sort_by in sorting_options:
            queryset = queryset.order_by(f"{sort_prefix}{sorting_options[sort_by]}")
        return queryset
class AchatCreate(StaffRequiredMixin,CreateView):
    model = Achat
    form_class = AchatForm
    template_name = 'gui/ajouter_achat.html'
    success_url = reverse_lazy('achats_list')
class AchatUpdate(StaffRequiredMixin, UpdateView):
    model = Achat
    form_class = AchatForm
    template_name = 'gui/modifier_achat.html'
    sucess_url = reverse_lazy('achats_list')
    def get_object(self):
        return get_object_or_404(Achat, pk=self.kwargs['pk'])
class AchatDelete(StaffRequiredMixin, View):
    template_name = 'gui/supprimer_achat.html'

    def get(self, request, pk=None):
        achat = None
        if pk:
            achat = get_object_or_404(Achat, pk=pk)
        return render(request, self.template_name, {'achat': achat})

    def post(self, request, pk=None):
        achat_id = pk or request.POST.get('achat_id')
        if achat_id:
            try:
                achat = Achat.objects.get(id=achat_id)
                if pk:
                    achat.delete()
                    return redirect(reverse_lazy('achats_list'))
                else:
                    return redirect(reverse_lazy('achats_with_ID_delete', kwargs={'pk': achat.id}))
            except Achat.DoesNotExist:
                return render(request, self.template_name, {'error': "Achat non trouvée."})
        return render(request, self.template_name, {'error': "ID d'achat invalide."})
class AchatResearch(StaffRequiredMixin, ListView):
    model = Achat
    template_name = 'gui/lister_achats.html'
    context_object_name = 'achats'
    def get_queryset(self):
        search_query = self.request.GET.get('search', '')
        if search_query:
            query = Q()
            keywords = search_query.split()
            for keyword in keywords:
                query |= Q(personne__nom__icontains=keyword) | \
                         Q(personne__prenom__icontains=keyword) | \
                         Q(livre__titre__icontains=keyword) | \
                         Q(id__icontains=keyword)
            return Achat.objects.filter(query).distinct()
        return Achat.objects.all()
@login_required(login_url='login')
def saisir_ID_achat(request):
    if request.method == 'POST':
        form = IDAchatForm(request.POST)
        if form.is_valid():
            achat_id = form.cleaned_data['achat_id']

            if Achat.objects.filter(id=achat_id).exists():
                return redirect(reverse('achats_update', kwargs={'pk': achat_id}))
            else:
                return render(request, 'gui/saisir_achat_ID.html',
                              {'form': form, 'error': 'Achat non trouvé.'})
    else:
        form = IDAchatForm()
    return render(request, 'gui/saisir_achat_ID.html', {'form': form})

#%%------------------------------GERER-LES-COMMANDES---------------------------------
class CommanderList(StaffRequiredMixin, ListView):
    model = Commander
    template_name = 'gui/lister_commandes.html'
    context_object_name = 'commandes'
    def get_queryset(self):
        # Récupérer les paramètres GET
        sort_by = self.request.GET.get('sort_by', 'date_commande')  # Par défaut : tri par date_commande
        order = self.request.GET.get('order', 'asc')  # Par défaut : ordre ascendant
        sort_prefix = '' if order == 'asc' else '-'
        sorting_options = {
            'id':'id',
            'date':'date_commande',
            'quantite':'quantite',
        }
        # Récupérer le queryset initial
        queryset = super().get_queryset()
        # Appliquer le tri si valide, sinon fallback au tri par 'nom'
        if sort_by in sorting_options:
            queryset = queryset.order_by(f"{sort_prefix}{sorting_options[sort_by]}")
        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Récupérer les commandes en cours et terminées
        commandes_en_cours = Commander.objects.filter(statut='en cours')
        commandes_terminees = Commander.objects.filter(statut='terminé')
        # Appliquer le tri si un paramètre de tri est défini
        sort_by = self.request.GET.get('sort_by', 'date_commande')
        order = self.request.GET.get('order', 'asc')
        sort_prefix = '' if order == 'asc' else '-'
        commandes_en_cours = commandes_en_cours.order_by(f"{sort_prefix}{sort_by}")
        commandes_terminees = commandes_terminees.order_by(f"{sort_prefix}{sort_by}")
        context['commandes_en_cours'] = commandes_en_cours
        context['commandes_terminees'] = commandes_terminees
        return context
class CommanderCreate(StaffRequiredMixin,CreateView):
    model = Commander
    form_class = CommanderForm
    template_name = 'gui/ajouter_commande.html'
    success_url = reverse_lazy('commandes_list')
class CommanderUpdate(StaffRequiredMixin, UpdateView):
    model = Commander
    form_class = CommanderForm
    template_name = 'gui/modifier_commandes.html'
    success_url = reverse_lazy('commandes_list')
    def get_object(self):
        return get_object_or_404(Commander, pk=self.kwargs['pk'])
class CommanderDelete(StaffRequiredMixin, View):
    template_name = 'gui/supprimer_commande.html'
    def get(self, request, pk=None):
        """
        Si un `pk` est fourni, pré-remplit le formulaire avec l'ID de la commande.
        Sinon, affiche un formulaire vide pour que l'utilisateur entre l'ID manuellement.
        """
        commande = None
        if pk:
            # Si un ID de commande est dans l'URL, on le charge pour affichage
            commande = get_object_or_404(Commander, pk=pk)
        return render(request, self.template_name, {'commande': commande})
    def post(self, request, pk=None):
        """
        Supprime une commande :
        - Si un `pk` est fourni dans l'URL, on supprime directement la commande.
        - Sinon, on récupère l'ID envoyé dans le formulaire et on redirige pour confirmer la suppression.
        """
        commande_id = pk or request.POST.get('commande_id')
        if commande_id:
            # Si un ID est fourni, on cherche la commande correspondante
            try:
                commande = Commander.objects.get(id=commande_id)
                if pk:
                    # Si on est dans la page de confirmation, on supprime la commande directement
                    commande.delete()
                    return redirect(reverse_lazy('commandes_list'))  # Redirection après suppression
                else:
                    # Si on est dans le formulaire de saisie de l'ID, on redirige vers la confirmation
                    return redirect(reverse_lazy('commandes_with_ID_delete', kwargs={'pk': commande.id}))
            except Commander.DoesNotExist:
                # Si la commande n'existe pas avec l'ID donné
                return render(request, self.template_name, {'error': "Commande non trouvée."})
        return render(request, self.template_name, {'error': "ID de commande invalide."})
class CommanderResearch(ListView):
    model = Commander
    template_name = 'gui/lister_commandes.html'
    context_object_name = 'commandes'

    def get_queryset(self):
        # Récupérer les paramètres de recherche et de tri
        search_query = self.request.GET.get('search', '')
        sort_by = self.request.GET.get('sort_by', 'date_commande')
        order = self.request.GET.get('order', 'asc')
        sort_prefix = '' if order == 'asc' else '-'

        # Définir la recherche de manière générique pour tous les cas
        query = Q()

        if search_query:
            keywords = search_query.split()
            for keyword in keywords:
                # Recherche sur les champs de Commander
                query |= Q(statut__icontains=keyword) | \
                         Q(date_commande__icontains=keyword) | \
                         Q(quantite__icontains=keyword) |\
                         Q(id__icontains=keyword)

                # Recherche sur les relations ForeignKey : Personne, Livre, Fournisseur
                query |= Q(personne__nom__icontains=keyword)  # Personne liée
                query |= Q(personne__prenom__icontains=keyword)  # Prenom de la personne
                query |= Q(livre__titre__icontains=keyword)  # Livre lié
                query |= Q(fournisseur__nom_fournisseur__icontains=keyword)  # Fournisseur lié

        # Filtrer les commandes selon le statut et la recherche
        commandes_en_cours = Commander.objects.filter(statut='en cours').filter(query)
        commandes_terminees = Commander.objects.filter(statut='terminé').filter(query)

        # Appliquer le tri
        commandes_en_cours = commandes_en_cours.order_by(f"{sort_prefix}{sort_by}")
        commandes_terminees = commandes_terminees.order_by(f"{sort_prefix}{sort_by}")

        return commandes_en_cours, commandes_terminees

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Récupérer les commandes en cours et terminées avec recherche et tri
        commandes_en_cours, commandes_terminees = self.get_queryset()

        # Ajouter les commandes au contexte
        context['commandes_en_cours'] = commandes_en_cours
        context['commandes_terminees'] = commandes_terminees
        return context
@login_required(login_url='login')
def terminer_commande(request, pk):
    if not request.user.is_staff:  # Vérifie que l'utilisateur est autorisé
        return HttpResponseForbidden("Vous n'avez pas la permission de faire cette action.")

    # Récupérer la commande
    commande = get_object_or_404(Commander, pk=pk)
    if commande.statut == 'en cours':
        # Mettre à jour le statut de la commande
        commande.statut = 'terminé'
        commande.save()

        # Vérifier si le livre est dans la table Reserver
        reservations = Reserver.objects.filter(livre=commande.livre, statut='en cours')
        for reservation in reservations:
            # Créer une nouvelle notification de type 'commande'
            Notifier.objects.create(
                personne=reservation.personne,
                livre=commande.livre,
                quantite=commande.quantite,  # Assurez-vous que `quantite` correspond bien à la commande
                type='commande',
                commentaire=f"Le livre '{commande.livre.titre}' réservé est maintenant disponible suite à une commande terminée.",
                date_creation=timezone.now(),
            )

    return redirect('commandes_list')
@login_required(login_url='login')
def saisir_ID_commande(request):
    if request.method == 'POST':
        form = IDCommandeForm(request.POST)
        if form.is_valid():
            commande_id = form.cleaned_data['commande_id']

            if Commander.objects.filter(id=commande_id).exists():
                return redirect(reverse('commandes_update', kwargs={'pk': commande_id}))
            else:
                return render(request, 'gui/saisir_commande_ID.html',
                              {'form': form, 'error': 'Commande non trouvé.'})
    else:
        form = IDCommandeForm()
    return render(request, 'gui/saisir_commande_ID.html', {'form': form})

#%%------------------------------GERER-LES-RESERVATIONS------------------------------
class ReserverList(StaffRequiredMixin, ListView):
    model = Reserver
    template_name = 'gui/lister_reservations.html'
    context_object_name = 'reservations'

    def get_queryset(self):
        # Récupérer les paramètres GET pour le tri
        sort_by = self.request.GET.get('sort_by', 'date_reservation')  # Par défaut : tri par date_reservation
        order = self.request.GET.get('order', 'asc')  # Par défaut : ordre ascendant
        sort_prefix = '' if order == 'asc' else '-'
        sorting_options = {
            'id': 'id_commande',
            'date': 'date_commande',
            'quantite': 'quantite',
            'statut': 'statut',
        }
        # Récupérer le queryset initial
        queryset = super().get_queryset()
        # Appliquer le tri si valide, sinon fallback au tri par 'nom'
        if sort_by in sorting_options:
            queryset = queryset.order_by(f"{sort_prefix}{sorting_options[sort_by]}")
        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Récupérer les commandes en cours et terminées
        reservations_en_cours = Reserver.objects.filter(statut='en cours')
        reservations_terminees = Reserver.objects.filter(statut='terminé')
        # Appliquer le tri si un paramètre de tri est défini
        sort_by = self.request.GET.get('sort_by', 'date_reservation')
        order = self.request.GET.get('order', 'asc')
        sort_prefix = '' if order == 'asc' else '-'
        reservations_en_cours = reservations_en_cours.order_by(f"{sort_prefix}{sort_by}")
        reservations_terminees = reservations_terminees.order_by(f"{sort_prefix}{sort_by}")
        context['reservations_en_cours'] = reservations_en_cours
        context['reservations_terminees'] = reservations_terminees
        return context
class ReserverCreate(StaffRequiredMixin, CreateView):
    model = Reserver
    form_class = ReserverForm  # Formulaire à créer pour Reserver
    template_name = 'gui/ajouter_reservation.html'
    success_url = reverse_lazy('reservations_list')
class ReserverUpdate(StaffRequiredMixin, UpdateView):
    model = Reserver
    form_class = ReserverForm  # Formulaire à créer pour Reserver
    template_name = 'gui/modifier_reservations.html'
    success_url = reverse_lazy('reservations_list')

    def get_object(self):
        return get_object_or_404(Reserver, pk=self.kwargs['pk'])
class ReserverDelete(StaffRequiredMixin, View):
    template_name = 'gui/supprimer_reservation.html'
    def get(self, request, pk=None):
        """
        Si un `pk` est fourni, pré-remplit le formulaire avec l'ID de la commande.
        Sinon, affiche un formulaire vide pour que l'utilisateur entre l'ID manuellement.
        """
        reservation = None
        if pk:
            # Si un ID de commande est dans l'URL, on le charge pour affichage
            reservation = get_object_or_404(Reserver, pk=pk)
        return render(request, self.template_name, {'reservation': reservation})
    def post(self, request, pk=None):
        """
        Supprime une commande :
        - Si un `pk` est fourni dans l'URL, on supprime directement la commande.
        - Sinon, on récupère l'ID envoyé dans le formulaire et on redirige pour confirmer la suppression.
        """
        reservation_id = pk or request.POST.get('reservation_id')
        if reservation_id:
            # Si un ID est fourni, on cherche la commande correspondante
            try:
                reservation = Reserver.objects.get(id=reservation_id)
                if pk:
                    # Si on est dans la page de confirmation, on supprime la commande directement
                    reservation.delete()
                    return redirect(reverse_lazy('reservations_list'))  # Redirection après suppression
                else:
                    # Si on est dans le formulaire de saisie de l'ID, on redirige vers la confirmation
                    return redirect(reverse_lazy('reservations_with_ID_delete', kwargs={'pk': reservation.id}))
            except Reserver.DoesNotExist:
                # Si la commande n'existe pas avec l'ID donné
                return render(request, self.template_name, {'error': "Reservation non trouvée."})
        return render(request, self.template_name, {'error': "ID de reservation invalide."})
class ReserverResearch(ListView):
    model = Reserver
    template_name = 'gui/lister_reservations.html'
    context_object_name = 'reservations'

    def get_queryset(self):
        # Récupérer les paramètres de recherche et de tri
        search_query = self.request.GET.get('search', '')
        sort_by = self.request.GET.get('sort_by', 'date_reservation')
        order = self.request.GET.get('order', 'asc')
        sort_prefix = '' if order == 'asc' else '-'

        # Définir la recherche de manière générique pour tous les cas
        query = Q()

        if search_query:
            keywords = search_query.split()
            for keyword in keywords:
                # Recherche sur les champs de Reserver
                query |= Q(statut__icontains=keyword) | \
                         Q(date_reservation__icontains=keyword) | \
                         Q(id__icontains=keyword)

                # Recherche sur les relations ForeignKey : Personne, Livre
                query |= Q(personne__nom__icontains=keyword)  # Personne liée
                query |= Q(personne__prenom__icontains=keyword)  # Prenom de la personne
                query |= Q(livre__titre__icontains=keyword)  # Livre lié

        # Filtrer les réservations selon le statut et la recherche
        reservations_en_cours = Reserver.objects.filter(statut='en cours').filter(query)
        reservations_terminees = Reserver.objects.filter(statut='terminé').filter(query)

        # Appliquer le tri
        reservations_en_cours = reservations_en_cours.order_by(f"{sort_prefix}{sort_by}")
        reservations_terminees = reservations_terminees.order_by(f"{sort_prefix}{sort_by}")

        return reservations_en_cours, reservations_terminees

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Récupérer les réservations en cours et terminées avec recherche et tri
        reservations_en_cours, reservations_terminees = self.get_queryset()

        # Ajouter les réservations au contexte
        context['reservations_en_cours'] = reservations_en_cours
        context['reservations_terminees'] = reservations_terminees
        return context
@login_required(login_url='login')
def terminer_reservation(request, pk):
    if not request.user.is_staff:  # Vérifie que l'utilisateur est autorisé
        return HttpResponseForbidden("Vous n'avez pas la permission d'effectuer cette action.")
    reservation = get_object_or_404(Reserver, pk=pk)
    if reservation.statut == 'en cours':
        reservation.statut = 'terminé'
        reservation.save()

    return redirect('reservations_list')
@login_required(login_url='login')
def saisir_ID_reservation(request):
    if request.method == 'POST':
        form = IDReservationForm(request.POST)
        if form.is_valid():
            reservation_id = form.cleaned_data['reservation_id']

            if Reserver.objects.filter(id=reservation_id).exists():
                return redirect(reverse('reservations_update', kwargs={'pk': reservation_id}))
            else:
                return render(request, 'gui/saisir_reservation_ID.html',
                              {'form': form, 'error': 'Reservation non trouvé.'})
    else:
        form = IDReservationForm()
    return render(request, 'gui/saisir_reservation_ID.html', {'form': form})

#%%------------------------------GERER-LES-NOTIFICATIONS-----------------------------

class NotificationList(StaffRequiredMixin, TemplateView):
    model = Notifier
    template_name = 'gui/lister_notifications.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notifications_commande'] = Notifier.objects.filter(type='commande')
        context['notifications_quantite_min'] = Notifier.objects.filter(type='quantite_min')
        context['notifications_reservation'] = Notifier.objects.filter(type='reservation')
        return context

#class NotificationDelete(StaffRequiredMixin, View):
def check_reservations(request):
    if request.method == "POST":
        # Calculer la date limite
        date_limite = timezone.now().date() - timezone.timedelta(weeks=3)

        # Filtrer les réservations en cours dépassées
        reservations_depassees = Reserver.objects.filter(
            date_reservation__lt=date_limite,
            statut='en cours'
        )
        # Créer les notifications
        for reservation in reservations_depassees:
            # Vérifier si une notification similaire existe déjà
            existe = Notifier.objects.filter(
                personne=reservation.personne,
                livre=reservation.livre,
                quantite=reservation.quantite,
                type='reservation',
                commentaire=f"Réservation de {reservation.livre.titre} dépassée depuis plus de 3 semaines.",
                termine=False,
            ).exists()

            if not existe:
                notification = Notifier.objects.create(
                    personne=reservation.personne,
                    livre=reservation.livre,
                    quantite=reservation.quantite,
                    type='reservation',
                    commentaire=f"Réservation de {reservation.livre.titre} dépassée depuis plus de 3 semaines.",
                    termine=False,
                )

        # Rediriger vers la liste des notifications
        return redirect('notifications_list')

    # Rediriger si la méthode n'est pas POST
    return redirect('notifications_list')


def mark_notification_done(request, notification_id):
    if request.method == 'POST':
        # Récupérer la notification
        notification = get_object_or_404(Notifier, id=notification_id)

        # Marquer la notification comme terminée
        notification.termine = True
        notification.save()

        # Vérifier si la notification est liée à une réservation
        if notification.type == 'reservation' and notification.personne and notification.livre:
            # Rechercher la réservation correspondante
            reservation = Reserver.objects.filter(
                personne=notification.personne,
                livre=notification.livre,
                statut='en cours'
            ).first()

            if reservation:
                # Mettre à jour le statut de la réservation
                reservation.statut = 'terminé'
                reservation.save()

        return redirect('notifications_list')
def delete_notification(request, notification_id):
    if request.method == 'POST':
        notification = get_object_or_404(Notifier, id=notification_id)
        notification.delete()
        return redirect('notifications_list')
