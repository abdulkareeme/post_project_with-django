from django import forms
from .models import CustomUser as User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate , get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from collections import OrderedDict

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput , label='password_confirm')

    class Meta :
        model = User
        fields = ['first_name' , 'last_name' , 'email' , 'password' , 'password_confirm']

    # method for check in the email if it is unique
    def email_clean(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email is already in use.")
        return email
    def clean(self) :
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm :
            raise forms.ValidationError("Passwird is not match")
        return cleaned_data
    
    # method for save the user in database 
    # befor saving data (commit=False) we do some tric:
        # 1- username in Model user is importent so we put email in it
        # 2- befor save password we must hashing it using set.password()
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = f"{self.cleaned_data['first_name']} {self.cleaned_data['last_name']}"
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
    
# class for login to appear email address and password not username , password
class LoginForm(AuthenticationForm):
    username =forms.CharField(
        required=False ,
        widget=forms.HiddenInput()
    )
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'})
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'})
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        ordered_fields = OrderedDict()
        ordered_fields['email'] = self.fields['email']
        ordered_fields['password'] = self.fields['password']
        # ordered_fields['username'] = self.fields['username'] 
        self.fields = ordered_fields

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email') 
        password = cleaned_data.get('password')

        # check if user has been register befor
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError("User doesn't exist.")

        self.user_cache = user
        return cleaned_data

    def get_user(self):
        return getattr(self, 'user_cache', None)