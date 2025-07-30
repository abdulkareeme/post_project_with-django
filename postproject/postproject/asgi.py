import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
import django

# استيراد AuthMiddlewareStack للتعامل مع مصادقة المستخدمين عبر الجلسات (sessions)
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

# قم بتعيين متغير البيئة لملف الإعدادات الخاص بك.
# (استخدم اسم مشروعك هنا، والذي يبدو أنه 'postproject' بناءً على المحادثات السابقة،
# لكن في الكود الذي قدمته كان 'Chat.settings'، سأفترض أنه 'postproject' أو الاسم الصحيح)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'postproject.settings')

# يجب استدعاء django.setup() بعد تعيين DJANGO_SETTINGS_MODULE
# وقبل أي استيرادات لـ Django (مثل نماذجك أو تطبيقاتك)
django.setup()

# استيراد أنماط الـ WebSocket من تطبيقاتك
# تأكد من أن أسماء التطبيقات ومسارات ملفات routing.py صحيحة.
# سأفترض هنا أن لديك تطبيقين: 'post' و 'auth_user' بناءً على محادثاتنا السابقة،
# وأن ملفات الـ routing الخاصة بهما هي 'post.routing' و 'auth_user.routing'.
# إذا كانت أسماء تطبيقاتك أو مساراتها مختلفة، قم بتعديلها هنا.
from post.routing import websocket_urlpatterns as post_websocket_urlpatterns


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        # استخدام AuthMiddlewareStack لمصادقة المستخدمين عبر جلسات Django القياسية
        AuthMiddlewareStack(
            URLRouter(
                # دمج جميع أنماط الـ WebSocket من تطبيقاتك
                post_websocket_urlpatterns
            )
        )
    ),
})