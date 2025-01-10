from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required  # accès aux pages seulement si login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.db.models import Q, Prefetch
from django.http import HttpResponseRedirect, \
    HttpResponseForbidden  # rediriger vers une autre url, refuser l'accès à une url
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import ListView, CreateView, DeleteView, UpdateView, View, TemplateView

from gui.models import Role, Ville, Adresse, Personne, Fournisseur, FournisseurAdresse, Editeur, Contributeur, Livre, \
    Achat, Commander, Reserver, Notifier
from .decorators import unauthenticated_user_required, staff_required
from .forms import (VilleForm, AdresseForm, PersonneForm, EmailInputForm, FournisseurForm,
                    IDFournisseurForm, FournisseurAdresseFormSet, \
                    EditeurForm, IDEditeurForm, ContributeurForm, IDContributeurForm, LivreForm, ISBNForm, AchatForm,
                    AchatUpdateForm, IDAchatForm, ReserverUpdateForm, ReserverForm, IDReservationForm, CommanderForm,
                    IDCommandeForm,
                    CommanderUpdateForm)
from django.core.paginator import Paginator


#%%------------------------------LOGIN/LOGOUT----------------------------------------
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
#%%------------------------------HOMEPAGE--------------------------------------------
@login_required(login_url='login')
def home(request):
    return render(request, 'gui/homepage.html')
@login_required(login_url='login')
def autres(request):
    return render(request, 'gui/autres.html')
#%%------------------------------PERMISSIONS-----------------------------------------
class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = 'login'
    def test_func(self):

        return self.request.user.is_staff
#%%------------------------------GERER-LES-ROLES-------------------------------------
class RoleList(StaffRequiredMixin,ListView):
    model = Role
    template_name = 'gui/lister_roles.html'
class RoleCreate(StaffRequiredMixin,CreateView):
    model = Role
    fields = ['type']
    template_name = 'gui/ajouter_role.html'
    success_url = reverse_lazy('roles_list')
#%%------------------------------GERER-LES-VILLES------------------------------------
class VilleList(StaffRequiredMixin,ListView):
    model = Ville
    template_name = 'gui/lister_villes.html'
class VilleCreate(StaffRequiredMixin,CreateView):
    model = Ville
    fields = ['nom_ville', 'code_postal', 'pays']
    template_name = 'gui/ajouter_ville.html'
    success_url = reverse_lazy('villes_list')
def ville_create(request):
    if request.method == 'POST':

        form_ville = VilleForm(request.POST)

        if form_ville.is_valid():
            nom_ville = form_ville.cleaned_data['nom_ville']
            code_postal = form_ville.cleaned_data['code_postal']
            pays = form_ville.cleaned_data['pays']


            ville_existante = Ville.objects.filter(nom_ville=nom_ville, code_postal=code_postal).first()

            if not ville_existante:

                ville = form_ville.save()
            else:

                ville = ville_existante
            return redirect('villes_list')

    else:
        form_ville = VilleForm()



    return render(request, 'gui/ajouter_ville.html', {
        'form_ville': form_ville
    })

class VilleUpdate(StaffRequiredMixin, UpdateView):
    model = Ville
    fields = ['nom_ville', 'code_postal', 'pays']
    template_name = 'gui/modifier_ville.html'
    success_url = reverse_lazy('villes_list')


class VilleDelete(StaffRequiredMixin, DeleteView):
    model = Ville
    template_name = 'gui/supprimer_ville.html'
    success_url = reverse_lazy('villes_list')
#%%------------------------------GERER-LES-ADRESSES----------------------------------
from django.db.models import Q

class AdresseList(StaffRequiredMixin, ListView):
    model = Adresse
    template_name = 'gui/lister_adresses.html'
    paginate_by = 10

    def get_queryset(self):
        sort_by = self.request.GET.get('sort_by', 'id')
        order = self.request.GET.get('order', 'asc')

        sort_prefix = '' if order == 'asc' else '-'

        sorting_options = {
            'id': 'id',
            'rue': 'rue',
            'n_rue': 'n_rue',
            'ville': 'ville',
            'ville_code_postal': 'ville__code_postal',
            'ville_pays': 'ville__pays',
        }

        # Récupération du queryset de base
        queryset = super().get_queryset()

        # Application du tri seulement
        if sort_by in sorting_options:
            queryset = queryset.order_by(f"{sort_prefix}{sorting_options[sort_by]}")

        return queryset

@login_required(login_url='login')
def create_adresse(request):
    if request.method == 'POST':
        adresse_form = AdresseForm(request.POST)

        if adresse_form.is_valid():

            rue = adresse_form.cleaned_data['rue']
            n_rue = adresse_form.cleaned_data['n_rue']


            nom_ville = request.POST.get('nom_ville')
            code_postal = request.POST.get('code_postal')
            pays = request.POST.get('pays')

            if nom_ville and code_postal and pays:

                ville, created = Ville.objects.get_or_create(
                    nom_ville=nom_ville,
                    defaults={
                        'code_postal': code_postal,
                        'pays': pays
                    }
                )


                if Adresse.objects.filter(rue=rue, n_rue=n_rue, ville=ville).exists():
                    adresse_form.add_error(None, "Cette adresse existe déjà.")
                else:

                    adresse = adresse_form.save(commit=False)
                    adresse.ville = ville
                    adresse.save()

                    return redirect('adresses_list')
            else:

                adresse_form.add_error(None, "Veuillez remplir les informations de la ville.")
    else:
        adresse_form = AdresseForm()

    return render(request, 'gui/ajouter_adresse.html', {
        'adresse_form': adresse_form,
    })
