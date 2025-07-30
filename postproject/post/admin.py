from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Post , Comment , Notification

# Register your models here.
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id','title', 'author', 'total_likes') 

    def total_likes(self, obj):
        return obj.likes.count()
    
    total_likes.short_description = 'Total Likes'  

# register for comment
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id' , 'content' ,'user' , 'post_id' , 'post')

# register for comment
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id' , 'user' , 'message' , 'read')
