from django.contrib.auth import login  
from django.contrib.auth.views import LoginView as AuthLoginView 
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from .forms import RegisterForm 
from .forms import LoginForm 
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView as AuthLogoutView
from django.shortcuts import resolve_url


# Create your views here.
# Home Page

# class for Register page
class RegisterView(FormView) :
    form_class =RegisterForm
    template_name = 'register.html'
    success_url = reverse_lazy('post:index-post')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)
    
# class for login
class LoginView(AuthLoginView):
    template_name = 'login.html'
    form_class = LoginForm
    success_url = reverse_lazy('post:index-post')
    def get_success_url(self):
        return resolve_url('post:index-post')
    def form_valid(self, form):
        from django.contrib.auth import login
        login(self.request, form.get_user())
        return super().form_valid(form)

# class for logout 
# you must to be loggedin to do logout
class LogoutView(AuthLogoutView):
    next_page = reverse_lazy('login') 
    
    

