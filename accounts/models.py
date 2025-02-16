from django.db import models
from django.conf import settings

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='profile', on_delete=models.CASCADE)
    bio = models.TextField(max_length=400, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    profile_photo = models.ImageField(upload_to="user/%Y/%m/%d/", blank=True, null=True)

    def __str__(self):
        return f'{self.user.username}'
    
    def count_likes(self):
        return self.likes.filter(like=True).count()
    
