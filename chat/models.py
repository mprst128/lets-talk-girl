from django.db import models
from datetime import datetime
from datetime import timedelta
from django.utils import timezone
import uuid
from cryptography.fernet import Fernet
from django.conf import settings


key = Fernet.generate_key()
cipher = Fernet(settings.ENCRYPTION_KEY)

# Create your models here.

class Room(models.Model):
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    def __str__(self):
        return self.name


class UniqueLink(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    link = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField(default=timezone.now() + timedelta(hours=50))  
    is_expired = models.BooleanField(default=False)

    def check_expiration(self):
        if timezone.now() > self.expired_at:
            self.is_expired = True
            self.save()
        return self.is_expired


class Message(models.Model):
    value = models.TextField()
    date = models.DateTimeField(default=timezone.now, blank=True)
    user = models.CharField(max_length=1000)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.user}: {self.value[:50]}"


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