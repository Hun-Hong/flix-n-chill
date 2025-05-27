from functools import wraps
from rest_framework.authtoken.models import Token
from django.http import JsonResponse
from django.shortcuts import redirect
from django.conf import settings

def token_required(view_func):
    """
    Custom decorator to check token authentication for chat views.
    This replaces Django's @login_required which uses session authentication.
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        # Check for token in Authorization header
        auth_header = request.headers.get('Authorization', '')
        
        if auth_header.startswith('Token '):
            token_key = auth_header.split(' ')[1]
            try:
                token = Token.objects.get(key=token_key)
                request.user = token.user
                return view_func(request, *args, **kwargs)
            except Token.DoesNotExist:
                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return JsonResponse({'error': 'Invalid token'}, status=401)
                return redirect(settings.LOGIN_URL)
        
        # If no token found, check if user is authenticated via session (for backward compatibility)
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
            
        # If no authentication found, return error or redirect
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({'error': 'Authentication required'}, status=401)
        return redirect(settings.LOGIN_URL)
        
    return wrapped_view