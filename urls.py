from django.contrib import admin
from django.urls import path
from chat import views  

# Définition des routes URL pour les vues
urlpatterns = [
    path('admin/', admin.site.urls),  # Page d'administration Django
    path('', views.pageEntrer, name='pageEntrer'),  # Page d'accueil avec formulaire
    path('home', views.home, name='home'),  # Page d'accueil avec formulaire
    path('create_room/', views.create_room, name='create_room'),  # Page pour créer une room
    path('send_mail/', views.send_mail, name='send_mail'),  # Envoi de l'email d'invitation
    path('room/<str:room_name>/', views.room, name='room'),  # Page d'une room avec le paramètre room_name
    path('join_room/', views.join_room, name='join_room'),  # Page pour rejoindre une room
    path('send/', views.send, name="send"),  # Envoi d'un message
    path('getMessages/<str:room>/', views.getMessages, name="getMessages"),  # Récupération des messages d'une room
    path('access_room/<uuid:unique_link>/', views.access_room, name='access_room'), #Accés à une room via un lien unique
]
