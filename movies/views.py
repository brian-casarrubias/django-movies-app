from django.shortcuts import render, redirect
from movies.forms import UserRegisterForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout # im using this so i can authenticate via the home view without the use of class based views, im doing it manually
from django.contrib.auth.decorators import login_required
#safety
from django.views.decorators.debug import sensitive_post_parameters, sensitive_variables
import time
# Create your views here.

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
              
              