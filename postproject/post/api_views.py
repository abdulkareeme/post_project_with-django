from .filters import PostFilter
from django_filters import rest_framework as filters
from rest_framework import viewsets
from .models import Post ,Comment
from .serializers import IndexSerializer ,CreateSerializer ,CommentSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly 
from rest_framework.pagination import PageNumberPagination
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Pagination for Post
class PostPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 100


# Get All posts
class IndexApiPost(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class  = PostFilter
    pagination_class = PostPagination

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CreateSerializer
        return IndexSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    #  custom action: /posts/{id}/like/
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        post = self.get_object()
        user = request.user

        if user in post.likes.all():
            post.likes.remove(user)
            liked = False
        else:
            post.likes.add(user)
            liked = True
            # --- Send Like Notification ---
            if post.author and post.author.id: 
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f"user_{post.author.id}_notifications", # Target user's group
                    {
                        'type': 'send_notification', # Calls method in consumer
                        'notification_data': {
                            'type': 'like',
                            'message': f"{user.username} liked your post '{post.title}'.",
                            'postId': post.id,
                        }
                    }
                )
            # --- End Send Like Notification ---  

        return Response({
            "status": "liked" if liked else "unliked",
            "total_likes": post.likes.count(),
            "user_has_liked": liked
        })

    #  custom action: /posts/{id}/unlike/
    @action(detail=True, methods=['post'])
    def unlike(self, request, pk=None):
        post = self.get_object()
        user = request.user

        if user in post.likes.all():
            post.likes.remove(user)
            liked = False
        else:
            liked = True

        return Response({
            "status": "unliked",
            "total_likes": post.likes.count(),
            "user_has_liked": False
        })

    #  custom action: /posts/{id}/check-like/
    @action(detail=True, methods=['get'])
    def check_like(self, request, pk=None):
        post = self.get_object()
        return Response({
            "user_has_liked": request.user in post.likes.all(),
            "total_likes": post.likes.count()
        })

    # custom action: /user/likes/
    @action(detail=False, methods=['get'], url_path='user/likes')
    def user_liked_posts(self, request):
        posts = Post.objects.filter(likes=request.user)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)
    
    # add comment api/posts/{post_id}/comment
    @action(detail=True, methods=['post'], url_path='comment')
    def add_comment(self, request, pk=None):
        post = self.get_object()  # the corrent post
        content = request.data.get('content', '').strip()

        if not content:
            return Response({"error": "Content is required"}, status=status.HTTP_400_BAD_REQUEST)

        
        comment = Comment.objects.create(
            post=post,
            user=request.user,
            content=content
        )

        serializer = CommentSerializer(comment, context={'request': request})
        # --- Send Comment Notification ---
        if post.author and post.author.id:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{post.author.id}_notifications", # Target user's group
                {
                    'type': 'send_notification',
                    'notification_data': {
                        'type': 'comment',
                        'message': f"{request.user.username} commented on your post '{post.title}'.",
                        'postId': post.id,
                        'commentId': comment.id,
                    }
                }
            )
        # --- End Send Comment Notification ---
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    # display all comments for specific user in all posts
    # detail=[False] => yhis mean ther is no pk
    @action(detail=False, methods=['get'], url_path='comments')
    def list_user_comments(self, request):
        user = request.user
        comments = Comment.objects.filter(user=user).order_by('-created_at')
        serializer = CommentSerializer(comments, many=True, context={'request': request})
        return Response(serializer.data)

    # edit comment only user how add the comment can edit it
    # urls : api/posts/{post_id}/comments/{comment_id} 
    @action(detail=True, methods=['put'], url_path='comments-edit')
    def edit_comment(self, request, pk=None, comment_id=None):
        comment_id = request.query_params.get('comment_id')
        if not comment_id:
            return Response({"error": "comment_id is required"}, status=400)
        try:
            comment = Comment.objects.get(id=comment_id, post__id=pk)
        except Comment.DoesNotExist:
            return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

        if comment.user != request.user:
            return Response({"error": "You are not the author of this comment"}, status=status.HTTP_403_FORBIDDEN)

        new_content = request.data.get('content', '').strip()
        if not new_content:
            return Response({"error": "Content is required"}, status=status.HTTP_400_BAD_REQUEST)

        comment.content = new_content
        comment.save()

        serializer = CommentSerializer(comment, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    # delete comment only user how add the comment can delete it
    # urls : api/posts/{post_id}/comments/{comment_id} 
    @action(detail=True, methods=['delete'], url_path='delete-comment')
    def delete_comment(self, request, pk=None, comment_id=None):
        comment_id = request.query_params.get('comment_id')
        if not comment_id:
            return Response({"error": "comment_id is required"}, status=400)
        try:
            comment = Comment.objects.get(id=comment_id, post__id=pk)
        except Comment.DoesNotExist:
            return Response({"error": "Comment not found"}, status=404)

        if comment.user != request.user:
            return Response({"error": "You are not allowed to delete this comment"}, status=403)

        comment.delete()
        return Response({"status": "Comment deleted"})