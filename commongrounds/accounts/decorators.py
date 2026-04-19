from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(role):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            try:
                profile = request.user.profile
            except Exception:
                raise PermissionDenied
            if profile.role != role:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