class AdresseResearch(StaffRequiredMixin, ListView):
    model = Adresse
    template_name = 'gui/lister_adresses.html'

    def get_queryset(self):
        sort_by = self.request.GET.get('sort_by', 'id')
        order = self.request.GET.get('order', 'asc')
        search_query = self.request.GET.get('search', '').strip()

        sort_prefix = '' if order == 'asc' else '-'
        sorting_options = {
            'id': 'id',
            'rue': 'rue',
            'n_rue': 'n_rue',
            'ville': 'ville',
            'ville_code_postal': 'ville__code_postal',
            'ville_pays': 'ville__pays',
        }

        queryset = super().get_queryset()

        # --- Filtrage ---
        if search_query:
            # On coupe la chaîne en mots
            words = search_query.split()
            for word in words:

                queryset = queryset.filter(
                    Q(rue__icontains=word) |
                    Q(n_rue__icontains=word)
                )


        if sort_by in sorting_options:
            queryset = queryset.order_by(f"{sort_prefix}{sorting_options[sort_by]}")

        return queryset
class AdresseDelete(StaffRequiredMixin, View):
    template_name = 'gui/supprimer_adresse.html'

    def get(self, request):

        return render(request, self.template_name)

    def post(self, request):

        adresse_id = request.POST.get('adresse_id')
        if adresse_id:

            adresse = get_object_or_404(Adresse, id=adresse_id)

            adresse.delete()

            return redirect(reverse_lazy('adresses_list'))

        return render(request, self.template_name, {'error': 'Adresse invalide.'})
#%%------------------------------GERER-LES-PERSONNES---------------------------------
class PersonneList(StaffRequiredMixin, ListView):
    model = Personne
    template_name = 'gui/lister_personnes.html'
    context_object_name = 'personnes'  # Optionnel : pour un accès plus clair dans le template
    paginate_by = 10
    def get_queryset(self):
        # Récupération des paramètres GET
        sort_by = self.request.GET.get('sort_by', 'nom')
        order = self.request.GET.get('order', 'asc')
        search_query = self.request.GET.get('q', '').strip()

        # Détermination du préfixe de tri
        sort_prefix = '' if order == 'asc' else '-'

        # Options de tri autorisées
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

        # Obtention du queryset de base
        queryset = super().get_queryset()

        # Application du filtre de recherche si une requête est présente
        if search_query:
            queryset = queryset.filter(
                Q(nom__icontains=search_query) |
                Q(prenom__icontains=search_query)
            )

        # Application du tri si l'option est valide
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

            nom_ville = form_ville.cleaned_data['nom_ville']
            code_postal = form_ville.cleaned_data['code_postal']
            pays = form_ville.cleaned_data['pays']

            ville, created = Ville.objects.get_or_create(
                nom_ville=nom_ville,
                code_postal=code_postal,
                pays=pays
            )


            rue = form_adresse.cleaned_data['rue']
            n_rue = form_adresse.cleaned_data['n_rue']

            adresse, created = Adresse.objects.get_or_create(
                rue=rue,
                n_rue=n_rue,
                ville=ville
            )


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


            email = form_personne.cleaned_data['email']
            password = form_personne.cleaned_data['password']

            if Personne.objects.filter(email=email).exists():
                form_personne.add_error('email', 'Cet email est déjà utilisé.')
                return render(request, 'gui/ajouter_personne.html', {
                    'form_personne': form_personne,
                    'form_adresse': form_adresse,
                    'form_ville': form_ville
                })


            nom = form_personne.cleaned_data['nom']
            prenom = form_personne.cleaned_data['prenom']
            date_naissance = form_personne.cleaned_data['date_naissance']
            telephone = form_personne.cleaned_data['telephone']
            solde = form_personne.cleaned_data['solde']


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

            keywords = search_query.split()
            query = Q()

            for keyword in keywords:

                query |= Q(nom__icontains=keyword) | \
                         Q(prenom__icontains=keyword) | \
                         Q(date_naissance__icontains=keyword) | \
                         Q(email__icontains=keyword) | \
                         Q(date_creation__icontains=keyword) | \
                         Q(adresse__ville__nom_ville__icontains=keyword)


            return Personne.objects.filter(query).distinct()


        return Personne.objects.all()
class PersonneDelete(StaffRequiredMixin, View):
    template_name = 'gui/supprimer_personne.html'

    def get(self, request):

        return render(request, self.template_name)

    def post(self, request):

        personne_email = request.POST.get('personne_email')
        if personne_email:

            personne = get_object_or_404(Personne, email=personne_email)

            if not request.user.is_superuser:
                roles_interdits = ['employe', 'admin']
                if personne.role.type in roles_interdits:
                    return HttpResponseForbidden(
                        "Vous n'êtes pas autorisé à supprimer cet utilisateur."
                    )

            personne.delete()

            return redirect(reverse_lazy('personnes_list'))

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

            personne = get_object_or_404(Personne, email=email)

            if not request.user.is_superuser:

                roles_interdits = ['employe', 'admin']
                if personne.role.type in roles_interdits:
                    return HttpResponseForbidden("Vous n'êtes pas autorisé à modifier cet utilisateur.")

            return redirect(reverse('personnes_update', args=[email]))
        else:
            messages.error(request, 'Veuillez saisir un email valide.')
            return render(request, self.template_name, {'form': form})
