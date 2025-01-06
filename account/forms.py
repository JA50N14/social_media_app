from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from . models import Profile
from django.core.exceptions import ValidationError

class RegistrationForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field in self.Meta.required:
            self.fields[field].required = True

    password = forms.CharField(min_length=8, max_length=30, widget=forms.PasswordInput, required=True)
    password_confirm = forms.CharField(min_length=8, max_length=30, widget=forms.PasswordInput, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        required = ('username', 'first_name', 'last_name', 'email')

    def clean(self):
        cd = super().clean()
        password = cd.get('password')
        password_confirm = cd.get('password_confirm')
        if password != password_confirm:
            raise ValidationError('Passwords do not match.')
        username = cd.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Username already exists. Please enter a different Username.')
        email = cd.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email is already linked to an account.')
        return cd

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.save()
        return user

class ProfileBioForm(ModelForm):
    class Meta:
        model = Profile
        fields = ["bio"]
    
class ProfilePhotoForm(ModelForm):
    class Meta:
        model = Profile
        fields = ["profile_photo"]

class ProfileDateOfBirthForm(ModelForm):
    class Meta:
        model = Profile
        fields = ["date_of_birth"]

class UserFirstLastNameForm(ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name"]

class UsernameForm(ModelForm):
    class Meta:
        model = User
        fields = ["username"]
        exclude = ["email", "password", "first_name", "last_name"]
    