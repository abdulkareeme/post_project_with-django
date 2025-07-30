import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Post, Comment , Notification
from django.contrib.auth import get_user_model

User = get_user_model()

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
        else:
            self.user = self.scope["user"]
            self.group_name = f"user_{self.user.id}_notifications"  # تطابق مع api_views
            
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()
            print(f"WebSocket connected for {self.user.username}")

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
        print(f"WebSocket disconnected for {getattr(self, 'user', 'Anonymous')}")

    async def send_notification(self, event):
        try:
            await self.send(text_data=json.dumps({
                'type': event['notification_data']['type'],
                'message': event['notification_data']['message'],
                'postId': event['notification_data'].get('postId'),
                'commentId': event['notification_data'].get('commentId')
            }))
            
            # قم باستدعاء الدالة المتزامنة لحفظ الإشعار
            # تأكد من أن self.user.id متاح هنا
            await self.create_notification_record(
                user_id=self.user.id,
                message=event['notification_data']['message']
            )
            
        except Exception as e:
            print(f"Error sending notification: {e}")

    # دالة مساعدة لحفظ الإشعار في قاعدة البيانات
    @database_sync_to_async
    def create_notification_record(self, user_id, message):
        try:
            user_instance = User.objects.get(id=user_id)
            Notification.objects.create(user=user_instance, message=message)
            print(f"Notification saved to DB for user {user_instance.username}: {message}")
        except User.DoesNotExist:
            print(f"Error: User with ID {user_id} not found when saving notification.")
        except Exception as e:
            print(f"Error saving notification to DB: {e}")