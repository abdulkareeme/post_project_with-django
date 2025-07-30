from django.views.generic.edit import CreateView ,DeleteView , UpdateView
from django.views.generic import ListView ,TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Post
from .forms import CreatePostForm ,IndexPostForm
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404 
from .models import User
from django.views import View
from django.http import JsonResponse

class IndexPostView(LoginRequiredMixin, ListView):
    model = Post
    form_class = IndexPostForm
    template_name = 'posts/index.html'
    context_object_name = 'posts'
    def get_queryset(self):
        query = self.request.GET.get('q')
        qs = Post.objects.select_related('author').prefetch_related('likes')
        if query:
            return qs.filter(Q(title__icontains=query) | Q(content__icontains=query))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '') 
        return context
    
# class for create post
class CreatePostView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = CreatePostForm
    template_name = 'posts/create.html' # Make sure this template exists
    success_url = reverse_lazy('post:index-post')  # Adjust to your index view name

    def form_valid(self, form):
        # Automatically set the author to the logged-in user
        form.instance.author = self.request.user
        return super().form_valid(form)
    
# class for edit specific post   
class UpdatePostView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = CreatePostForm
    template_name = 'posts/edit.html'
    success_url = reverse_lazy('post:index-post')  # Redirect after successful update

    def dispatch(self, request, *args, **kwargs):
        # Ensure only the author can edit the post
        post = self.get_object()
        if post.author != request.user:
            raise PermissionDenied("You are not the author of this post.")
        return super().dispatch(request, *args, **kwargs)

# class for delete specific post 
class DeletePostView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'posts/delete.html'
    success_url = reverse_lazy('post:index-post')

    def dispatch(self, request, *args, **kwargs):
        # Ensure only the author can delete the post
        post = self.get_object()
        if post.author != request.user:
            raise PermissionDenied("You are not the author of this post.")
        return super().dispatch(request, *args, **kwargs)
    
class UsersListView(LoginRequiredMixin, TemplateView):
    template_name = 'posts/users_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.all()
        return context

class UserPostsView(LoginRequiredMixin, ListView):
    template_name = 'posts/user_posts.html'
    context_object_name = 'posts'

    def get_queryset(self):
        self.selected_user = get_object_or_404(User, pk=self.kwargs['user_id'])
        return Post.objects.filter(author=self.selected_user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_user'] = self.selected_user
        return context
    
class ToggleLikeView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        post = get_object_or_404(Post, pk=pk)
        print(f"Like request received for post {pk}")
        liked = False

        #like = post.likes.filter(request.user)
        if request.user in post.likes.all():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
            liked = True

        return JsonResponse({
            'liked': liked,
            'likes_count': post.likes.count()
        })
