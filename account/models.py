from django.db import models
from django.conf import settings

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.CharField(max_length=400, blank=True)
    date_of_birth = models.DateField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    profile_photo = models.ImageField(upload_to="user/%Y/%m/%d/", blank=True)

    def __str__(self):
        return f'{self.user.username}' 
