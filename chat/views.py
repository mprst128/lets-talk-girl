from .models import Message, Room 
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse , JsonResponse , HttpResponseBadRequest
import bcrypt
import uuid
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib, ssl
from django.core.mail import send_mail


def home(request):
    room_name = request.GET.get('room_name', '')   
    return render(request, 'home.html', {'room_name': room_name})

def room(request, room):
    username = request.GET.get('username')  # Récupère le nom d'utilisateur depuis l'URL
    room_details = Room.objects.get(name=room)  # Récupère les détails de la room par son nom

    # Récupérer les paramètres de recherche (nom d'utilisateur et mot-clé)
    search_username = request.GET.get('username_search', '')  # Si un nom d'utilisateur est fourni
    search_keyword = request.GET.get('keyword_search', '')  # Si un mot-clé est fourni

    # Récupérer tous les messages de la room
    messages = Message.objects.filter(room=room_details.id).order_by('date')

    # Appliquer le filtre par nom d'utilisateur (si présent)
    if search_username:
        messages = messages.filter(user__icontains=search_username)

    # Appliquer le filtre par mot-clé dans le message (si présent)
    if search_keyword:
        messages = messages.filter(value__icontains=search_keyword)

    # Passer les informations nécessaires à la template
    return render(request, 'room.html', {
        'username': username,
        'room': room,
        'room_details': room_details,
        'messages': messages,  # Les messages filtrés sont passés à la template
        'search_username': search_username,
        'search_keyword': search_keyword,
    })

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
    #django-cryptography pour crypter tout les messages

def create_room(request):
    unique_link = None 
    if request.method == "POST":
        room_name = request.POST['room_name']  
        password = request.POST['password']  
        emails = request.POST.getlist('emails')   
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        #boucler ici
        unique_link = str(uuid.uuid4())  # Définir unique_link dans le cas POST
        #ajouter une gestion de l'expiration, par défaut 24h
        # Créer la room
        room = Room.objects.create(name=room_name, password=hashed_password, unique_link=unique_link)
        for email in emails:
            send_invitation_email(request,email, room_name, unique_link)
        # Rendre le lien unique entre personnes
        return redirect("home")  
    return render(request, 'create_room.html', {'unique_link': unique_link})
#rajouter un fichier d'exception pour la gestion d'erreur pour mdp 

#ajouter une methode d'invitation à partir de la room
def send_invitation_email(request, email, room_name, unique_link):
    lien = f"http://{request.get_host()}/access_room/{unique_link}"
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
    '''
    html = f'''
    <html>
    <body>
    <h1>Bonjour</h1>
    <p>Vous avez été invité à rejoindre le canal {room_name}.</p>
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

def access_room(request, unique_link):
    try:
        room = Room.objects.get(unique_link=unique_link)
        if request.method == 'POST':
            room_name = request.POST.get('room_name')
            username = request.POST.get('username')
            password = request.POST.get('password')
            if room_name != room.name:
                return render(request, 'join_room.html', {'error': 'Nom du canal incorrect'})
            if room.password and not bcrypt.checkpw(password.encode('utf-8'), room.password.encode('utf-8')):
                return render(request, 'join_room.html', {'error': 'Mot de passe incorrect'})
            return redirect(f'/room/{room.name}/')
        return render(request, 'join_room.html')
    except Room.DoesNotExist:
        return HttpResponse("Lien invalide ou expiré.")



def getMessages(request, room):
    room_details = Room.objects.get(name=room)
    
    # Récupérer les paramètres de recherche depuis la requête GET
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

    # Retourner les messages filtrés sous forme de JSON
    return JsonResponse({"messages": list(messages.values())})


