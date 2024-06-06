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
    path('request/discover-top-movies/', views.request_top_movies, name='request-top-movies-page'),
    path('request/discover-least-movies/', views.request_least_movies, name='request-least-movies-page'),
    path('request/discover-ordered-movies/', views.request_title_ordered, name='request-ordered-movies-page'),

    path('add-movie/', views.add_movie, name='add-movie-page'),
    

    path('my-movies/', views.my_movies, name='my-movies-page'),

    path('complete-movie/<int:pk>/', views.complete_movie, name='complete-movie-page'),

    path('delete-movie/<int:pk>/', views.delete_movie, name='delete-movie-page'),
]