class PersonneUpdate(StaffRequiredMixin, View):
    template_name = 'gui/modifier_personnes.html'

    def get(self, request, email):
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
        personne = get_object_or_404(Personne, email=email)
        adresse_initiale = personne.adresse
        ville_initiale = adresse_initiale.ville if adresse_initiale.ville else None

        personne_form = PersonneForm(request.POST, instance=personne, user=request.user)
        adresse_form = AdresseForm(request.POST)
        ville_form = VilleForm(request.POST)

        if personne_form.is_valid() and adresse_form.is_valid() and ville_form.is_valid():
            with transaction.atomic():

                ville_data = ville_form.cleaned_data
                nom_ville = ville_data.get('nom_ville')
                code_postal = ville_data.get('code_postal')
                pays = ville_data.get('pays')

                if nom_ville and code_postal and pays:
                    ville_obj, _ = Ville.objects.get_or_create(
                        nom_ville=nom_ville,
                        code_postal=code_postal,
                        pays=pays
                    )
                else:
                    ville_obj = None

                adresse_data = adresse_form.cleaned_data
                rue = adresse_data.get('rue')
                n_rue = adresse_data.get('n_rue')

                adresse_modifiee = (
                    (rue != adresse_initiale.rue) or
                    (n_rue != adresse_initiale.n_rue) or
                    (ville_obj != ville_initiale)
                )

                adresse_partagee = Adresse.objects.filter(pk=adresse_initiale.pk).exclude(personne=personne).exists()

                if adresse_partagee or adresse_modifiee:

                    nouvelle_adresse, _ = Adresse.objects.get_or_create(
                        rue=rue,
                        n_rue=n_rue,
                        ville=ville_obj
                    )
                    personne.adresse = nouvelle_adresse
                else:

                    pass

                personne_form.save()

            messages.success(request, 'La personne, son adresse et sa ville ont été mises à jour avec succès.')
            return redirect(reverse_lazy('personnes_list'))

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
            # 'ville': 'adresses__ville__nom_ville',
        }

        queryset = super().get_queryset()

        if search_query:
            queryset = queryset.filter(
                Q(nom_fournisseur__icontains=search_query) |
                Q(adresses__ville__nom_ville__icontains=search_query)
            ).distinct()

        if sort_by in sorting_options:
            queryset = queryset.order_by(f"{sort_prefix}{sorting_options[sort_by]}")
        else:
            queryset = queryset.order_by('nom_fournisseur')

        return queryset.prefetch_related('adresses', 'adresses__ville')
def fournisseur_create(request):
    if request.method == 'POST':
        form_fournisseur = FournisseurForm(request.POST)
        formset_adresse = FournisseurAdresseFormSet(request.POST)

        if form_fournisseur.is_valid() and formset_adresse.is_valid():
            fournisseur = form_fournisseur.save()

            for form in formset_adresse:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    adresse = form.cleaned_data['adresse']

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

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

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
class EditeurList(ListView):
    model = Editeur
    template_name = 'gui/lister_editeurs.html'

    def get_queryset(self):
        sort_by = self.request.GET.get('sort_by', 'id')
        order = self.request.GET.get('order', 'asc')

        sort_prefix = '' if order == 'asc' else '-'

        sorting_options = {
            'id' : 'id',
            'nom': 'nom'
        }

        queryset = super().get_queryset()

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
        return render(request, self.template_name)

    def post(self, request):
        editeur_id = request.POST.get('editeur_id')
        if editeur_id:
            editeur = get_object_or_404(Editeur, pk=editeur_id)

            editeur.delete()

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
            return redirect('editeurs_list')

        return render(request, self.template_name, {'form': form, 'editeur': editeur})

class EditeurResearch(StaffRequiredMixin,ListView):
    model = Editeur
    template_name = 'gui/lister_editeurs.html'

    def get_queryset(self):
        search_query = self.request.GET.get('search', '')

        if search_query:
            return Editeur.objects.filter(nom__icontains=search_query).distinct()

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

#%%------------------------------GERER-LES-CONTRIBUTEURS-----------------------------
class ContributeurList(StaffRequiredMixin,ListView):
    model = Contributeur
    template_name = 'gui/lister_contributeurs.html'
    paginate_by = 5
    def get_queryset(self):
        sort_by = self.request.GET.get('sort_by', 'id')
        order = self.request.GET.get('order', 'asc')

        sort_prefix = '' if order == 'asc' else '-'

        sorting_options = {
            'id':'id',
            'nom': 'nom',
            'prenom': 'prenom',
        }

        queryset = super().get_queryset()

        if sort_by in sorting_options:
            queryset = queryset.order_by(f"{sort_prefix}{sorting_options[sort_by]}")

        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Filtrer par type
        auteurs = Contributeur.objects.filter(type='Auteur')
        traducteurs = Contributeur.objects.filter(type='Traducteur')
        illustrateurs = Contributeur.objects.filter(type='Illustrateur')

        # Pagination pour chaque groupe
        paginator_auteurs = Paginator(auteurs, self.paginate_by)
        paginator_traducteurs = Paginator(traducteurs, self.paginate_by)
        paginator_illustrateurs = Paginator(illustrateurs, self.paginate_by)

        # Récupérer la page spécifique pour chaque groupe
        page_auteurs = self.request.GET.get('page_auteurs', 1)  # Par défaut page 1
        page_traducteurs = self.request.GET.get('page_traducteurs', 1)
        page_illustrateurs = self.request.GET.get('page_illustrateurs', 1)

        # Appliquer la pagination à chaque groupe
        context['auteurs'] = paginator_auteurs.get_page(page_auteurs)
        context['traducteurs'] = paginator_traducteurs.get_page(page_traducteurs)
        context['illustrateurs'] = paginator_illustrateurs.get_page(page_illustrateurs)

        return context
