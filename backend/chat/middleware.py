from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser

@database_sync_to_async
def get_user_from_token(token_key):
    try:
        token = Token.objects.get(key=token_key)
        return token.user
    except Token.DoesNotExist:
        return AnonymousUser()

class TokenAuthMiddleware(BaseMiddleware):
    """
    Custom middleware for token authentication in WebSocket connections.
    This middleware extracts the token from the query string and authenticates the user.
    """
    async def __call__(self, scope, receive, send):
        # Get query string from scope
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        
        # Extract token from query params
        token_key = query_params.get('token', [None])[0]
        
        if token_key:
            # Get user from token
            scope['user'] = await get_user_from_token(token_key)
        
        # If no token or invalid token, check if user is already authenticated via session
        if not scope.get('user') or not scope['user'].is_authenticated:
            # Keep the existing session authentication if available
            pass
        
        return await super().__call__(scope, receive, send)

def TokenAuthMiddlewareStack(inner):
    """
    Combines TokenAuthMiddleware with AuthMiddlewareStack for both token and session authentication.
    """
    from channels.auth import AuthMiddlewareStack
    return TokenAuthMiddleware(AuthMiddlewareStack(inner))