from django.shortcuts import render, redirect
from .models import Message, Room 
from django.http import HttpResponse , JsonResponse


def home(request):
    return render(request, 'home.html')

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


def checkview(request):
    room = request.POST['room_name']
    username = request.POST['username']

    if Room.objects.filter(name=room).exists():
        return redirect(f'/{room}/?username={username}')
    else:
        new_room = Room.objects.create(name=room)
        new_room.save()
        return redirect(f'/{room}/?username={username}')
def send(request):
    message = request.POST['message']
    username = request.POST['username']
    room_id = request.POST['room_id']

    new_message = Message.objects.create(value= message , user = username , room = room_id)
    new_message.save()
    return HttpResponse('Message envoyé avec succès')

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


