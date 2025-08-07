from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect


def redirect_authenticated_user(view_func):
    """
    Decorator to redirect authenticated users to the home page.
    """
    def _wrapped_view(request: HttpRequest, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view