class ContributeurCreate(StaffRequiredMixin,CreateView):
    model = Contributeur
    form_class = ContributeurForm
    template_name = 'gui/ajouter_contributeur.html'
    success_url = reverse_lazy('contributeurs_list')
    def form_valid(self, form):
        response = super().form_valid(form)



        return response
class ContributeurDelete(StaffRequiredMixin,View):
    template_name = 'gui/supprimer_contributeur.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        contributeur_id = request.POST.get('contributeur_id')
        if contributeur_id:
            contributeur = get_object_or_404(Contributeur, pk=contributeur_id)
            contributeur.delete()
            return redirect(reverse_lazy('contributeurs_list'))
        return render(request, self.template_name, {'error': "ID du contributeur invalide."})
class ContributeurUpdate(StaffRequiredMixin, UpdateView):
    model = Contributeur
    form_class = ContributeurForm
    template_name = 'gui/modifier_contributeur.html'
    pk_url_kwarg = 'pk'

    def form_valid(self, form):
        form.save()
        return redirect('contributeurs_list')

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))
class ContributeurResearch(ListView):
    model = Contributeur
    template_name = 'gui/lister_contributeurs.html'
    context_object_name = 'contributeurs'

    def get_queryset(self):

        search_query = self.request.GET.get('search', '')
        sort_by = self.request.GET.get('sort_by', 'nom')
        order = self.request.GET.get('order', 'asc')
        sort_prefix = '' if order == 'asc' else '-'

        query = Q()

        if search_query:
            keywords = search_query.split()
            for keyword in keywords:
                query |= Q(nom__icontains=keyword) | \
                         Q(prenom__icontains=keyword) | \
                         Q(id__icontains=keyword)



        auteurs = Contributeur.objects.filter(type='Auteur').filter(query)
        traducteurs = Contributeur.objects.filter(type='Traducteur').filter(query)
        illustrateurs = Contributeur.objects.filter(type='Illustrateur').filter(query)

        auteurs = auteurs.order_by(f"{sort_prefix}{sort_by}")
        traducteurs = traducteurs.order_by(f"{sort_prefix}{sort_by}")
        illustrateurs = illustrateurs.order_by(f"{sort_prefix}{sort_by}")
        return auteurs, traducteurs, illustrateurs


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        auteurs, traducteurs, illustrateurs = self.get_queryset()

        context['auteurs'] = auteurs
        context['traducteurs'] = traducteurs
        context['illustrateurs'] = illustrateurs

        return context

@login_required(login_url='login')
def saisir_ID_contributeur(request):
    if request.method == 'POST':
        form = IDContributeurForm(request.POST)
        if form.is_valid():
            contributeur_id = form.cleaned_data['contributeur_id']

            if Contributeur.objects.filter(id=contributeur_id).exists():

                return redirect(reverse('contributeurs_update', kwargs={'pk': contributeur_id}))
            else:
                return render(request, 'gui/saisir_contributeur_ID.html', {'form': form, 'error': 'Contributeur non trouvé.'})
    else:
        form = IDContributeurForm()
    return render(request, 'gui/saisir_contributeur_ID.html', {'form': form})

