from django.db import models
from datetime import datetime
import uuid
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