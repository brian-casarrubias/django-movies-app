from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.CharField(max_length=155, null=True, blank=True)
    
    ## add profile image later!!!!
    # profile_image = models.ImageField()

    def __str__(self):
        return f'{self.user}'
