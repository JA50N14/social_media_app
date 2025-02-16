from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from .models import Profile
from post.models import TagNotification
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.forms import UserCreationForm
from .forms import RegistrationForm, ProfileBioForm, ProfilePhotoForm, UserFirstLastNameForm, ProfileDateOfBirthForm, UsernameForm
from django.contrib.auth.decorators import login_required

# Create your views here.

def register(request):
    if request.method == "POST":
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            form.save()
            user = User.objects.get(username=form.cleaned_data['username'])
            TagNotification.objects.create(user=user)
            return redirect('login')
        else:
            return render(request, 'registration/register.html', {'form': form})
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


def edit_profile(request):
    return render(request, 'settings/edit_profile.html')


@login_required
def edit_profile_photo(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = ProfilePhotoForm(data=request.POST, files=request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('edit_profile')
    else:
        form = ProfilePhotoForm(instance=profile)
    return render(request, 'settings/edit_profile_photo.html', {'form': form})


@login_required
def edit_first_last_name(request):
    user = request.user
    if request.method == "POST":
        form = UserFirstLastNameForm(data=request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('edit_profile')
    else:
        form = UserFirstLastNameForm(instance=user)
    return render(request, 'settings/edit_first_last_name.html', {'form': form})


@login_required
def edit_username(request):
    if request.method == "POST":
        form = UsernameForm(data=request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('edit_profile')
    else:
        form = UsernameForm(instance=request.user)
    return render(request, 'settings/edit_username.html', {'form': form})


@login_required
def edit_profile_bio(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = ProfileBioForm(data=request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('edit_profile')
    else:
        form = ProfileBioForm(instance=profile)
    return render(request, 'settings/edit_bio.html', {'form': form})


@login_required
def edit_date_of_birth(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = ProfileDateOfBirthForm(data=request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('edit_profile')
    else:
        form = ProfileDateOfBirthForm(instance=profile)
    return render(request, 'settings/edit_date_of_birth.html', {'form': form})

        



