from django.shortcuts import render, redirect
from movies.forms import UserRegisterForm
from django.contrib import messages
from django.contrib.auth import authenticate # im using this so i can authenticate via the home view without the use of class based views, im doing it manually

# Create your views here.


def home(request):
    
    context = {'name':'Brian', 'age':23}
    return render(request, 'movies/index.html', context) # (request, htmlfile, context {})


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