import os
from django.core.mail import send_mail
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projet_mdo.settings')  # Remplacez par le nom de votre projet

try:
    send_mail(
        subject="Test Email",
        message="Ceci est un test pour vérifier l'envoi d'e-mails depuis Django avec Gmail.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['sachamalray2000@gmail.com'],  # Adresse cible
        fail_silently=False,
    )
    print("Email envoyé avec succès !")
except Exception as e:
    print(f"Erreur lors de l'envoi de l'email : {e}")