#%%------------------------------GERER-LES-LIVRES------------------------------------
class LivreList(StaffRequiredMixin, ListView):
    model = Livre
    template_name = 'gui/lister_livres.html'

    def get_queryset(self):

        sort_by = self.request.GET.get('sort_by', 'titre')
        order = self.request.GET.get('order', 'asc')

        sort_prefix = '' if order == 'asc' else '-'

        sorting_options = {
            'isbn13': 'isbn13',
            'titre': 'titre',
            'auteur_nom': 'contributeurs__nom',
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

        queryset = super().get_queryset()

        contributeurs_prefetch = Prefetch(
            'contributeurs',
            queryset=Contributeur.objects.filter(type__in=['Auteur', 'Traducteur', 'Illustrateur']),
            to_attr='contributeurs_data'
        )
        queryset = queryset.prefetch_related(contributeurs_prefetch)

        if sort_by in sorting_options:
            queryset = queryset.order_by(f"{sort_prefix}{sorting_options[sort_by]}")



        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        for livre in context['object_list']:
            livre.auteurs = [c for c in livre.contributeurs.all() if c.type == 'Auteur']
            livre.traducteurs = [c for c in livre.contributeurs.all() if c.type == 'Traducteur']
            livre.illustrateurs = [c for c in livre.contributeurs.all() if c.type == 'Illustrateur']

        return context
@login_required(login_url='login')
def create_livre(request):
    if request.method == 'POST':
        livre_form = LivreForm(request.POST)

        if livre_form.is_valid():

            livre = livre_form.save()

            def ajouter_contributeurs(noms, prenoms, dates_naissance, type_contributeur):
                for nom, prenom, date_naissance in zip(noms, prenoms, dates_naissance):
                    if nom and prenom:
                        contributeur, created = Contributeur.objects.get_or_create(
                            nom=nom,
                            prenom=prenom,
                            date_naissance=date_naissance if date_naissance else None,
                            type=type_contributeur
                        )

                        livre.contributeurs.add(contributeur)

            noms_auteurs = request.POST.getlist('nom_auteur')
            prenoms_auteurs = request.POST.getlist('prenom_auteur')
            dates_naissance_auteurs = request.POST.getlist('date_naissance_auteur')
            ajouter_contributeurs(noms_auteurs, prenoms_auteurs, dates_naissance_auteurs, 'Auteur')

            noms_traducteurs = request.POST.getlist('nom_traducteur')
            prenoms_traducteurs = request.POST.getlist('prenom_traducteur')
            dates_naissance_traducteurs = request.POST.getlist('date_naissance_traducteur')
            ajouter_contributeurs(noms_traducteurs, prenoms_traducteurs, dates_naissance_traducteurs, 'Traducteur')

            noms_illustrateurs = request.POST.getlist('nom_illustrateur')
            prenoms_illustrateurs = request.POST.getlist('prenom_illustrateur')
            dates_naissance_illustrateurs = request.POST.getlist('date_naissance_illustrateur')
            ajouter_contributeurs(noms_illustrateurs, prenoms_illustrateurs, dates_naissance_illustrateurs, 'Illustrateur')

            return redirect('livres_list')

    else:
        livre_form = LivreForm()

    return render(request, 'gui/ajouter_livre.html', {
        'livre_form': livre_form,
    })

class LivreDelete(StaffRequiredMixin,View):
    template_name = 'gui/supprimer_livre.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        livre_id = request.POST.get('livre_id')
        if livre_id:
            livre = get_object_or_404(Livre, pk=livre_id)

            livre.delete()

            return redirect(reverse_lazy('livres_list'))
        return render(request, self.template_name, {'error': 'ID du livre invalide.'})


class LivreUpdate(StaffRequiredMixin, View):
    template_name = 'gui/modifier_livres.html'

    def get(self, request, isbn13):
        livre = get_object_or_404(Livre, isbn13=isbn13)

        auteurs_ex = livre.contributeurs.filter(type='Auteur')
        traducteurs_ex = livre.contributeurs.filter(type='Traducteur')
        illustrateurs_ex = livre.contributeurs.filter(type='Illustrateur')

        form = LivreForm(instance=livre)

        context = {
            'form': form,
            'livre': livre,
            'auteurs_ex': auteurs_ex,
            'traducteurs_ex': traducteurs_ex,
            'illustrateurs_ex': illustrateurs_ex,
        }

        return render(request, self.template_name, context)

    def post(self, request, isbn13):
        livre = get_object_or_404(Livre, isbn13=isbn13)
        form = LivreForm(request.POST, instance=livre)

        auteurs_ex = livre.contributeurs.filter(type='Auteur')
        traducteurs_ex = livre.contributeurs.filter(type='Traducteur')
        illustrateurs_ex = livre.contributeurs.filter(type='Illustrateur')

        if form.is_valid():
            livre = form.save()

            for a in auteurs_ex:
                if request.POST.get(f'delete_auteur_{a.id}', '') == 'on':
                    livre.contributeurs.remove(a)

            for t in traducteurs_ex:
                if request.POST.get(f'delete_traducteur_{t.id}', '') == 'on':
                    livre.contributeurs.remove(t)

            for i in illustrateurs_ex:
                if request.POST.get(f'delete_illustrateur_{i.id}', '') == 'on':
                    livre.contributeurs.remove(i)

            noms_auteurs = request.POST.getlist('nom_auteur')
            prenoms_auteurs = request.POST.getlist('prenom_auteur')
            dates_naissance_auteurs = request.POST.getlist('date_naissance_auteur')
            self.ajouter_contributeurs(livre, noms_auteurs, prenoms_auteurs, dates_naissance_auteurs, 'Auteur')

            noms_traducteurs = request.POST.getlist('nom_traducteur')
            prenoms_traducteurs = request.POST.getlist('prenom_traducteur')
            dates_naissance_traducteurs = request.POST.getlist('date_naissance_traducteur')
            self.ajouter_contributeurs(livre, noms_traducteurs, prenoms_traducteurs, dates_naissance_traducteurs,
                                       'Traducteur')

            noms_illustrateurs = request.POST.getlist('nom_illustrateur')
            prenoms_illustrateurs = request.POST.getlist('prenom_illustrateur')
            dates_naissance_illustrateurs = request.POST.getlist('date_naissance_illustrateur')
            self.ajouter_contributeurs(livre, noms_illustrateurs, prenoms_illustrateurs, dates_naissance_illustrateurs,
                                       'Illustrateur')

            return redirect('livres_list')

        context = {
            'form': form,
            'livre': livre,
            'auteurs_ex': auteurs_ex,
            'traducteurs_ex': traducteurs_ex,
            'illustrateurs_ex': illustrateurs_ex,
        }
        return render(request, self.template_name, context)

    def ajouter_contributeurs(self, livre, noms, prenoms, dates, type_contributeur):
        for nom, prenom, date_naissance in zip(noms, prenoms, dates):
            if nom and prenom:
                contributeur, created = Contributeur.objects.get_or_create(
                    nom=nom,
                    prenom=prenom,
                    date_naissance=date_naissance if date_naissance else None,
                    type=type_contributeur
                )
                livre.contributeurs.add(contributeur)


class LivreResearch(StaffRequiredMixin, ListView):
    model = Livre
    template_name = 'gui/lister_livres.html'

    def get_queryset(self):
        search_query = self.request.GET.get('search', '').strip()

        if search_query:

            keywords = search_query.split()
            query = Q()


            for keyword in keywords:
                query |= Q(titre__icontains=keyword) | Q(isbn13__icontains=keyword)


            livres = Livre.objects.filter(query).distinct().prefetch_related(
                Prefetch('contributeurs', queryset=Contributeur.objects.all())
            )
        else:

            livres = Livre.objects.all().prefetch_related(
                Prefetch('contributeurs', queryset=Contributeur.objects.all())
            )

        return livres

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        for livre in context['object_list']:
            livre.auteurs = [c for c in livre.contributeurs.all() if c.type == 'Auteur']
            livre.traducteurs = [c for c in livre.contributeurs.all() if c.type == 'Traducteur']
            livre.illustrateurs = [c for c in livre.contributeurs.all() if c.type == 'Illustrateur']

        return context
@login_required(login_url='login')
def saisir_isbn(request):
    if request.method == 'POST':
        form = ISBNForm(request.POST)
        if form.is_valid():
            isbn13 = form.cleaned_data['isbn13']

            if Livre.objects.filter(isbn13=isbn13).exists():
                return redirect(reverse('livre_update', kwargs={'isbn13': isbn13}))
            else:

                return render(request, 'gui/saisir_isbn.html', {'form': form, 'error': 'Livre non trouvé.'})
    else:
        form = ISBNForm()
    return render(request, 'gui/saisir_isbn.html', {'form': form})
#%%------------------------------GERER-LES-ACHATS------------------------------------
class AchatList(StaffRequiredMixin,ListView):
    model = Achat
    template_name = 'gui/lister_achats.html'
    context_object_name = 'achats'
    paginate_by = 10
    def get_queryset(self):
        sort_by = self.request.GET.get('sort_by', 'date_achat')
        order = self.request.GET.get('order', 'asc')
        sort_prefix = '' if order == 'asc' else '-'
        sorting_options = {
            'date': 'date_achat',
            'quantite': 'quantite',
        }
        queryset = super().get_queryset()

        if sort_by in sorting_options:
            queryset = queryset.order_by(f"{sort_prefix}{sorting_options[sort_by]}")
        return queryset
class AchatCreate(StaffRequiredMixin, CreateView):
    model = Achat
    form_class = AchatForm
    template_name = 'gui/ajouter_achat.html'
    success_url = reverse_lazy('achats_list')


    def form_valid(self, form):

        personne = form.cleaned_data['personne']
        date_achat = form.cleaned_data['date_achat']

        livres = self.request.POST.getlist('livres[]')
        quantites = self.request.POST.getlist('quantites[]')

        if not livres or not quantites:
            form.add_error(None, "Vous devez ajouter au moins un livre avec une quantité.")
            return self.form_invalid(form)

        try:
            with transaction.atomic():
                for isbn13, quantite in zip(livres, quantites):
                    if isbn13 and quantite:
                        quantite = int(quantite)
                        if quantite <= 0:
                            form.add_error(None, f"Quantité invalide pour le livre {isbn13}.")
                            return self.form_invalid(form)

                        try:
                            livre = Livre.objects.get(isbn13=isbn13)
                        except Livre.DoesNotExist:
                            form.add_error(None, f"Le livre avec l'ISBN {isbn13} n'existe pas.")
                            return self.form_invalid(form)

                        if quantite > livre.quantite_disponible:
                            form.add_error(
                                None,
                                f"Quantité demandée ({quantite}) pour le livre '{livre.titre}' dépasse le stock disponible ({livre.quantite_disponible})."
                            )
                            return self.form_invalid(form)

                        Achat.objects.create(
                            personne=personne,
                            livre=livre,
                            date_achat=date_achat,
                            quantite=int(quantite)
                        )

        except Exception as e:
            form.add_error(None, f"Erreur lors de l'enregistrement : {e}")
            return self.form_invalid(form)

        return HttpResponseRedirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['livres'] = Livre.objects.all()
        return context
class AchatUpdate(StaffRequiredMixin, UpdateView):
    model = Achat
    form_class = AchatUpdateForm
    template_name = 'gui/modifier_achat.html'
    success_url = reverse_lazy('achats_list')
    def get_object(self):
        return get_object_or_404(Achat, pk=self.kwargs['pk'])

    def form_valid(self, form):
        achat_instance = self.get_object()

        livre = achat_instance.livre
        ancienne_quantite = achat_instance.quantite

        nouvelle_quantite = form.cleaned_data['quantite']

        difference = nouvelle_quantite - ancienne_quantite

        livre.quantite_disponible -= difference
        if livre.quantite_disponible < 0:
            form.add_error('quantite', "Le stock est insuffisant pour cette quantité.")
            return self.form_invalid(form)

        livre.save()

        response = super().form_valid(form)

        return response
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
                    livre = achat.livre
                    quantite_achat = achat.quantite

                    livre.quantite_disponible += quantite_achat
                    livre.save()

                    achat.delete()
                    return redirect(reverse_lazy('achats_list'))
                else:
                    return redirect(reverse_lazy('achats_with_ID_delete', kwargs={'pk': achat_id}))



            except Achat.DoesNotExist:
                return render(request, self.template_name, {'error': "Achat non trouvé."})
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
        sort_by = self.request.GET.get('sort_by', 'date_commande')
        order = self.request.GET.get('order', 'asc')
        sort_prefix = '' if order == 'asc' else '-'
        sorting_options = {
            'id':'id',
            'date':'date_commande',
            'quantite':'quantite',
        }

        queryset = super().get_queryset()

        if sort_by in sorting_options:
            queryset = queryset.order_by(f"{sort_prefix}{sorting_options[sort_by]}")
        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        commandes_en_cours = Commander.objects.filter(statut='en cours')
        commandes_terminees = Commander.objects.filter(statut='terminé')

        sort_by = self.request.GET.get('sort_by', 'date_commande')
        order = self.request.GET.get('order', 'asc')
        sort_prefix = '' if order == 'asc' else '-'
        commandes_en_cours = commandes_en_cours.order_by(f"{sort_prefix}{sort_by}")
        commandes_terminees = commandes_terminees.order_by(f"{sort_prefix}{sort_by}")
        context['commandes_en_cours'] = commandes_en_cours
        context['commandes_terminees'] = commandes_terminees
        return context
class CommanderCreate(StaffRequiredMixin, CreateView):
    model = Commander
    form_class = CommanderForm
    template_name = 'gui/ajouter_commande.html'
    success_url = reverse_lazy('commandes_list')

    def form_valid(self, form):

        personne = form.cleaned_data['personne']
        date_commande = form.cleaned_data['date_commande']
        fournisseur = form.cleaned_data['fournisseur']
        statut = form.cleaned_data['statut']

        livres = self.request.POST.getlist('livres[]')
        quantites = self.request.POST.getlist('quantites[]')

        if not livres or not quantites:
            form.add_error(None, "Vous devez ajouter au moins un livre avec une quantité.")
            return self.form_invalid(form)

        try:
            with transaction.atomic():
                for isbn13, quantite in zip(livres, quantites):
                    if isbn13 and quantite:
                        quantite = int(quantite)
                        if quantite <= 0:
                            form.add_error(None, f"Quantité invalide pour le livre {isbn13}.")
                            return self.form_invalid(form)

                        try:
                            livre = Livre.objects.get(isbn13=isbn13)
                        except Livre.DoesNotExist:
                            form.add_error(None, f"Le livre avec l'ISBN {isbn13} n'existe pas.")
                            return self.form_invalid(form)

                        Commander.objects.create(
                            personne=personne,
                            livre=livre,
                            date_commande=date_commande,
                            quantite=quantite,
                            fournisseur=fournisseur,
                            statut=statut
                        )

        except Exception as e:
            form.add_error(None, f"Erreur lors de l'enregistrement : {e}")
            return self.form_invalid(form)

        return HttpResponseRedirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['livres'] = Livre.objects.all()
        return context
class CommanderUpdate(StaffRequiredMixin, UpdateView):
    model = Commander
    form_class = CommanderUpdateForm
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

            try:
                commande = Commander.objects.get(id=commande_id)
                if pk:

                    commande.delete()
                    return redirect(reverse_lazy('commandes_list'))
                else:

                    return redirect(reverse_lazy('commandes_with_ID_delete', kwargs={'pk': commande.id}))
            except Commander.DoesNotExist:

                return render(request, self.template_name, {'error': "Commande non trouvée."})
        return render(request, self.template_name, {'error': "ID de commande invalide."})
class CommanderResearch(ListView):
    model = Commander
    template_name = 'gui/lister_commandes.html'
    context_object_name = 'commandes'

    def get_queryset(self):

        search_query = self.request.GET.get('search', '')
        sort_by = self.request.GET.get('sort_by', 'date_commande')
        order = self.request.GET.get('order', 'asc')
        sort_prefix = '' if order == 'asc' else '-'

        query = Q()

        if search_query:
            keywords = search_query.split()
            for keyword in keywords:
                query |= Q(statut__icontains=keyword) | \
                         Q(date_commande__icontains=keyword) | \
                         Q(quantite__icontains=keyword) |\
                         Q(id__icontains=keyword)

                query |= Q(personne__nom__icontains=keyword)
                query |= Q(personne__prenom__icontains=keyword)
                query |= Q(livre__titre__icontains=keyword)
                query |= Q(fournisseur__nom_fournisseur__icontains=keyword)

        commandes_en_cours = Commander.objects.filter(statut='en cours').filter(query)
        commandes_terminees = Commander.objects.filter(statut='terminé').filter(query)

        commandes_en_cours = commandes_en_cours.order_by(f"{sort_prefix}{sort_by}")
        commandes_terminees = commandes_terminees.order_by(f"{sort_prefix}{sort_by}")

        return commandes_en_cours, commandes_terminees

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        commandes_en_cours, commandes_terminees = self.get_queryset()

        context['commandes_en_cours'] = commandes_en_cours
        context['commandes_terminees'] = commandes_terminees
        return context
@login_required(login_url='login')
def terminer_commande(request, pk):
    if not request.user.is_staff:
        return HttpResponseForbidden("Vous n'avez pas la permission de faire cette action.")

    commande = get_object_or_404(Commander, pk=pk)
    if commande.statut == 'en cours':

        commande.statut = 'terminé'
        commande.save()

        livre = commande.livre
        livre.quantite_disponible += commande.quantite
        livre.save()

        reservations = Reserver.objects.filter(livre=commande.livre, statut='en cours')
        for reservation in reservations:
            Notifier.objects.create(
                personne=reservation.personne,
                livre=commande.livre,
                quantite=commande.quantite,
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
        sort_by = self.request.GET.get('sort_by', 'date_reservation')
        order = self.request.GET.get('order', 'asc')
        sort_prefix = '' if order == 'asc' else '-'
        sorting_options = {
            'id': 'id_commande',
            'date': 'date_commande',
            'quantite': 'quantite',
            'statut': 'statut',
        }

        queryset = super().get_queryset()

        if sort_by in sorting_options:
            queryset = queryset.order_by(f"{sort_prefix}{sorting_options[sort_by]}")
        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        reservations_en_cours = Reserver.objects.filter(statut='en cours')
        reservations_terminees = Reserver.objects.filter(statut='terminé')

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
    form_class = ReserverForm
    template_name = 'gui/ajouter_reservation.html'
    success_url = reverse_lazy('reservations_list')

    def form_valid(self, form):

        personne = form.cleaned_data['personne']
        date_reservation = form.cleaned_data['date_reservation']
        statut = form.cleaned_data['statut']

        livres = self.request.POST.getlist('livres[]')
        quantites = self.request.POST.getlist('quantites[]')

        if not livres or not quantites:
            form.add_error(None, "Vous devez ajouter au moins un livre avec une quantité.")
            return self.form_invalid(form)

        try:
            with transaction.atomic():
                for isbn13, quantite in zip(livres, quantites):
                    if isbn13 and quantite:
                        quantite = int(quantite)
                        if quantite <= 0:
                            form.add_error(None, f"Quantité invalide pour le livre {isbn13}.")
                            return self.form_invalid(form)

                        try:
                            livre = Livre.objects.get(isbn13=isbn13)
                        except Livre.DoesNotExist:
                            form.add_error(None, f"Le livre avec l'ISBN {isbn13} n'existe pas.")
                            return self.form_invalid(form)

                        Reserver.objects.create(
                            personne=personne,
                            livre=livre,
                            date_reservation=date_reservation,
                            statut=statut,
                            quantite=quantite
                        )

        except Exception as e:
            form.add_error(None, f"Erreur lors de l'enregistrement : {e}")
            return self.form_invalid(form)

        return HttpResponseRedirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['livres'] = Livre.objects.all()
        return context


class ReserverUpdate(StaffRequiredMixin, UpdateView):
    model = Reserver
    form_class = ReserverUpdateForm
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

            try:
                reservation = Reserver.objects.get(id=reservation_id)
                if pk:

                    reservation.delete()
                    return redirect(reverse_lazy('reservations_list'))
                else:

                    return redirect(reverse_lazy('reservations_with_ID_delete', kwargs={'pk': reservation.id}))
            except Reserver.DoesNotExist:

                return render(request, self.template_name, {'error': "Reservation non trouvée."})
        return render(request, self.template_name, {'error': "ID de reservation invalide."})
class ReserverResearch(ListView):
    model = Reserver
    template_name = 'gui/lister_reservations.html'
    context_object_name = 'reservations'

    def get_queryset(self):

        search_query = self.request.GET.get('search', '')
        sort_by = self.request.GET.get('sort_by', 'date_reservation')
        order = self.request.GET.get('order', 'asc')
        sort_prefix = '' if order == 'asc' else '-'

        query = Q()

        if search_query:
            keywords = search_query.split()
            for keyword in keywords:
                query |= Q(statut__icontains=keyword) | \
                         Q(date_reservation__icontains=keyword) | \
                         Q(id__icontains=keyword)

                query |= Q(personne__nom__icontains=keyword)
                query |= Q(personne__prenom__icontains=keyword)
                query |= Q(livre__titre__icontains=keyword)

        reservations_en_cours = Reserver.objects.filter(statut='en cours').filter(query)
        reservations_terminees = Reserver.objects.filter(statut='terminé').filter(query)

        reservations_en_cours = reservations_en_cours.order_by(f"{sort_prefix}{sort_by}")
        reservations_terminees = reservations_terminees.order_by(f"{sort_prefix}{sort_by}")

        return reservations_en_cours, reservations_terminees

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        reservations_en_cours, reservations_terminees = self.get_queryset()

        context['reservations_en_cours'] = reservations_en_cours
        context['reservations_terminees'] = reservations_terminees
        return context
@login_required(login_url='login')
def terminer_reservation(request, pk):
    if not request.user.is_staff:
        return HttpResponseForbidden("Vous n'avez pas la permission d'effectuer cette action.")

    reservation = get_object_or_404(Reserver, pk=pk)
    livre = reservation.livre

    if reservation.statut == 'en cours':

        if reservation.quantite > livre.quantite_disponible:
            messages.error(request, "La quantité réservée dépasse le stock disponible.")
            return redirect('reservations_list')

        reservation.statut = 'terminé'
        reservation.save()

        livre.quantite_disponible -= reservation.quantite
        livre.save()

        messages.success(request, "Réservation terminée avec succès.")

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


def check_reservations(request):
    if request.method == "POST":

        date_limite = timezone.now().date() - timezone.timedelta(weeks=3)

        reservations_depassees = Reserver.objects.filter(
            date_reservation__lt=date_limite,
            statut='en cours'
        )

        for reservation in reservations_depassees:

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

        return redirect('notifications_list')

    return redirect('notifications_list')


def mark_notification_done(request, notification_id):
    if request.method == 'POST':

        notification = get_object_or_404(Notifier, id=notification_id)

        notification.termine = True
        notification.save()

        if notification.type == 'reservation' and notification.personne and notification.livre:

            reservation = Reserver.objects.filter(
                personne=notification.personne,
                livre=notification.livre,
                statut='en cours'
            ).first()

            if reservation:
                reservation.statut = 'terminé'
                reservation.save()

        return redirect('notifications_list')
def delete_notification(request, notification_id):
    if request.method == 'POST':
        notification = get_object_or_404(Notifier, id=notification_id)
        notification.delete()
        return redirect('notifications_list')

def custom_404_view(request, exception):
    return render(request, 'gui/404.html', status=404)