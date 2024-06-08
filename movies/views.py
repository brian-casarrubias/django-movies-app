from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from movies.forms import UserRegisterForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout # im using this so i can authenticate via the home view without the use of class based views, im doing it manually
from django.contrib.auth.decorators import login_required
#safety
from django.views.decorators.debug import sensitive_post_parameters, sensitive_variables
import time
#optimization
from django.urls import reverse_lazy

#these are imports for websecraping
import pprint
import re
import time
import concurrent.futures # maybe use
import requests
import os
import threading
import lxml
from bs4 import BeautifulSoup

#our models
from . models import Profile, Movie, User

#cahcing stuff
from django.views.decorators.cache import cache_page
from django.core.cache import cache #this is going to be used to cache the webscraping result so we dont have to keep making requests... speeding up the process


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
@cache_page(60 * 15)
@login_required
def discover_movies(request):
    profile = request.user.profile if request.user.is_authenticated else None


    context = {
        'profile':profile,
    }
    return render(request, 'movies/all-movies.html')


##############these are my regexes and dictionary########################################################           
movie_titles = {}

# these are my regexes we will zip them into a dictionary
title_regex = re.compile(r'mediatitle="([^"]*)"')
#new regex
#this solves the issue when there are no characters/the score is blank!!
movie_scores_regex = re.compile(r'theme="medium"> (\d{2,3}| )?')
#belo were changed on their website so its no longer useful -.-
# audience_score_regex = re.compile(r'audiencescore="(\d{1,3})?"') # the ? we can either have a score or not, i put it since the werbsite sometimes doesnt have any value and that fixed my problem it created with indexing incorrect values
# critics_score_regex = re.compile(r'criticsscore="(\d{1,3})?"') #the 1-3 means it can match 0, 1, 10, 100 or nothing, that fiexed everything
movie_images_regex = re.compile(r'src="([^"]*)"')


#this is the function that scrapes rotten tomatoes for movies!
#ill use this to scrape, and sort things in other functions

def scrape_website(url):
    #first were going to check if we have already webscraped this within the time we set  below
    #if it is found, then we wont make a new request/webscrape, instead we will look in our cache.
    #if its not found, we will indeed make the request/webscrape and then store the results so the next time we wont have to do this again!


    
    if cache.get('webscrape') != None:
        source = cache.get('webscrape')
        print('cache')
      
    else:
        source = str(requests.get(url).content)
        source += str(requests.get('https://www.rottentomatoes.com/browse/movies_at_home/affiliates:netflix?page=6').content)
        cache.set('webscrape', source, 60 * 5)
       
        print('hit')
      

    
    soup = BeautifulSoup(source, 'lxml')

    classes = soup.find_all('div', class_='discovery-tiles__wrap')
      ############new find all we are using to 
    classes_scores = soup.find_all('score-pairs-deprecated')
     ######new vareiable this is a list of all the values im using########
    #what im trying to do is have all the even as critic, and odd as the audience 
    movie_scores = movie_scores_regex.findall(str(classes_scores))

     #converting the values to int because below were calculating so we need them to be in
    movie_scores = [int(movie) if movie != '' else movie for movie in movie_scores] 
    audience_scores = []
    critic_scores = []

    # we need to index all these so that we can properly display them. Since the list is like this [1, 1, 2, 2, 3, 3]
    #these are pairs, so to get the correct ones im getting all the even nums and appending them to audience score list
    #and the odds im paring them to the critic, that way when i use lets say index 1 for both critic audience they will be paired toegther
    # im also checking if its int because in the sorted part, i cant sort int and str, this fixed the error
    for index, score in enumerate(movie_scores):
        if index % 2 == 0:
            #some values are empty, rarely but if it is it gets added in my list as empty string, so if i get that i just say 0
            if type(score) == int:
                critic_scores.append(score)
            else:
                critic_scores.append(0)
        else:
            if type(score) == int:
                audience_scores.append(score)
            else:
                audience_scores.append(0)
 

    all_title = title_regex.findall(str(classes))
    all_imgs = movie_images_regex.findall(str(classes))

    #loop throgu all my titles, and enumerate and use the index to also access my scores and such

    for index, title in enumerate(all_title):
        movie_titles[title] = {
            'AudienceScore':audience_scores[index] if index < len(audience_scores) else str(0) ,
            'CriticScore':critic_scores[index] if index < len(critic_scores) else str(0) ,
            'MovieThumbnail':all_imgs[index] if index < len(all_imgs) else str(0),
        }
   
    return movie_titles

