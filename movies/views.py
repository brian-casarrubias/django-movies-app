from django.shortcuts import render, HttpResponse

# Create your views here.


def home(request):
    
    context = {'name':'Brian', 'age':23}
    return render(request, 'movies/index.html', context) # (request, htmlfile, context {})
