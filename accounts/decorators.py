from functools import wraps
from django.http import Http404
from django.shortcuts import redirect

def hr_or_admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.employee_set.first().designation in ['H', 'A']:
                return view_func(request, *args, **kwargs)
            else:
                return redirect('/') 
        return redirect('/users/login')
    return _wrapped_view
