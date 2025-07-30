from django.urls import path
from .views import CreatePostView , IndexPostView ,DeletePostView , UpdatePostView ,UsersListView , UserPostsView , ToggleLikeView 
from django.conf import settings
from django.conf.urls.static import static

app_name = 'post'
urlpatterns = [
    path('', IndexPostView.as_view(), name='index-post'),
    path('users/', UsersListView.as_view(), name='users-list'),
    path('user/<int:user_id>/posts/', UserPostsView.as_view(), name='user-posts'),
    path('create/', CreatePostView.as_view(), name='create-post'),
    path('<int:pk>/edit/', UpdatePostView.as_view(), name='update-post'),
    path('<int:pk>/delete/', DeletePostView.as_view(), name='delete-post'),
    path('toggle-like/<int:pk>/', ToggleLikeView.as_view(), name='toggle-like'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)