import os
import django

# 1. 환경 변수 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flix_n_chill.settings')

# 2. Django 초기화 명시적으로 먼저 실행
django.setup()

# 3. Django 의존 모듈 import
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from chat.middleware import TokenAuthMiddlewareStack
from chat.routing import websocket_urlpatterns

# 4. ASGI 애플리케이션 정의
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": TokenAuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
