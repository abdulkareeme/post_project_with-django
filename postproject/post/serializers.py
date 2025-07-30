from rest_framework import serializers
from .models import Post , Comment ,Notification


# for comments
class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    class Meta:
        model = Comment
        fields = ['id', 'user', 'content','post_id' ,'created_at']
        read_only_fields = ['user', 'post', 'created_at']
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['created_at'] = instance.created_at.strftime("%Y-%m-%d")
        return rep

# Get all Posts
class IndexSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    likes  = serializers.StringRelatedField(many=True)
    total_likes = serializers.IntegerField( read_only=True)
    user_has_liked = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)
    class Meta:
        model = Post
        fields = ['id','title', 'content', 'image', 'video', 'author', 'total_likes', 'user_has_liked', 'likes', 'comments', 'created_at']
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['created_at'] = instance.created_at.strftime("%Y-%m-%d")
        return rep
    
    def get_total_like(self, obj):
        return obj.likes.count()
    def get_user_has_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user in obj.likes.all()
        return False

# Create a new post
class CreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id','title', 'content', 'image', 'video']
        def create(self, validated_data):
            request = self.context.get('request')
            user = request.user
            return Post.objects.create(author=user, **validated_data)
        
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'created_at', 'read']