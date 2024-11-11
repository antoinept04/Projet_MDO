from django.http import  HttpResponseRedirect
from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse_lazy,reverse
from django.views.generic import CreateView, DeleteView, UpdateView, ListView
from gui.models import Ville, Adresse, Role, Personne, Fournisseur, Editeur, Auteur, Livre, Ecrire, Commander, Notifier, Achat, Reserver
from .forms import PersonneForm, LivreForm, ISBNForm
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, View
from django.contrib.auth.forms import UserCreationForm



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

# 1. Classe Ville
class VilleList(ListView):
    model = Ville
    template_name = 'gui/lister_villes.html'

class VilleCreate(CreateView):
    model = Ville
    fields = ['nom', 'code_postal', 'pays']
    template_name = 'gui/ajouter_ville.html'
    success_url = reverse_lazy('villes_list')



# 2. Classe Adresse
class AdresseList(ListView):
    model = Adresse
    template_name = 'gui/lister_adresses.html'


class AdresseCreate(CreateView):
    model = Adresse
    fields = ['rue', 'n_rue', 'ville']
    template_name = 'gui/ajouter_adresse.html'
    success_url = reverse_lazy('adresses_list')

# 3. Classe Role
class RoleList(ListView):
    model = Role
    template_name = 'gui/lister_roles.html'

class RoleCreate(CreateView):
    model = Role
    fields = ['type']
    template_name = 'gui/ajouter_role.html'
    success_url = reverse_lazy('roles_list')

# 4. Classe Personne
class PersonneList(ListView):
    model = Personne
    template_name = 'gui/lister_personnes.html'

def personne_create(request):
    if request.method == 'POST':
        form = PersonneForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data.get('role')
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Vérifier si l'email existe déjà
            if Personne.objects.filter(email=email).exists():
                form.add_error('email', 'Cet email est déjà utilisé.')
                return render(request, 'gui/ajouter_personne.html', {'form': form})

            # Créer l'utilisateur en fonction du rôle
            nom = form.cleaned_data['nom']
            prenom = form.cleaned_data['prenom']
            date_naissance = form.cleaned_data['date_naissance']
            telephone = form.cleaned_data['telephone']
            adresse = form.cleaned_data['adresse']
            solde = form.cleaned_data['solde']

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
        form = PersonneForm()

    return render(request, 'gui/ajouter_personne.html', {'form': form})

# 5. Classe Fournisseur
class FournisseurList(ListView):
    model = Fournisseur
    template_name = 'gui/lister_fournisseurs.html'

class FournisseurCreate(CreateView):
    model = Fournisseur
    fields = ['nom']
    template_name = 'gui/ajouter_fournisseur.html'
    success_url = reverse_lazy('fournisseurs_list')

# 6. Classe Editeur
class EditeurList(ListView):
    model = Editeur
    template_name = 'gui/lister_editeurs.html'

class EditeurCreate(CreateView):
    model = Editeur
    fields = ['nom']
    template_name = 'gui/ajouter_editeur.html'
    success_url = reverse_lazy('editeurs_list')
    """
    def form_valid(self, form):
        self.object = form.save()
        referer_url = self.request.META.get('HTTP_REFERER')
        if referer_url and 'livres/create/' in referer_url:
            return redirect('livres_create')
        else:
            return redirect(reverse('editeurs_list'))
    """
# 7. Classe Auteur
class AuteurList(ListView):
    model = Auteur
    template_name = 'gui/lister_auteurs.html'

class AuteurCreate(CreateView):
    model = Auteur
    fields = ['nom', 'prenom', 'date_naissance']
    template_name = 'gui/ajouter_auteur.html'
    success_url = reverse_lazy('auteurs_list')

# 8. Classe Livre
class LivreList(ListView):
    model = Livre
    template_name = 'gui/lister_livres.html'


class LivreCreate(View):
    def get(self, request):
        form = LivreForm()
        return render(request, 'gui/ajouter_livre.html', {'form': form})

    def post(self, request):
        form = LivreForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('livres_list')  # Ou toute autre page de redirection

        return render(request, 'gui/ajouter_livre.html', {'form': form})

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

# 9. Classe Ecrire
class EcrireList(ListView):
    model = Ecrire
    template_name = 'gui/lister_ecrits.html'

class EcrireCreate(CreateView):
    model = Ecrire
    fields = ['livre', 'auteur']
    template_name = 'gui/ajouter_ecrire.html'
    success_url = reverse_lazy('ecrits_list')

# 10. Classe Commander
class CommanderList(ListView):
    model = Commander
    template_name = 'gui/lister_commandes.html'

class CommanderCreate(CreateView):
    model = Commander
    fields = ['personne', 'livre', 'date_commande', 'quantite', 'statut']
    template_name = 'gui/ajouter_commande.html'
    success_url = reverse_lazy('commandes_list')

# 11. Classe Notifier
class NotifierList(ListView):
    model = Notifier
    template_name = 'gui/lister_notifications.html'

class NotifierCreate(CreateView):
    model = Notifier
    fields = ['personne', 'livre', 'quantite', 'type', 'commentaire']
    template_name = 'gui/ajouter_notification.html'
    success_url = reverse_lazy('notifications_list')

# 12. Classe Achat
class AchatList(ListView):
    model = Achat
    template_name = 'gui/lister_achats.html'

class AchatCreate(CreateView):
    model = Achat
    fields = ['personne', 'livre', 'quantite', 'date_achat']
    template_name = 'gui/ajouter_achat.html'
    success_url = reverse_lazy('achats_list')

# 13. Classe Reserver
class ReserverList(ListView):
    model = Reserver
    template_name = 'gui/lister_reservations.html'

class ReserverCreate(CreateView):
    model = Reserver
    fields = ['personne', 'livre', 'quantite', 'statut', 'date_reservation']
    template_name = 'gui/ajouter_reservation.html'
    success_url = reverse_lazy('reservations_list')



