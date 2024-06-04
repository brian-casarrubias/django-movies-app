from django.shortcuts import render, redirect
from movies.forms import UserRegisterForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout # im using this so i can authenticate via the home view without the use of class based views, im doing it manually
from django.contrib.auth.decorators import login_required
#safety
from django.views.decorators.debug import sensitive_post_parameters, sensitive_variables
import time

#these are imports for websecraping

import re
import time
import concurrent.futures # maybe use
import requests
import os
import threading
import lxml
from bs4 import BeautifulSoup


@sensitive_post_parameters('username', 'password') # these variables will be treated in a special way, for example if were logging, these variables wont be exposed
def home(request):
   
    if request.method == 'POST':
        if request.user.is_authenticated:
            return redirect('home-page')
        else:
            #were retriving the data we submited
            username = request.POST.get('usernameInput', 0)
            password = request.POST.get('passwordInput', 0)
            user = authenticate(request, username=username, password=password)

            #now we can login using this data
            try:
                login(request, user)
                messages.success(request, f'{user} has logged in!')
                return redirect('home-page')
            except:
                messages.error(request, 'Could not login, please check again!')
                
    return render(request, 'movies/index.html') # (request, htmlfile, context {})


def register(request):
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data['username'] # gets the username
            messages.success(request, f'Account: "{username}" successfuly created!')
            return redirect('home-page')
        else:
            messages.error(request, 'Could not create account, please try again!')
            return redirect('register-page')
    else:
        form = UserRegisterForm()

    context = {
        'form':form,
    }
    return render(request, 'movies/register.html', context)


@login_required
def logoutUser(request):
    logout(request) # logout the user
    messages.success(request, 'You have been logged out!')        
    return redirect('home-page')      



########################## main sections of the application#######################
@login_required
def discover_movies(request):
    profile = request.user.profile if request.user.is_authenticated else None


    context = {
        'profile':profile,
    }
    return render(request, 'movies/all-movies.html')


###############these are my regexes and dictionary########################################################           
movie_titles = {}

# these are my regexes we will zip them into a dictionary
title_regex = re.compile(r'mediatitle="([^"]*)"')
audience_score_regex = re.compile(r'audiencescore="(\d{1,3})?"') # the ? we can either have a score or not, i put it since the werbsite sometimes doesnt have any value and that fixed my problem it created with indexing incorrect values
critics_score_regex = re.compile(r'criticsscore="(\d{1,3})?"') #the 1-3 means it can match 0, 1, 10, 100 or nothing, that fiexed everything
movie_images_regex = re.compile(r'src="([^"]*)"')


#this is the function that scrapes rotten tomatoes for movies!
#ill use this to scrape, and sort things in other functions
def scrape_website(url):
    source = requests.get(url).content
    soup = BeautifulSoup(source, 'lxml')

    classes = soup.find_all('div', class_='discovery-tiles__wrap')

    all_title = title_regex.findall(str(classes))
    all_audience_score = audience_score_regex.findall(str(classes)) 
    all_critics_score = critics_score_regex.findall(str(classes))

    all_imgs = movie_images_regex.findall(str(classes))

    #loop throgu all my titles, and enumerate and use the index to also access my scores and such

    for index, title in enumerate(all_title):
        movie_titles[title] = {
            'AudienceScore':all_audience_score[index] if index < len(all_audience_score) else str(0),
            'CriticScore':all_critics_score[index] if index < len(all_critics_score) else str(0),
            'MovieThumbnail':all_imgs[index] if index < len(all_imgs) else str(0),
        }
    return movie_titles

# this is the snippet to find movies, so this is where im going to add the 
# web scraping stuff
@login_required
def request_discover_movies(request):
    #what ever is returned (dictionary)
    movie_titles = scrape_website('https://www.rottentomatoes.com/browse/movies_at_home/sort:popular?page=5')
    
    context = {
        'movie_titles':movie_titles,
    }
    # how to iterate over the dictionary
    # for movie, details in movie_titles.items():
    # print(movie, details['AudienceScore'], details['CriticScore'])
        
    return render(request, 'movies/snippets/find-movies.html', context) 

@login_required
def request_top_movies(request):
    start_timer = time.perf_counter()

    if movie_titles != {}:
        movies = movie_titles
       
    else:
        movies = scrape_website('https://www.rottentomatoes.com/browse/movies_at_home/sort:popular?page=5')
    #this is gonna order from hiehgest values to least
    order_movies = dict(sorted(movies.items(), key= lambda x: x[1]['AudienceScore'], reverse=True))
    end_timer = time.perf_counter()
    print(F'Time it took to execute: {round(end_timer - start_timer, 2)} second(s)')
    context = {
        'order_movies':order_movies,
    }
    
    return render(request, 'movies/snippets/top-movies.html', context) 


@login_required
def request_least_movies(request):
    start_timer = time.perf_counter()

    if movie_titles != {}:
        movies = movie_titles
    else:
        movies = scrape_website('https://www.rottentomatoes.com/browse/movies_at_home/sort:popular?page=5')
    #this is gonna order from hiehgest values to least
    order_movies = dict(sorted(movies.items(), key= lambda x: x[1]['AudienceScore'], reverse=False))
    end_timer = time.perf_counter()
    print(F'Time it took to execute: {round(end_timer - start_timer, 2)} second(s)')
    context = {
        'order_movies':order_movies,
    }
    return render(request, 'movies/snippets/least-movies.html', context) 

@login_required
def request_title_ordered(request):
    start_timer = time.perf_counter()
    if movie_titles != {}:
        movies = movie_titles
    else:
        movies = scrape_website('https://www.rottentomatoes.com/browse/movies_at_home/sort:popular?page=5')

    order_movies = dict(sorted(movies.items(), key= lambda x: x[0], reverse=False))
    end_timer = time.perf_counter()
    print(F'Time it took to execute: {round(end_timer - start_timer, 2)} second(s)')
    context = {
        'order_movies':order_movies,
    }
    return render(request, 'movies/snippets/name-ordered-movies.html', context) 

@login_required
def add_movie(request):
    if request.method == 'POST':
        title = request.POST.get('movie')
        print(title, 'has been received!')
    return render(request, 'movies/snippets/least-movies.html')