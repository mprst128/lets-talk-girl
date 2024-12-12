from django.db import models
from datetime import datetime
import uuid
from cryptography.fernet import Fernet
from django.conf import settings


key = Fernet.generate_key()
cipher = Fernet(settings.ENCRYPTION_KEY)

# Create your models here.

class Room(models.Model):
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    unique_link = models.UUIDField(default=uuid.uuid4, editable=False)


class Message(models.Model):
    value = models.CharField(max_length=1000)
    date = models.DateTimeField(default=datetime.now, blank=True)
    user = models.CharField(max_length=1000)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)


    def save(self, *args, **kwargs):
        #si pas chiffré on chiffre
        if not self.value.startswith("gAAAAA"):
            self.value =  cipher.encrypt(self.value.encode()).decode()
            super(Message, self).save(*args, **kwargs)


    def get_decrypted_message(self):
        #try:
            return cipher.decrypt(self.value.encode()).decode()
        #except Exception as e:
        #       print(f"Erreur de déchiffrement")
        #      return "Erreur lors du déchiffrement"