from .models import Message, Room , UniqueLink
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse , JsonResponse , HttpResponseBadRequest
import bcrypt
import uuid
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib, ssl
from django.core.mail import send_mail

from .models import Room
from .models import Message

import re

# méthode vue page entrer
def pageEntrer(request):
    return render(request, 'pageEntrer.html')

# méthode vue room, nécessite room_name
def home(request):
    room_name = request.GET.get('room_name', '')   
    return render(request, 'home.html', {'room_name': room_name})

# méthode vue room avec filtre de recherche
def room(request, room_name):
    username = request.GET.get('username')   
    try:
        room_details = Room.objects.get(name=room_name)  
    except Room.DoesNotExist:
        return render(request, 'home.html', {'error': 'Room non trouvée'})  
    # Récupérer les paramètres de recherche (nom d'utilisateur et mot-clé)
    search_username = request.GET.get('username_search', '')  # Si un nom d'utilisateur est fourni
    search_keyword = request.GET.get('keyword_search', '')  # Si un mot-clé est fourni
    messages = Message.objects.filter(room=room_details.id).order_by('date')

    # Appliquer le filtre par nom d'utilisateur (si présent)
    if search_username:
        messages = messages.filter(user__icontains=search_username)

    # Appliquer le filtre par mot-clé dans le message (si présent)
    if search_keyword:
        messages = messages.filter(value__icontains=search_keyword)
    return render(request, 'room.html', {
        'username': username,
        'room': room_name,
        'room_details': room_details,
        'messages': messages,  # Les messages filtrés sont passés à la template
        'search_username': search_username,
        'search_keyword': search_keyword,
    })

# méthode pour envoyer des messages
# attention le nom ne s'affiche plus dans le message, username 🔺
def send(request):
    message = request.POST['message']
    username = request.POST['username']
    room_id = request.POST['room_id']
    if not room_id:
        return HttpResponseBadRequest("L'Id de la room est obligatoire")
    try:
        room_id = int(room_id)
    except ValueError:
        return HttpResponseBadRequest("L'Id de la room doit être un integrer.")
    room = get_object_or_404(Room, id=room_id)
    new_message = Message.objects.create(value= message , user = username , room = room)
    new_message.save()
    return HttpResponse('Message envoyé avec succès')

def validate_password(password):
    # vérifie que le mot de passe respecte le pattern
    if not re.match(r"(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}", password):
        return False
    return True

# méthode pour créer une room à partir des données du formulaire, envoie le mail 
def create_room(request):
    unique_links = []  
    if request.method == "POST":
        room_name = request.POST['room_name']  
        password = request.POST['password']  
        emails = request.POST.getlist('emails')
       
        if not validate_password(password):
            # Mot de passe invalide, retourner un message d'erreur
            return render(request, 'create_room.html', {'error': "Le mot de passe doit contenir au moins 8 caractères, dont une majuscule, une minuscule, un chiffre et un caractère spécial."})

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        room = Room.objects.create(name=room_name, password=hashed_password)
        
        for email in emails:
            unique_link = UniqueLink.objects.create(room=room)
            send_invitation_email(request, email, room_name, unique_link, password)
            unique_links.append(unique_link.link)
        return redirect("home") 
    return render(request, 'create_room.html', {'unique_links': unique_links})  

# méthode pour envoyer un lien d'accés par mail
def send_invitation_email(request, email, room_name, unique_link, password):
    lien = f"http://{request.get_host()}/access_room/{unique_link.link}"
    # Configuration du serveur SMTP
    smtp_address = 'smtp.gmail.com'
    smtp_port = 465
    message = MIMEMultipart("alternative")
    message["Subject"] = "[Invitation canal] Vous avez été invité à rejoindre ce canal"
    email_address = "no.reply.lets.talk.girl@gmail.com"   
    email_password = 'pfxv vkus gmll qhgt'   #code genere email gmail à remplacer par une var d'env pour eviter brut
    message["From"] = email_address
    message["To"] = email
    #envoyer le mdp à la personne pour qu'elle se connecte mdp en brut
    texte = f'''
    Bonjour, 
    Vous avez été invité à rejoindre le canal {room_name}.
    Lien vers le canal : {lien}
    Le lien expirera à : {unique_link.expired_at}
    '''
    html = f'''
    <html>
    <body>
    <h1>Bonjour</h1>
    <p>Vous avez été invité à rejoindre le canal {room_name}.</p>
    <p>Le mot de passe est le suivant : {password}<p>
    <p>Le lien expirera à : {unique_link.expired_at}</p>
    <a href="{lien}">Cliquez ici pour rejoindre</a>
    </body>
    </html>
    '''
    # Attacher les versions texte et HTML
    texte_mime = MIMEText(texte, 'plain')
    html_mime = MIMEText(html, 'html')
    message.attach(texte_mime)
    message.attach(html_mime)
    # Envoi de l'email via le serveur SMTP
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(smtp_address, smtp_port, context=context) as server:
            server.login(email_address, email_password)
            server.sendmail(email_address, email, message.as_string())
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email : {e}")

        
#  méthode pour acceder à une room avec nom de la room, password et username de l'utilisateur
def join_room(request):
    if request.method == 'POST':
        room_name = request.POST.get('room_name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not room_name or not username or not password:
            return render(request, 'join_room.html', {'error': 'Tous les champs sont requis'})
        try:
            room = Room.objects.get(name=room_name)
        except Room.DoesNotExist:
            return render(request, 'join_room.html', {'error': 'La salle n\'existe pas'})
        if room.password and not bcrypt.checkpw(password.encode('utf-8'), room.password.encode('utf-8')):
            return render(request, 'join_room.html', {'error': 'Mot de passe incorrect'})
        return redirect(f'/room/{room.name}/')
    return render(request, 'join_room.html')

# méthode pour accéder à une room depuis le lien unique envoyé par mail
def access_room(request, unique_link):
    try:
        link = UniqueLink.objects.get(link=unique_link)
    except UniqueLink.DoesNotExist:
        return HttpResponse("Lien invalide.")
    if link.check_expiration(): 
        return HttpResponse("Ce lien est expiré.")
    room = link.room
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if room.password and not bcrypt.checkpw(password.encode('utf-8'), room.password.encode('utf-8')):
            return render(request, 'join_room.html', {'error': 'Mot de passe incorrect'})
        return redirect(f'/room/{room.name}/')
    return render(request, 'join_room.html', {'room_name': room.name})

# méthode pour récupérer les messages
def getMessages(request, room):
    room_details = Room.objects.get(name=room)
    search_username = request.GET.get('username_search', '')
    search_keyword = request.GET.get('keyword_search', '')

    # Récupérer tous les messages de la room
    messages = Message.objects.filter(room=room_details.id).order_by('date')

    # Appliquer le filtre par nom d'utilisateur 
    if search_username:
        messages = messages.filter(user__icontains=search_username)

    # Appliquer le filtre par mot-clé dans le message
    if search_keyword:
        messages = messages.filter(value__icontains=search_keyword)


    # Déchiffrer les messages avant d'envoyer
    decrypted_messages = []
    for message in messages:
        decrypted_message = message.get_decrypted_message()
        decrypted_messages.append({
            "user" : message.user,
            "value": decrypted_message,
            "date": message.date
        })

    return JsonResponse({"messages": decrypted_messages})
    
