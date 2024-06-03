from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home-page'),
    path('register/', views.register, name='register-page'),
    path('logout/', views.logoutUser, name='logout-page'),

    ########################## MAIN PROGRAM URLS #####################
    path('discover-movies/', views.discover_movies, name='discover-movies-page'),
    path('request/discover-movies/', views.request_discover_movies, name='request-movies-page'), # this is the snippet view that webscrapes movies
    
    
]
