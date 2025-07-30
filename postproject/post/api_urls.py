from django.urls import path , include
from .api_views import IndexApiPost 
from django.conf import settings
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'posts', IndexApiPost, basename='post')

urlpatterns = [
    path('', include(router.urls)),
]