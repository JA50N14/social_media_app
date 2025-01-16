from django.db import models
from django.conf import settings
from django.db.models import Q, F, UniqueConstraint

# Create your models here.

class Chat(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='chat_user1', on_delete=models.PROTECT)
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='chat_user2', on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user1', 'user2'], name='unqiue_users', condition=Q(user1__lt=F('user2')))
        ]

    def __str__(self):
        return f'Chat between {self.user1.username} and {self.user2.username}'


class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='messages', on_delete=models.PROTECT)
    content = models.CharField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f'Message from {self.sender} at {self.timestamp}'


class ChatViewed(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    last_viewed = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-last_viewed']
        indexes = [
            models.Index(fields=['chat', 'last_viewed']),
        ]
    
    def __str__(self):
        return f'Chat last seen: {self.last_viewed}'
