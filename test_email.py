import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Paramètres de configuration
smtp_host = 'smtp.umons.ac.be'
smtp_port = 587
smtp_user = '231418@umons.ac.be'
smtp_password = 'aqwpmzsx666fapbkh94'
sender_email = '231418@umons.ac.be'
recipient_email = 'sachamalray2000@gmail.com'  # Adresse de destination

# Sujet et contenu de l'email
subject = 'Test Email'
body = 'Ceci est un email de test envoyé depuis Python.'

# Création du message MIME
message = MIMEMultipart()
message['From'] = sender_email
message['To'] = recipient_email
message['Subject'] = subject

message.attach(MIMEText(body, 'plain'))

try:
    # Connexion au serveur SMTP et envoi de l'email
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()  # Sécurisation de la connexion
        server.login(smtp_user, smtp_password)  # Connexion avec l'email et le mot de passe
        server.sendmail(sender_email, recipient_email, message.as_string())  # Envoi de l'email
        print("Email envoyé avec succès.")
except Exception as e:
    print(f"Erreur lors de l'envoi de l'email: {e}")
