from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as auth_logout
from .forms import LoginForm, RegisterForm, ProfileUpdateForm
from mini_github import utils


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(username=username, password=password)

            if user is not None:
                auth_login(request, user)
                return redirect('/')
            else:
                return render(request, 'auth/login.html', {'error_message': 'Invalid username or password'})
        else:
            error_message = utils.get_error_message(form)
            return render(request, 'auth/register.html', {'error_message': error_message})

    else:
        form = LoginForm()

    return render(request, 'auth/login.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')

            user = authenticate(username=username, password=password)
            auth_login(request, user)

            return redirect('/')
        else:
            error_message = utils.get_error_message(form)
            return render(request, 'auth/register.html', {'error_message': error_message})
    else:
        form = RegisterForm()

    return render(request, 'auth/register.html', {'form': form})


@login_required()
def logout(request):
    auth_logout(request)
    return redirect('login')


@login_required()
def my_profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            return redirect('my_profile')
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'auth/my_profile.html', {'form': form})
