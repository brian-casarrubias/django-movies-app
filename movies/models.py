from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.CharField(max_length=155, null=True, blank=True)
   
    
    ## add profile image later maybe!!!!
    # profile_image = models.ImageField()

    def __str__(self):
        return f'{self.user}'
    

class Movie(models.Model):
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='movies') #note always do plural of the class
    title = models.CharField(max_length=155, null=True, blank=False)                        #so profile.movies.all() etc!!
    image_url = models.CharField(max_length=255, null=True, blank=False)
    completed = models.BooleanField(default=False, null=True, blank=False)
    slug = models.SlugField(unique=True, null=True, blank=True, max_length=255)

    audience_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True, blank=False
    )
    critic_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True, blank=False
    )

    #were overriding the save method, if the slug doesnt exist, then will will make one with the title
    #then call the super save() method
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
