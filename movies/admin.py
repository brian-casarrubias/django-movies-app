from django.contrib import admin
from movies.models import Profile, Movie

# Register your models here.

admin.site.register(Profile) # adding our models to the admin site :)
admin.site.register(Movie)