# this is the snippet to find movies, so this is where im going to add the 
# web scraping stuff
cache_page(60)
@login_required
def request_discover_movies(request):
    #what ever is returned (dictionary)
    order_movies = scrape_website('https://www.rottentomatoes.com/browse/movies_at_home/sort:popular?page=5')
    # pprint.pprint(order_movies)
  
    profile = request.user.profile
    #were gonna filter out even further, by only displaying the movies that are not in our current movies list, cuz why would peiople want to see the movie if theyh already have it
    try:
        my_movies = Movie.objects.filter(profile=profile)
        for movie in my_movies:
            if movie.title in order_movies:
                del order_movies[movie.title]
            else:
                continue
    except:
        raise Exception('An error occured')
        
    
    context = {
        'order_movies':order_movies,
    }

        
    return render(request, 'movies/snippets/find-movies.html', context) 
cache_page(60)
@login_required
def request_top_movies(request):
    start_timer = time.perf_counter()
 

    if movie_titles != {}:
        movies = movie_titles
       
    else:
        movies = scrape_website('https://www.rottentomatoes.com/browse/movies_at_home/sort:popular?page=5')
        
    #this is gonna order from hiehgest values to least
    if cache.get('top_movies') != None:
        order_movies = cache.get('top_movies')
        print('cache')
    else:
        order_movies = dict(sorted(movies.items(), key= lambda x: x[1]['AudienceScore' ], reverse=True))
        cache.set('top_movies', order_movies, 60 * 5)
        print('hit')
    end_timer = time.perf_counter()
    print(F'Time it took to execute: {round(end_timer - start_timer, 2)} second(s)')

    profile = request.user.profile
    #were gonna filter out even further, by only displaying the movies that are not in our current movies list, cuz why would peiople want to see the movie if theyh already have it
    try:
        my_movies = Movie.objects.filter(profile=profile)
        for movie in my_movies:
            if movie.title in order_movies:
                del order_movies[movie.title]
            else:
                continue
    except:
        raise Exception('An error occured')
    context = {
        'order_movies':order_movies,
    }
    
    return render(request, 'movies/snippets/find-movies.html', context) 

cache_page(60)
@login_required
def request_least_movies(request):
    start_timer = time.perf_counter()

    if movie_titles != {}:
        movies = movie_titles
    else:
        movies = scrape_website('https://www.rottentomatoes.com/browse/movies_at_home/sort:popular?page=5')
    #this is gonna order from hiehgest values to least
   
    if cache.get('least_movies')!= None:
        order_movies = cache.get('least_movies')
        print('cache')
    else:
        order_movies = dict(sorted(movies.items(), key= lambda x: x[1]['AudienceScore'], reverse=False))
        cache.set('least_movies', order_movies, 60 * 5)
        print('hit')
    end_timer = time.perf_counter()
    print(F'Time it took to execute: {round(end_timer - start_timer, 2)} second(s)')

    profile = request.user.profile
    #were gonna filter out even further, by only displaying the movies that are not in our current movies list, cuz why would peiople want to see the movie if theyh already have it
    try:
        my_movies = Movie.objects.filter(profile=profile)
        for movie in my_movies:
            if movie.title in order_movies:
                del order_movies[movie.title]
            else:
                continue
    except:
        raise Exception('An error occured')
    
    context = {
        'order_movies':order_movies,
    }
    return render(request, 'movies/snippets/find-movies.html', context) 

