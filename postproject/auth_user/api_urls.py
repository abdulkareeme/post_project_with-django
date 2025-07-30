from django.urls import path
from knox import views as knox_views
from .api_views import RegisterAPIView, LoginAPIView ,ListOfUser

urlpatterns = [
    path('register', RegisterAPIView.as_view() ) ,
    path('login' , LoginAPIView.as_view() ) ,
    path('logout' , knox_views.LogoutView.as_view() ),
    path('logout/all' , knox_views.LogoutAllView().as_view() ),
    path('users' , ListOfUser.as_view({'get': 'list'})),
]