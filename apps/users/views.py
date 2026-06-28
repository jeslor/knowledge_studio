from django.shortcuts import render, redirect
from models import CustomUser, UserProfile
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


def login(request):
    if(request.method == 'POST'):
        data = request.POST
        form = UserCreationForm(request, data=data)
        if form.is_valid():
            # Retrieve the authenticated user object from the form
            user = form.get_user()
            auth_login(request, user)

            return redirect("/profile", pk=user.pk)
    else:
        # If it is a get request
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})


def register(request):
    if(request.method == 'POST'):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            #Automatically log the user in  after registering
            auth_login(request, user)

            #redirect the user to their profile
            return red

# Create your views here.