@login_required
def request_title_ordered(request):
    start_timer = time.perf_counter()
    if movie_titles != {}:
        movies = movie_titles
    else:
        movies = scrape_website('https://www.rottentomatoes.com/browse/movies_at_home/sort:popular?page=5')

    if cache.get('alphabet_ordered')!= None:
        order_movies = cache.get('alphabet_ordered')
        print('cache')
    else:
        order_movies = dict(sorted(movies.items(), key= lambda x: x[0], reverse=False))
        cache.set('alphabet_ordered', order_movies, 60 * 5)
        print('hit')
    end_timer = time.perf_counter()
    print(F'Time it took to execute: {round(end_timer - start_timer, 2)} second(s)')

    profile = request.user.profile
    #were gonna filter out even further, by only displaying the movies that are not in our current movies list, cuz why would peiople want to see the movie if theyh already have it
    try:
        my_movies = Movie.objects.filter(profile=profile)
        for movie in my_movies:
            if movie.title in order_movies:
                del order_movies[movie.title]
            else:
                continue
    except:
        raise Exception('An error occured')
    context = {
        'order_movies':order_movies,
    }
    return render(request, 'movies/snippets/find-movies.html', context) 

@login_required
def add_movie(request):
  
    movie_creation = []
    if request.method == 'POST':

        # were looping because we added a counter to the name of the input in the HTML, therefore we dont know what the acrtualy
        #value is so were looping through all until we find it
        #im adding these values to an empty list i initialized above
        for key in request.POST.keys():
            if key.startswith('movie-'):
                movie_creation.append(request.POST.get(key))
            if key.startswith('audience-'):
                movie_creation.append(request.POST.get(key))     
            if key.startswith('critic-'):
                movie_creation.append(request.POST.get(key))
            if key.startswith('url-'):
                movie_creation.append(request.POST.get(key))
        
        #now were going to initialize variables to create the movie for the profile movies list
        profile = request.user.profile
        title = movie_creation[0]
        audience_score = int(movie_creation[1])
        critic_score = int(movie_creation[2])
        image_url = movie_creation[3]


        #creating thje object, we need to check that there are no duplicate title values
        #here im filtering the movie based on matching profile and movie title, and getting the first value
        #if it is empty that means there are no duplicates, so create/add a movie
        #if it is not empty, then we DONT want to add/ create a movie because im not allowing duplicates
        current_movies = Movie.objects.filter(profile=profile, title=title).first()
        
        if current_movies == None:
            Movie.objects.create(profile=profile, title=title,image_url=image_url, audience_score=audience_score, critic_score=critic_score )
        else:
            return HttpResponse('<script> alert("This movie is already within your movies list!"); </script>')
        

       
           
    # return render(request, 'movies/snippets/least-movies.html')
    return HttpResponse(status=201)




@login_required
def my_movies(request):
    profile = request.user.profile
    movies = Movie.objects.select_related('profile').filter(profile=profile).order_by('-completed','title')
    
    context = {
        'movies':movies,
        
    }
    
    return render(request, 'movies/my-movies.html', context)

@login_required
def my_movies_snippet(request):
   
    profile = request.user.profile
    movies = Movie.objects.select_related('profile').filter(profile=profile).order_by('-completed','title')
    
    context = {
        'movies':movies,
        
    }
    return render(request, 'movies/snippets/my-movies-snippet.html', context)

@login_required
def complete_movie(request, pk):
    
    #lets retrieb the profile
    profile = request.user.profile
    #now lets retirve the movie with the pk they sent
    movie = get_object_or_404(Movie, pk=pk)

    #first were gonna check that the current profile matches the profile associated with the movie, or else this would give others
    # permission to do stuff with you movie if they had the link!
    if movie.profile == profile:
        if not movie.completed:
            movie.completed = True
        else:
            movie.completed = False
    #let us save now
    movie.save()
    #now lets query alll the movies again so that we get the updated version
    movies = Movie.objects.select_related('profile').filter(profile=profile).order_by('-completed','title')

    context = {
        'movies':movies,
    }

    return render(request, 'movies/snippets/my-movies-snippet.html', context)


def delete_movie(request, pk):
    profile = request.user.profile
    movie = get_object_or_404(Movie, pk=pk)

    if movie.profile == profile:
        movie.delete() # i dont think we need to save for deleting
    else:
        return HttpResponse('<h1>You DONT have access to this!! leave NOW!! </h1>')
    
    movies = Movie.objects.select_related('profile').filter(profile=profile).order_by('-completed','title')

    context = {
        'movies':movies,
    }
    
    return render(request, 'movies/snippets/my-movies-snippet.html', context)